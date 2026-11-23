import os
import asyncio
import httpx
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from datetime import datetime
import uuid

from app.alerts.db import engine, Base, get_db
from app.alerts.models import Subscription, Alert
from app.core.auth import get_actor_id

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Microservicio de Alertas", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

INTERNAL_API_URL = os.getenv("INTERNAL_API_URL", "http://app:8000/api/reportes")
INTERNAL_API_TOKEN = os.getenv("INTERNAL_API_TOKEN", "secret-token")

class SubscriptionCreate(BaseModel):
    municipality: str

class SubscriptionResponse(BaseModel):
    id: uuid.UUID
    municipality: str
    created_at: datetime
    class Config:
        from_attributes = True

class AlertResponse(BaseModel):
    id: uuid.UUID
    event_id: uuid.UUID
    message: str
    municipality: str
    created_at: datetime
    class Config:
        from_attributes = True

async def alert_worker():
    await asyncio.sleep(5)
    while True:
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                headers = {"X-Internal-Token": INTERNAL_API_TOKEN}
                response = await client.get(f"{INTERNAL_API_URL}/internal/events?limit=50", headers=headers)
                
                if response.status_code == 200:
                    events = response.json()
                    db = next(get_db())
                    try:
                        for event in events:
                            event_id = event.get("id")
                            municipality = event.get("municipality")
                            event_created_at = datetime.fromisoformat(event.get("created_at"))
                            message = event.get("message", f"Nuevo reporte en {municipality}")
                            
                            subs = db.query(Subscription).filter(
                                Subscription.municipality == municipality,
                                Subscription.created_at <= event_created_at
                            ).all()
                            
                            for sub in subs:
                                exists = db.query(Alert).filter_by(
                                    event_id=event_id, 
                                    recipient_id=sub.recipient_id
                                ).first()
                                
                                if not exists:
                                    new_alert = Alert(
                                        event_id=event_id,
                                        recipient_id=sub.recipient_id,
                                        message=message,
                                        municipality=municipality
                                    )
                                    db.add(new_alert)
                            
                            db.commit()
                            
                            ack_resp = await client.post(
                                f"{INTERNAL_API_URL}/internal/events/{event_id}/ack",
                                headers=headers
                            )
                    except Exception as e:
                        db.rollback()
                        print(f"Error procesando eventos en worker: {e}")
                    finally:
                        db.close()
        except Exception as err:
            print(f"Error de conexión en worker de alertas: {err}")
        
        await asyncio.sleep(10)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(alert_worker())

@app.post("/api/alertas/subscriptions", response_model=SubscriptionResponse, status_code=status.HTTP_201_CREATED)
def create_subscription(sub_in: SubscriptionCreate, db: Session = Depends(get_db), actor_id: uuid.UUID = Depends(get_actor_id)):
    existing = db.query(Subscription).filter_by(recipient_id=actor_id, municipality=sub_in.municipality).first()
    if existing:
        return existing
    
    new_sub = Subscription(recipient_id=actor_id, municipality=sub_in.municipality)
    db.add(new_sub)
    db.commit()
    db.refresh(new_sub)
    return new_sub

@app.get("/api/alertas/subscriptions", response_model=List[SubscriptionResponse])
def list_subscriptions(db: Session = Depends(get_db), actor_id: uuid.UUID = Depends(get_actor_id)):
    return db.query(Subscription).filter_by(recipient_id=actor_id).all()

@app.delete("/api/alertas/subscriptions/{sub_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subscription(sub_id: uuid.UUID, db: Session = Depends(get_db), actor_id: uuid.UUID = Depends(get_actor_id)):
    sub = db.query(Subscription).filter_by(id=sub_id, recipient_id=actor_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Suscripción no encontrada")
    db.delete(sub)
    db.commit()
    return None

@app.get("/api/alertas/inbox", response_model=List[AlertResponse])
def get_inbox(db: Session = Depends(get_db), actor_id: uuid.UUID = Depends(get_actor_id)):
    return db.query(Alert).filter_by(recipient_id=actor_id).order_by(Alert.created_at.desc()).all()

@app.get("/health/ready")
def health_ready(db: Session = Depends(get_db)):
    try:
        db.execute("SELECT 1")
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
