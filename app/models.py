from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()


class Thread(Base):
    __tablename__ = 'thread'
    id = Column(String, primary_key=True)
    created_at = Column(DateTime, server_default=func.now())
    messages = relationship("Message", back_populates="thread")


class Message(Base):
    __tablename__ = 'message'
    id = Column(String, primary_key=True)
    input = Column(String)
    answer = Column(String)
    thread_id = Column(String, ForeignKey('thread.id'))
    created_at = Column(DateTime, server_default=func.now())
    thread = relationship("Thread", back_populates="messages")
    feedback = relationship("Feedback", back_populates="message")


class Feedback(Base):
    __tablename__ = 'feedback'
    id = Column(String, primary_key=True)
    message_id = Column(String, ForeignKey('message.id'))
    created_at = Column(DateTime, server_default=func.now())
    value = Column(Integer, default=0)
    message = relationship("Message", back_populates="feedback")
