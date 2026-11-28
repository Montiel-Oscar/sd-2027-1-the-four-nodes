"""Mensajes privados entre quien publicó un reporte y quien quiere ayudar."""

from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.reports.models import FoundPetReport, MissingPetReport, ReportConversation, ReportMessage
from app.reports.schemas import ConversationPublic, MessagePublic


def _report(session: Session, kind: str, report_id: UUID):
    model = {"extravios": MissingPetReport, "hallazgos": FoundPetReport}.get(kind)
    report = session.get(model, report_id) if model else None
    if report is None:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")
    return report


def _conversation(session: Session, conversation_id: UUID, actor_id: UUID) -> ReportConversation:
    conversation = session.get(ReportConversation, conversation_id)
    if conversation is None or actor_id not in (conversation.owner_id, conversation.participant_id):
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
    return conversation


def _message_public(message: ReportMessage, actor_id: UUID) -> MessagePublic:
    return MessagePublic(
        id=message.id, body=message.body,
        sender_is_me=message.sender_id == actor_id, created_at=message.created_at,
    )


def _conversation_public(session: Session, conversation: ReportConversation, actor_id: UUID) -> ConversationPublic:
    report = _report(session, conversation.report_kind, conversation.report_id)
    latest = session.scalar(
        select(ReportMessage.created_at)
        .where(ReportMessage.conversation_id == conversation.id)
        .order_by(ReportMessage.created_at.desc(), ReportMessage.id.desc())
        .limit(1)
    )
    return ConversationPublic(
        id=conversation.id, report_kind=conversation.report_kind,
        report_id=conversation.report_id,
        report_title=report.pet_name if conversation.report_kind == "extravios" else report.description,
        role="responsable" if actor_id == conversation.owner_id else "persona que ayuda",
        last_message_at=latest or conversation.created_at,
    )


def start_conversation(session: Session, kind: str, report_id: UUID, actor_id: UUID, body: str) -> ConversationPublic:
    report = _report(session, kind, report_id)
    if actor_id == report.owner_id:
        raise HTTPException(status_code=403, detail="No puedes escribirte a ti mismo")
    criteria = (
        ReportConversation.report_kind == kind,
        ReportConversation.report_id == report_id,
        ReportConversation.participant_id == actor_id,
    )
    conversation = session.scalar(select(ReportConversation).where(*criteria))
    if conversation is None:
        conversation = ReportConversation(
            report_kind=kind, report_id=report_id,
            owner_id=report.owner_id, participant_id=actor_id,
        )
        session.add(conversation)
        try:
            session.flush()
        except IntegrityError:
            session.rollback()
            conversation = session.scalar(select(ReportConversation).where(*criteria))
            if conversation is None:
                raise
    session.add(ReportMessage(conversation_id=conversation.id, sender_id=actor_id, body=body))
    session.commit()
    return _conversation_public(session, conversation, actor_id)


def list_conversations(session: Session, actor_id: UUID) -> list[ConversationPublic]:
    conversations = session.scalars(
        select(ReportConversation)
        .where(or_(ReportConversation.owner_id == actor_id, ReportConversation.participant_id == actor_id))
        .order_by(ReportConversation.created_at.desc())
        .limit(100)
    ).all()
    result = [_conversation_public(session, row, actor_id) for row in conversations]
    return sorted(result, key=lambda row: row.last_message_at, reverse=True)


def list_messages(session: Session, conversation_id: UUID, actor_id: UUID) -> list[MessagePublic]:
    _conversation(session, conversation_id, actor_id)
    messages = session.scalars(
        select(ReportMessage)
        .where(ReportMessage.conversation_id == conversation_id)
        .order_by(ReportMessage.created_at, ReportMessage.id)
        .limit(200)
    ).all()
    return [_message_public(message, actor_id) for message in messages]


def send_message(session: Session, conversation_id: UUID, actor_id: UUID, body: str) -> MessagePublic:
    _conversation(session, conversation_id, actor_id)
    message = ReportMessage(conversation_id=conversation_id, sender_id=actor_id, body=body)
    session.add(message)
    session.commit()
    return _message_public(message, actor_id)
