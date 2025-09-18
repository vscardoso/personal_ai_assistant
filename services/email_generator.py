import os
import openai
import logging
from typing import Dict, Optional, Any
import asyncio
from models.database import Prospect

logger = logging.getLogger(__name__)

class EmailGenerator:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

        if self.openai_api_key:
            openai.api_key = self.openai_api_key
        else:
            logger.warning("OPENAI_API_KEY not found in environment variables")

    async def generate_personalized_email(
        self,
        prospect: Prospect,
        email_type: str = "initial_outreach",
        context: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Generate a personalized email for a prospect using OpenAI

        Args:
            prospect: Prospect object from database
            email_type: Type of email ('initial_outreach', 'follow_up', etc.)
            context: Additional context for email generation

        Returns:
            Dict with 'subject' and 'body' keys
        """
        if not self.openai_api_key:
            logger.error("OpenAI API key not configured")
            return self._get_fallback_email(prospect)

        try:
            # Prepare prospect data
            prospect_data = self._extract_prospect_info(prospect)

            # Generate email using OpenAI
            email_content = await self._generate_with_openai(
                prospect_data, email_type, context
            )

            logger.info(f"Generated personalized email for {prospect.name} at {prospect.company}")
            return email_content

        except Exception as e:
            logger.error(f"Error generating personalized email: {e}")
            return self._get_fallback_email(prospect)

    def _extract_prospect_info(self, prospect: Prospect) -> Dict[str, Any]:
        """Extract relevant information from prospect for email generation"""

        # Get research data if available
        research_data = prospect.research_data or {}
        basic_info = research_data.get("basic_info", {})

        return {
            "name": prospect.name,
            "company": prospect.company,
            "title": prospect.title or basic_info.get("title"),
            "linkedin_url": prospect.linkedin_url or basic_info.get("linkedin_url"),
            "company_info": basic_info.get("company", {}),
            "industry": basic_info.get("company", {}).get("industry"),
            "company_size": basic_info.get("company", {}).get("size")
        }

    async def _generate_with_openai(
        self,
        prospect_data: Dict[str, Any],
        email_type: str,
        context: Optional[str]
    ) -> Dict[str, str]:
        """Use OpenAI to generate personalized email"""

        # Create the prompt based on prospect data
        prompt = self._create_email_prompt(prospect_data, email_type, context)

        try:
            # Use asyncio to run the synchronous OpenAI call in a thread
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, self._call_openai_sync, prompt
            )

            return self._parse_openai_response(response)

        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            raise

    def _call_openai_sync(self, prompt: str) -> str:
        """Synchronous OpenAI API call"""

        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": """Você é um especialista em vendas B2B e redação de emails comerciais.
                    Crie emails personalizados, profissionais e envolventes em português brasileiro.

                    IMPORTANTE:
                    - Use tom profissional mas acessível
                    - Seja específico sobre a empresa/pessoa
                    - Inclua uma proposta de valor clara
                    - Mantenha conciso (máximo 150 palavras)
                    - Sempre termine com call-to-action

                    Retorne no formato:
                    ASSUNTO: [assunto do email]

                    CORPO:
                    [corpo do email]"""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=400,
            temperature=0.7
        )

        return response.choices[0].message.content.strip()

    def _create_email_prompt(
        self,
        prospect_data: Dict[str, Any],
        email_type: str,
        context: Optional[str]
    ) -> str:
        """Create prompt for OpenAI based on prospect data"""

        name = prospect_data.get("name", "")
        company = prospect_data.get("company", "")
        title = prospect_data.get("title", "")
        industry = prospect_data.get("industry", "")

        base_prompt = f"""
        Crie um email personalizado para:

        Nome: {name}
        Empresa: {company}
        Cargo: {title or 'Não informado'}
        Setor: {industry or 'Não informado'}
        """

        if email_type == "initial_outreach":
            base_prompt += """

            Tipo: Primeiro contato comercial

            Template base: "Olá {name}, vi que você trabalha na {company}..."

            Objetivo: Apresentar nossa solução de IA para assistência pessoal e agendar uma conversa.

            Inclua:
            - Personalização baseada na empresa/cargo
            - Benefício específico para o setor
            - Call-to-action para agendar reunião
            """

        if context:
            base_prompt += f"\n\nContexto adicional: {context}"

        return base_prompt

    def _parse_openai_response(self, response: str) -> Dict[str, str]:
        """Parse OpenAI response to extract subject and body"""

        try:
            lines = response.strip().split('\n')
            subject_line = ""
            body_lines = []

            current_section = ""

            for line in lines:
                line = line.strip()
                if line.startswith("ASSUNTO:"):
                    subject_line = line.replace("ASSUNTO:", "").strip()
                    current_section = "subject"
                elif line.startswith("CORPO:"):
                    current_section = "body"
                elif current_section == "body" and line:
                    body_lines.append(line)

            # Clean up the results
            subject = subject_line or "Oportunidade de otimizar processos com IA"
            body = "\n".join(body_lines) if body_lines else self._get_default_body()

            return {
                "subject": subject,
                "body": body
            }

        except Exception as e:
            logger.error(f"Error parsing OpenAI response: {e}")
            return {
                "subject": "Oportunidade de parceria - IA para produtividade",
                "body": self._get_default_body()
            }

    def _get_fallback_email(self, prospect: Prospect) -> Dict[str, str]:
        """Generate fallback email when OpenAI is not available"""

        name = prospect.name.split()[0] if prospect.name else "Olá"
        company = prospect.company or "sua empresa"

        subject = f"Oportunidade para {company} - IA para produtividade"

        body = f"""Olá {name},

Vi que você trabalha na {company} e acredito que nossa solução de IA para assistência pessoal pode ser muito valiosa para vocês.

Nossa plataforma ajuda profissionais como você a:
• Analisar conversas e melhorar comunicação
• Gerar respostas personalizadas automaticamente
• Otimizar relacionamentos profissionais

Que tal agendarmos 15 minutos para mostrar como isso pode impactar positivamente o trabalho na {company}?

Atenciosamente,
[Seu nome]"""

        return {
            "subject": subject,
            "body": body
        }

    def _get_default_body(self) -> str:
        """Default email body template"""
        return """Olá,

Espero que esteja bem! Vi seu perfil e acredito que nossa solução de IA para assistência pessoal pode ser muito interessante para você.

Nossa plataforma ajuda profissionais a otimizar comunicação e relacionamentos através de análise inteligente de conversas e sugestões personalizadas.

Gostaria de agendar uma conversa rápida de 15 minutos para mostrar como isso funciona na prática?

Atenciosamente,
[Seu nome]"""

# Create a global instance
email_generator = EmailGenerator()