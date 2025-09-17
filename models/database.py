from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, ForeignKey, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.sql import func
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./personal_assistant.db")

# Configure engine based on database type
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False  # Set to True for SQL debugging
    )
elif DATABASE_URL.startswith("postgresql"):
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        echo=False  # Set to True for SQL debugging
    )
else:
    # Generic configuration for other databases
    engine = create_engine(DATABASE_URL, echo=False)

logger.info(f"Database engine configured for: {DATABASE_URL.split('://')[0]}")

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

# =============================================================================
# SALES ASSISTANT MODELS
# =============================================================================

class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="active")  # active, paused, completed
    total_prospects = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User")
    prospects = relationship("Prospect", back_populates="campaign", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Campaign(id={self.id}, name='{self.name}', prospects={self.total_prospects})>"

class Prospect(Base):
    __tablename__ = "prospects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    company = Column(String(200), nullable=True)
    email = Column(String(255), nullable=False, index=True)
    title = Column(String(150), nullable=True)
    linkedin_url = Column(String(500), nullable=True)
    research_data = Column(JSON, nullable=True)  # JSON field for flexible research data
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    status = Column(String(50), default="new")  # new, contacted, replied, closed, unqualified
    score = Column(Integer, default=0)  # Lead scoring 0-100
    tags = Column(String(500), nullable=True)  # Comma-separated tags
    notes = Column(Text, nullable=True)
    last_contact = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    campaign = relationship("Campaign", back_populates="prospects")
    email_sequences = relationship("EmailSequence", back_populates="prospect", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Prospect(id={self.id}, name='{self.name}', company='{self.company}', status='{self.status}')>"

class EmailSequence(Base):
    __tablename__ = "email_sequences"

    id = Column(Integer, primary_key=True, index=True)
    prospect_id = Column(Integer, ForeignKey("prospects.id"), nullable=False)
    step = Column(Integer, nullable=False)  # Sequence step number (1, 2, 3, etc.)
    subject = Column(String(500), nullable=False)
    body = Column(Text, nullable=False)
    template_name = Column(String(100), nullable=True)  # Reference to email template
    sent_at = Column(DateTime(timezone=True), nullable=True)
    opened_at = Column(DateTime(timezone=True), nullable=True)
    clicked_at = Column(DateTime(timezone=True), nullable=True)
    replied_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(50), default="pending")  # pending, sent, delivered, opened, clicked, replied, bounced
    scheduled_for = Column(DateTime(timezone=True), nullable=True)  # When to send
    error_message = Column(Text, nullable=True)  # If sending failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    prospect = relationship("Prospect", back_populates="email_sequences")

    def __repr__(self):
        return f"<EmailSequence(id={self.id}, prospect_id={self.prospect_id}, step={self.step}, status='{self.status}')>"

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

# =============================================================================
# SALES ASSISTANT HELPER FUNCTIONS
# =============================================================================

def create_campaign(db: Session, user_id: int, name: str, description: str = None):
    """Create a new sales campaign."""
    campaign = Campaign(
        user_id=user_id,
        name=name,
        description=description
    )
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    return campaign

def get_user_campaigns(db: Session, user_id: int):
    """Get all campaigns for a user."""
    return db.query(Campaign)\
        .filter(Campaign.user_id == user_id)\
        .order_by(Campaign.created_at.desc())\
        .all()

def create_prospect(db: Session, campaign_id: int, name: str, email: str,
                   company: str = None, title: str = None, linkedin_url: str = None,
                   research_data: dict = None):
    """Create a new prospect."""
    prospect = Prospect(
        campaign_id=campaign_id,
        name=name,
        email=email,
        company=company,
        title=title,
        linkedin_url=linkedin_url,
        research_data=research_data
    )
    db.add(prospect)

    # Update campaign prospect count
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if campaign:
        campaign.total_prospects += 1

    db.commit()
    db.refresh(prospect)
    return prospect

def get_campaign_prospects(db: Session, campaign_id: int):
    """Get all prospects for a campaign."""
    return db.query(Prospect)\
        .filter(Prospect.campaign_id == campaign_id)\
        .order_by(Prospect.created_at.desc())\
        .all()

def create_email_sequence(db: Session, prospect_id: int, step: int, subject: str,
                         body: str, template_name: str = None, scheduled_for = None):
    """Create a new email in sequence."""
    email = EmailSequence(
        prospect_id=prospect_id,
        step=step,
        subject=subject,
        body=body,
        template_name=template_name,
        scheduled_for=scheduled_for
    )
    db.add(email)
    db.commit()
    db.refresh(email)
    return email

def get_prospect_emails(db: Session, prospect_id: int):
    """Get all emails for a prospect."""
    return db.query(EmailSequence)\
        .filter(EmailSequence.prospect_id == prospect_id)\
        .order_by(EmailSequence.step.asc())\
        .all()

def update_email_status(db: Session, email_id: int, status: str,
                       sent_at = None, opened_at = None, clicked_at = None, replied_at = None):
    """Update email sequence status and timestamps."""
    email = db.query(EmailSequence).filter(EmailSequence.id == email_id).first()
    if email:
        email.status = status
        if sent_at:
            email.sent_at = sent_at
        if opened_at:
            email.opened_at = opened_at
        if clicked_at:
            email.clicked_at = clicked_at
        if replied_at:
            email.replied_at = replied_at
        db.commit()
        db.refresh(email)
    return email

def update_prospect_status(db: Session, prospect_id: int, status: str, notes: str = None):
    """Update prospect status and notes."""
    prospect = db.query(Prospect).filter(Prospect.id == prospect_id).first()
    if prospect:
        prospect.status = status
        prospect.last_contact = func.now()
        if notes:
            prospect.notes = notes
        db.commit()
        db.refresh(prospect)
    return prospect

def get_pending_emails(db: Session, limit: int = 50):
    """Get emails scheduled to be sent."""
    from datetime import datetime
    return db.query(EmailSequence)\
        .filter(EmailSequence.status == "pending")\
        .filter(EmailSequence.scheduled_for <= datetime.utcnow())\
        .limit(limit)\
        .all()

if __name__ == "__main__":
    create_tables()
    print("Database tables created successfully")