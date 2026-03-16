"""
OpenRouter AI chatbot service for NestScore.
Implements the official NestScore Assistant using Step 3.5 Flash.
"""
import logging
import os
from typing import Optional
import httpx
from app.config import settings

logger = logging.getLogger(__name__)

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "stepfun/step-3.5-flash:free"


def load_system_prompt() -> str:
    """Load and combine system prompt with knowledge base."""
    prompt_path = os.path.join(os.path.dirname(__file__), 'system_prompt.txt')
    kb_path = os.path.join(os.path.dirname(__file__), 'knowledge_base.txt')
    
    with open(prompt_path, 'r', encoding='utf-8') as sp:
        prompt = sp.read()
    
    with open(kb_path, 'r', encoding='utf-8') as kb:
        knowledge = kb.read()
    
    return prompt.replace(
        '[PASTE THE FULL KNOWLEDGE BASE FROM PART 2 OF THIS DOCUMENT HERE]',
        knowledge
    )


async def ask_chatbot(user_message: str) -> Optional[str]:
    """
    Send a message to NestScore Assistant and get a response.
    Returns None if OpenRouter API is not configured or request fails.
    """
    if not settings.OPENROUTER_API_KEY:
        logger.warning("OPENROUTER_API_KEY not configured - chatbot disabled")
        return None
    
    try:
        system_prompt = load_system_prompt()
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                OPENROUTER_API_URL,
                headers={
                    "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": MODEL,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    "max_tokens": 500,
                    "temperature": 0.7,
                },
            )
            
            if response.status_code != 200:
                logger.error(f"OpenRouter API error: {response.status_code}")
                return None
            
            data = response.json()
            answer = data["choices"][0]["message"]["content"]
            
            logger.info("Chatbot: Question answered successfully")
            return answer.strip()
            
    except Exception as e:
        logger.error(f"Error calling OpenRouter API: {e}")
        return None
