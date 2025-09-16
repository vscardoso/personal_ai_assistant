import openai
import os
import json
import logging
from typing import List, Dict, Optional
from datetime import datetime
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            self.client = openai.AsyncOpenAI(api_key=api_key)
        else:
            self.client = None
            logger.warning("OpenAI API key not found. AI features will be disabled.")
        self.model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "1000"))
        self.temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def _make_api_call(self, messages: List[Dict], max_tokens: int = None):
        if not self.client:
            raise Exception("OpenAI client not initialized. Please set OPENAI_API_KEY environment variable.")

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens or self.max_tokens,
                temperature=self.temperature
            )
            return response.choices[0].message.content
        except openai.RateLimitError as e:
            logger.warning(f"Rate limit exceeded: {e}")
            raise
        except openai.APIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in API call: {e}")
            raise

    async def analyze_personality(self, conversation_text: str, existing_traits: Optional[str] = None) -> Dict:
        try:
            system_prompt = """You are an expert psychologist specializing in personality analysis through communication patterns.
            Analyze the given conversation and provide insights about the person's communication style, emotional patterns, and personality traits.

            Return your analysis as a JSON object with the following structure:
            {
                "communication_style": "description of how they communicate",
                "emotional_patterns": "observed emotional tendencies",
                "personality_traits": ["trait1", "trait2", "trait3"],
                "strengths": ["strength1", "strength2"],
                "areas_for_growth": ["area1", "area2"],
                "relationship_tendencies": "how they tend to interact in relationships",
                "confidence_score": 0.8
            }
            """

            user_prompt = f"""Analyze this conversation for personality insights:

{conversation_text}

{f"Previous personality analysis: {existing_traits}" if existing_traits else ""}

Focus on communication patterns, emotional intelligence, conflict resolution style, and interpersonal dynamics."""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]

            response = await self._make_api_call(messages)

            try:
                analysis = json.loads(response)
                analysis["analyzed_at"] = datetime.utcnow().isoformat()
                return analysis
            except json.JSONDecodeError:
                logger.warning("AI response was not valid JSON, using fallback structure")
                return {
                    "communication_style": "Analysis unavailable",
                    "emotional_patterns": "Analysis unavailable",
                    "personality_traits": ["analytical"],
                    "strengths": ["communicative"],
                    "areas_for_growth": ["self-reflection"],
                    "relationship_tendencies": "Analysis unavailable",
                    "confidence_score": 0.3,
                    "analyzed_at": datetime.utcnow().isoformat(),
                    "raw_response": response
                }

        except Exception as e:
            logger.error(f"Error in personality analysis: {e}")
            return {
                "error": "Analysis failed",
                "communication_style": "Unable to analyze",
                "emotional_patterns": "Unable to analyze",
                "personality_traits": ["unknown"],
                "strengths": ["resilient"],
                "areas_for_growth": ["communication"],
                "relationship_tendencies": "Unable to analyze",
                "confidence_score": 0.0,
                "analyzed_at": datetime.utcnow().isoformat()
            }

    async def generate_response_suggestions(
        self,
        message: str,
        tone: str,
        personality_traits: Optional[str] = None,
        context: Optional[str] = None
    ) -> List[Dict]:
        try:
            system_prompt = f"""You are an expert communication coach. Generate 3 different response suggestions for the given message.
            Each response should match the requested tone: {tone}

            Consider the person's personality traits when crafting responses that feel authentic to them.

            Return your suggestions as a JSON array with this structure:
            [
                {{
                    "response": "suggested response text",
                    "explanation": "why this response works well",
                    "tone_match": "how well it matches the requested tone (1-10)",
                    "authenticity": "how authentic it feels (1-10)"
                }}
            ]
            """

            user_prompt = f"""Generate response suggestions for this message: "{message}"

Requested tone: {tone}
{f"Personality context: {personality_traits}" if personality_traits else ""}
{f"Situation context: {context}" if context else ""}

Create responses that are:
1. Appropriate for the tone
2. Authentic to the person's communication style
3. Effective for the relationship context
4. Emotionally intelligent"""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]

            response = await self._make_api_call(messages, max_tokens=1200)

            try:
                suggestions = json.loads(response)
                if not isinstance(suggestions, list):
                    suggestions = [suggestions]

                for suggestion in suggestions:
                    suggestion["generated_at"] = datetime.utcnow().isoformat()

                return suggestions[:3]

            except json.JSONDecodeError:
                logger.warning("AI response was not valid JSON, creating fallback suggestions")
                return [
                    {
                        "response": response[:200] + "..." if len(response) > 200 else response,
                        "explanation": "AI-generated response (parsing error occurred)",
                        "tone_match": 7,
                        "authenticity": 6,
                        "generated_at": datetime.utcnow().isoformat()
                    }
                ]

        except Exception as e:
            logger.error(f"Error generating response suggestions: {e}")
            return [
                {
                    "response": f"I understand you want to respond with a {tone} tone. Let me think about this...",
                    "explanation": "Fallback response due to service error",
                    "tone_match": 5,
                    "authenticity": 5,
                    "generated_at": datetime.utcnow().isoformat(),
                    "error": str(e)
                }
            ]

    async def analyze_relationship_dynamics(
        self,
        conversation_history: List[str],
        relationship_type: str,
        participants: List[str]
    ) -> Dict:
        try:
            system_prompt = """You are a relationship counselor analyzing communication dynamics between people.
            Analyze the conversation patterns and provide insights about the relationship health and dynamics.

            Return analysis as JSON:
            {
                "overall_health": "excellent/good/concerning/poor",
                "communication_patterns": ["pattern1", "pattern2"],
                "power_dynamics": "description of power balance",
                "conflict_resolution": "how conflicts are handled",
                "emotional_support": "level of mutual support",
                "recommendations": ["suggestion1", "suggestion2"],
                "red_flags": ["flag1", "flag2"] or [],
                "strengths": ["strength1", "strength2"]
            }
            """

            conversations = "\n\n".join([f"Message {i+1}: {conv}" for i, conv in enumerate(conversation_history)])

            user_prompt = f"""Analyze this {relationship_type} relationship based on these conversations:

{conversations}

Participants: {', '.join(participants)}

Focus on communication patterns, emotional dynamics, respect levels, and overall relationship health."""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]

            response = await self._make_api_call(messages, max_tokens=1200)

            try:
                analysis = json.loads(response)
                analysis["analyzed_at"] = datetime.utcnow().isoformat()
                analysis["relationship_type"] = relationship_type
                return analysis
            except json.JSONDecodeError:
                return {
                    "overall_health": "unknown",
                    "communication_patterns": ["Unable to analyze"],
                    "power_dynamics": "Analysis unavailable",
                    "conflict_resolution": "Analysis unavailable",
                    "emotional_support": "Analysis unavailable",
                    "recommendations": ["Consider professional counseling"],
                    "red_flags": [],
                    "strengths": ["Ongoing communication"],
                    "analyzed_at": datetime.utcnow().isoformat(),
                    "relationship_type": relationship_type,
                    "raw_response": response
                }

        except Exception as e:
            logger.error(f"Error analyzing relationship dynamics: {e}")
            return {
                "error": "Analysis failed",
                "overall_health": "unknown",
                "communication_patterns": ["Analysis error"],
                "power_dynamics": "Unable to determine",
                "conflict_resolution": "Unable to assess",
                "emotional_support": "Unable to assess",
                "recommendations": ["Retry analysis later"],
                "red_flags": [],
                "strengths": [],
                "analyzed_at": datetime.utcnow().isoformat(),
                "relationship_type": relationship_type
            }

    async def get_conversation_insights(self, conversation_text: str) -> Dict:
        try:
            system_prompt = """Extract key insights from this conversation. Focus on:
            - Main topics discussed
            - Emotional tone throughout
            - Decision points or action items
            - Unresolved issues
            - Communication effectiveness

            Return as JSON:
            {
                "main_topics": ["topic1", "topic2"],
                "emotional_tone": "overall emotional climate",
                "key_moments": ["moment1", "moment2"],
                "action_items": ["action1", "action2"],
                "unresolved_issues": ["issue1", "issue2"],
                "communication_score": 8,
                "summary": "brief summary of the conversation"
            }
            """

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Analyze this conversation:\n\n{conversation_text}"}
            ]

            response = await self._make_api_call(messages)

            try:
                insights = json.loads(response)
                insights["analyzed_at"] = datetime.utcnow().isoformat()
                return insights
            except json.JSONDecodeError:
                return {
                    "main_topics": ["General conversation"],
                    "emotional_tone": "Mixed",
                    "key_moments": ["Conversation occurred"],
                    "action_items": [],
                    "unresolved_issues": [],
                    "communication_score": 5,
                    "summary": "Analysis unavailable due to parsing error",
                    "analyzed_at": datetime.utcnow().isoformat(),
                    "raw_response": response
                }

        except Exception as e:
            logger.error(f"Error getting conversation insights: {e}")
            return {
                "error": "Insight extraction failed",
                "main_topics": ["Unknown"],
                "emotional_tone": "Unable to determine",
                "key_moments": [],
                "action_items": [],
                "unresolved_issues": [],
                "communication_score": 0,
                "summary": "Analysis failed",
                "analyzed_at": datetime.utcnow().isoformat()
            }