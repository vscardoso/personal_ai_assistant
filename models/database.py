from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.sql import func
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./personal_assistant.db")

if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    personality_traits = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    relationships = relationship("Relationship", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}', email='{self.email}')>"

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    context = Column(Text, nullable=True)
    relationship_type = Column(String(50), nullable=False)
    analysis_result = Column(Text, nullable=True)
    confidence_score = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Conversation(id={self.id}, user_id={self.user_id}, type='{self.relationship_type}')>"

class Relationship(Base):
    __tablename__ = "relationships"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    relationship_type = Column(String(50), nullable=False)
    notes = Column(Text, nullable=True)
    communication_style = Column(String(100), nullable=True)
    preferences = Column(Text, nullable=True)
    last_interaction = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="relationships")
    messages = relationship("Message", back_populates="relationship")

    def __repr__(self):
        return f"<Relationship(id={self.id}, name='{self.name}', type='{self.relationship_type}')>"

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    relationship_id = Column(Integer, ForeignKey("relationships.id"), nullable=True)
    sender = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    message_type = Column(String(50), default="text")
    sentiment_score = Column(Float, nullable=True)
    emotion_tags = Column(String(255), nullable=True)
    ai_suggestions = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    conversation = relationship("Conversation", back_populates="messages")
    relationship = relationship("Relationship", back_populates="messages")

    def __repr__(self):
        return f"<Message(id={self.id}, sender='{self.sender}', type='{self.message_type}')>"

class PersonalityInsight(Base):
    __tablename__ = "personality_insights"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    insight_type = Column(String(100), nullable=False)
    insight_data = Column(Text, nullable=False)
    confidence_level = Column(Float, default=0.0)
    source_conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Integer, default=1)

    def __repr__(self):
        return f"<PersonalityInsight(id={self.id}, user_id={self.user_id}, type='{self.insight_type}')>"

class ResponseSuggestion(Base):
    __tablename__ = "response_suggestions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    original_message = Column(Text, nullable=False)
    suggested_response = Column(Text, nullable=False)
    tone = Column(String(50), nullable=False)
    context = Column(Text, nullable=True)
    confidence_score = Column(Float, default=0.0)
    was_used = Column(Integer, default=0)
    feedback_rating = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<ResponseSuggestion(id={self.id}, user_id={self.user_id}, tone='{self.tone}')>"

class ConversationAnalysis(Base):
    __tablename__ = "conversation_analyses"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    analysis_type = Column(String(100), nullable=False)
    analysis_data = Column(Text, nullable=False)
    insights = Column(Text, nullable=True)
    recommendations = Column(Text, nullable=True)
    emotional_tone = Column(String(100), nullable=True)
    communication_effectiveness = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<ConversationAnalysis(id={self.id}, type='{self.analysis_type}')>"

def create_tables():
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def create_user(db: Session, name: str, email: str, personality_traits: str = None):
    db_user = User(
        name=name,
        email=email,
        personality_traits=personality_traits
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_conversations(db: Session, user_id: int, limit: int = 10, offset: int = 0):
    return db.query(Conversation)\
        .filter(Conversation.user_id == user_id)\
        .order_by(Conversation.created_at.desc())\
        .offset(offset)\
        .limit(limit)\
        .all()

def create_conversation(db: Session, user_id: int, content: str, context: str = None,
                       relationship_type: str = "general", analysis_result: str = None):
    db_conversation = Conversation(
        user_id=user_id,
        content=content,
        context=context,
        relationship_type=relationship_type,
        analysis_result=analysis_result
    )
    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)
    return db_conversation

def get_user_relationships(db: Session, user_id: int):
    return db.query(Relationship)\
        .filter(Relationship.user_id == user_id)\
        .order_by(Relationship.last_interaction.desc().nullslast(),
                 Relationship.created_at.desc())\
        .all()

def create_relationship(db: Session, user_id: int, name: str, relationship_type: str,
                       notes: str = None, communication_style: str = None):
    db_relationship = Relationship(
        user_id=user_id,
        name=name,
        relationship_type=relationship_type,
        notes=notes,
        communication_style=communication_style
    )
    db.add(db_relationship)
    db.commit()
    db.refresh(db_relationship)
    return db_relationship

def save_response_suggestion(db: Session, user_id: int, original_message: str,
                           suggested_response: str, tone: str, context: str = None,
                           confidence_score: float = 0.0):
    suggestion = ResponseSuggestion(
        user_id=user_id,
        original_message=original_message,
        suggested_response=suggested_response,
        tone=tone,
        context=context,
        confidence_score=confidence_score
    )
    db.add(suggestion)
    db.commit()
    db.refresh(suggestion)
    return suggestion

def save_personality_insight(db: Session, user_id: int, insight_type: str,
                           insight_data: str, confidence_level: float = 0.0,
                           source_conversation_id: int = None):
    insight = PersonalityInsight(
        user_id=user_id,
        insight_type=insight_type,
        insight_data=insight_data,
        confidence_level=confidence_level,
        source_conversation_id=source_conversation_id
    )
    db.add(insight)
    db.commit()
    db.refresh(insight)
    return insight

if __name__ == "__main__":
    create_tables()
    print("Database tables created successfully")