from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional
import json
import logging
import os
from datetime import datetime

from models.database import get_db, User, Conversation, Relationship
from services.ai_service import AIService
from services.email_service import email_service
from fastapi import BackgroundTasks
from sqlalchemy.orm import Session

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Personal AI Assistant",
    description="AI-powered assistant for conversation analysis and personalized suggestions",
    version="1.0.0"
)

# Configure CORS for development and production
allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "file://"
]

# Add production origins from environment
env_origins = os.getenv("ALLOWED_ORIGINS", "")
if env_origins:
    additional_origins = [origin.strip() for origin in env_origins.split(",")]
    allowed_origins.extend(additional_origins)

# In production, allow Railway and custom domains
environment = os.getenv("ENVIRONMENT", "development")
if environment == "production":
    allowed_origins.extend([
        "https://*.railway.app",
        "https://*.vercel.app",
        "https://*.netlify.app"
    ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ai_service = AIService()

class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    personality_traits: Optional[str] = None

class ConversationAnalyze(BaseModel):
    conversation_text: str = Field(..., min_length=1)
    context: Optional[str] = None
    relationship_type: str = Field(..., pattern=r'^(romantic|family|friend|professional)$')

class ResponseSuggestion(BaseModel):
    message: str = Field(..., min_length=1)
    tone: str = Field(..., pattern=r'^(formal|casual|empathetic|assertive)$')
    context: Optional[str] = None

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

@app.get("/")
async def root():
    return {"message": "Personal AI Assistant API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    # Return a simple JSON-friendly health response
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.post("/users", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: Session = Depends(get_db), background_tasks: BackgroundTasks = None):
    try:
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="User with this email already exists"
            )

        db_user = User(
            name=user.name,
            email=user.email,
            personality_traits=user.personality_traits
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        logger.info(f"User created: {user.email}")
        # prepare email content
        subject = "Seu material: Análise completa + guia de comunicação"
        body = f"Olá {user.name},\n\nObrigado por se inscrever! Em anexo (link) está sua análise completa e o guia prático de comunicação.\n\nAbraços,\nEquipe Personal AI"

        # schedule email in background (best-effort). Use db_user.email for the saved record
        try:
            # prepare template context
            materials_link = os.getenv("MATERIALS_LINK", "https://example.com/welcome-materials")
            context = {"name": db_user.name, "materials_link": materials_link}

            if background_tasks is not None:
                background_tasks.add_task(email_service.send_templated_email, db_user.email, subject, "welcome", context)
            else:
                email_service.send_templated_email(db_user.email, subject, "welcome", context)
        except Exception:
            logger.exception("Failed to enqueue/send welcome email")

        return {
            "id": db_user.id,
            "name": db_user.name,
            "email": db_user.email,
            "created_at": db_user.created_at
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create user")

@app.get("/users/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "personality_traits": user.personality_traits,
            "created_at": user.created_at
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch user")

@app.post("/analyze/conversation")
async def analyze_conversation(
    analysis: ConversationAnalyze,
    user_id: int,
    db: Session = Depends(get_db)
):
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        personality_analysis = await ai_service.analyze_personality(
            analysis.conversation_text,
            user.personality_traits
        )

        conversation = Conversation(
            user_id=user_id,
            content=analysis.conversation_text,
            context=analysis.context,
            relationship_type=analysis.relationship_type,
            analysis_result=json.dumps(personality_analysis) if isinstance(personality_analysis, dict) else personality_analysis
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

        logger.info(f"Conversation analyzed for user {user_id}")
        return {
            "conversation_id": conversation.id,
            "analysis": personality_analysis,
            "relationship_type": analysis.relationship_type,
            "analyzed_at": conversation.created_at
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing conversation: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to analyze conversation")

@app.post("/suggestions/response")
async def generate_response_suggestions(
    suggestion: ResponseSuggestion,
    user_id: int,
    db: Session = Depends(get_db)
):
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        suggestions = await ai_service.generate_response_suggestions(
            suggestion.message,
            suggestion.tone,
            user.personality_traits,
            suggestion.context
        )

        logger.info(f"Response suggestions generated for user {user_id}")
        return {
            "original_message": suggestion.message,
            "tone": suggestion.tone,
            "suggestions": suggestions,
            "generated_at": datetime.utcnow()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating suggestions: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate suggestions")

@app.get("/users/{user_id}/conversations")
async def get_user_conversations(
    user_id: int,
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        conversations = db.query(Conversation)\
            .filter(Conversation.user_id == user_id)\
            .offset(offset)\
            .limit(limit)\
            .all()

        return {
            "conversations": [
                {
                    "id": conv.id,
                    "relationship_type": conv.relationship_type,
                    "context": conv.context,
                    "analysis_result": conv.analysis_result,
                    "created_at": conv.created_at
                }
                for conv in conversations
            ],
            "total": len(conversations)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching conversations for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch conversations")

@app.get("/users/{user_id}/relationships")
async def get_user_relationships(user_id: int, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        relationships = db.query(Relationship)\
            .filter(Relationship.user_id == user_id)\
            .all()

        return {
            "relationships": [
                {
                    "id": rel.id,
                    "name": rel.name,
                    "relationship_type": rel.relationship_type,
                    "notes": rel.notes,
                    "created_at": rel.created_at
                }
                for rel in relationships
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching relationships for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch relationships")


class MaterialsRequest(BaseModel):
    user_id: int
    materials_link: Optional[str] = None


@app.post("/materials/send")
async def send_materials(request: MaterialsRequest, db: Session = Depends(get_db), background_tasks: BackgroundTasks = None):
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    subject = "Seu material: Análise completa + guia de comunicação"
    materials_link = request.materials_link or os.getenv("MATERIALS_LINK", "https://example.com/welcome-materials")
    context = {"name": user.name, "materials_link": materials_link}

    try:
        if background_tasks is not None:
            background_tasks.add_task(email_service.send_templated_email, user.email, subject, "welcome", context)
        else:
            email_service.send_templated_email(user.email, subject, "welcome", context)

        return {"status": "queued"}
    except Exception as e:
        logger.exception("Failed to send materials email")
        raise HTTPException(status_code=500, detail="Failed to send materials")

if __name__ == "__main__":
    import uvicorn

    # Use PORT from environment (platforms like Railway provide a dynamic port)
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "false").lower() in ("1", "true", "yes")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        reload=debug,
        log_level="info"
    )