from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional
import json
import logging
import os
from datetime import datetime, date
from sqlalchemy import func

from models.database import get_db, User, Conversation, Relationship, Prospect, Campaign
from services.ai_service import AIService
from services.email_service import email_service
from services.apollo_service import apollo_service
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

class ProspectResearch(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    company: str = Field(..., min_length=1, max_length=200)

class ProspectResearchRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Full name of the person")
    company: str = Field(..., min_length=1, max_length=200, description="Company name")
    linkedin_url: Optional[str] = Field(None, max_length=500, description="LinkedIn profile URL (optional)")

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

@app.post("/api/research/prospect", status_code=status.HTTP_201_CREATED)
async def research_prospect(prospect_data: ProspectResearch, db: Session = Depends(get_db)):
    try:
        # For now, we'll create a default campaign if none exists
        # In production, you might want to require a campaign_id parameter
        default_campaign = db.query(Campaign).filter(Campaign.name == "Default Research").first()
        if not default_campaign:
            default_campaign = Campaign(
                name="Default Research",
                user_id=1,  # You might want to get this from authentication context
                description="Default campaign for prospect research"
            )
            db.add(default_campaign)
            db.commit()
            db.refresh(default_campaign)

        # Check if prospect already exists
        existing_prospect = db.query(Prospect).filter(
            Prospect.name == prospect_data.name,
            Prospect.company == prospect_data.company
        ).first()

        if existing_prospect:
            raise HTTPException(
                status_code=400,
                detail="Prospect with this name and company already exists"
            )

        # Create new prospect with empty basic_info
        new_prospect = Prospect(
            name=prospect_data.name,
            company=prospect_data.company,
            email=f"temp_{prospect_data.name.lower().replace(' ', '_')}@example.com",  # Temporary email
            campaign_id=default_campaign.id,
            research_data={"basic_info": {}}  # Empty basic_info as requested
        )

        db.add(new_prospect)

        # Update campaign prospect count
        default_campaign.total_prospects += 1

        db.commit()
        db.refresh(new_prospect)

        logger.info(f"Prospect research created: {prospect_data.name} at {prospect_data.company}")

        return {
            "id": new_prospect.id,
            "name": new_prospect.name,
            "company": new_prospect.company,
            "basic_info": new_prospect.research_data.get("basic_info", {}),
            "status": new_prospect.status,
            "created_at": new_prospect.created_at
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating prospect research: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create prospect research")

@app.get("/api/analytics/prospects")
async def get_prospects_analytics(db: Session = Depends(get_db)):
    try:
        # Get today's date
        today = date.today()

        # Total prospects researched today
        prospects_today = db.query(Prospect).filter(
            func.date(Prospect.created_at) == today
        ).count()

        # Total prospects ever
        total_prospects = db.query(Prospect).count()

        # Calculate email success rate (prospects with non-temporary emails)
        prospects_with_email = db.query(Prospect).filter(
            Prospect.email.isnot(None),
            ~Prospect.email.like('temp_%@example.com')  # Exclude temporary emails
        ).count()

        email_success_rate = 0.0
        if total_prospects > 0:
            email_success_rate = round((prospects_with_email / total_prospects) * 100, 1)

        # Get latest 10 prospects
        latest_prospects = db.query(Prospect).order_by(
            Prospect.created_at.desc()
        ).limit(10).all()

        # Format prospects for response
        prospects_list = []
        for prospect in latest_prospects:
            # Check if prospect has real email (not temporary)
            has_email = (
                prospect.email and
                not prospect.email.startswith('temp_') and
                '@example.com' not in prospect.email
            )

            prospects_list.append({
                "id": prospect.id,
                "name": prospect.name,
                "company": prospect.company,
                "status": prospect.status,
                "has_email": has_email,
                "email": prospect.email if has_email else None,
                "created_at": prospect.created_at.strftime('%Y-%m-%d %H:%M')
            })

        logger.info(f"Analytics requested: {prospects_today} prospects today, {email_success_rate}% success rate")

        return {
            "prospects_today": prospects_today,
            "total_prospects": total_prospects,
            "email_success_rate": email_success_rate,
            "prospects_with_email": prospects_with_email,
            "latest_prospects": prospects_list,
            "generated_at": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        }

    except Exception as e:
        logger.error(f"Error getting prospects analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get analytics data")

@app.post("/api/research/apollo")
async def research_prospect_apollo(request: ProspectResearchRequest):
    """
    Research a prospect using Apollo.io API

    Returns enriched prospect data including email, LinkedIn, title, and company info
    """
    try:
        # Validate input
        if not request.name.strip() or not request.company.strip():
            raise HTTPException(
                status_code=400,
                detail="Name and company are required and cannot be empty"
            )

        logger.info(f"Starting Apollo research for: {request.name} at {request.company}")

        # Call Apollo.io API
        apollo_result = await apollo_service.search_person_by_name_company(
            request.name,
            request.company
        )

        if apollo_result is None:
            logger.warning(f"No Apollo data found for {request.name} at {request.company}")
            return {
                "success": False,
                "message": "No data found for the specified person and company",
                "data": {
                    "name": request.name,
                    "company": request.company,
                    "linkedin_url": request.linkedin_url,
                    "apollo_data": None,
                    "enriched": False,
                    "error": "No data found in Apollo.io database"
                }
            }

        # Format standardized response
        standardized_data = {
            "name": request.name,
            "company": request.company,
            "linkedin_url": apollo_result.get("linkedin_url") or request.linkedin_url,
            "email": apollo_result.get("email"),
            "title": apollo_result.get("title"),
            "company_info": apollo_result.get("company_info", {}),
            "apollo_data": apollo_result,  # Complete Apollo response
            "enriched": True,
            "data_source": "apollo",
            "researched_at": datetime.utcnow().isoformat()
        }

        logger.info(f"Successfully retrieved Apollo data for {request.name}")

        return {
            "success": True,
            "message": "Prospect data successfully retrieved from Apollo.io",
            "data": standardized_data
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during Apollo research for {request.name}: {str(e)}")

        # Check if it's an Apollo API error
        error_message = str(e).lower()
        if "authentication" in error_message or "api key" in error_message:
            raise HTTPException(
                status_code=500,
                detail="Apollo.io API authentication failed. Please check API key configuration."
            )
        elif "rate limit" in error_message:
            raise HTTPException(
                status_code=500,
                detail="Apollo.io API rate limit exceeded. Please try again later."
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Apollo.io API error: {str(e)}"
            )

@app.get("/api/debug/apollo-status")
async def apollo_debug_status():
    """Debug endpoint to check Apollo.io service status"""
    import os
    api_key = os.getenv("APOLLO_API_KEY")

    return {
        "apollo_api_key_configured": bool(api_key),
        "apollo_api_key_length": len(api_key) if api_key else 0,
        "apollo_api_key_prefix": api_key[:10] if api_key else None,
        "apollo_service_initialized": apollo_service is not None
    }

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