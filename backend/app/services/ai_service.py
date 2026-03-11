"""AI Service for generating intelligent responses using OpenRouter API with free Step 3.5 Flash model."""
import os
from typing import Optional
import httpx
from app.config import settings


class AIService:
    """Service for generating AI-powered responses using OpenRouter's free Step 3.5 Flash model."""
    
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY", "")
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "stepfun/step-3.5-flash:free"
        self.app_name = "NestScore"
        self.app_url = "https://nestscore.co.ke"
        self.enabled = bool(self.api_key)
    
    async def generate_response(
        self, 
        prompt: str, 
        system_message: str = "You are a helpful assistant for NestScore, a rental plot review platform.",
        max_tokens: int = 500,
        temperature: float = 0.7
    ) -> Optional[str]:
        """Generate AI response using OpenRouter API with Step 3.5 Flash (free)."""
        if not self.enabled:
            return None
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.base_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": self.app_url,
                        "X-Title": self.app_name
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": system_message},
                            {"role": "user", "content": prompt}
                        ],
                        "max_tokens": max_tokens,
                        "temperature": temperature
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data["choices"][0]["message"]["content"].strip()
                else:
                    return None
        except Exception:
            return None
    
    async def generate_plot_description(self, plot_name: str, area: str) -> str:
        """Generate a description for a new plot."""
        prompt = f"Generate a brief, professional description (2-3 sentences) for a rental plot called '{plot_name}' located in the {area} area. Focus on location benefits and typical amenities."
        
        response = await self.generate_response(
            prompt=prompt,
            system_message="You are a real estate content writer for NestScore, a student housing review platform in Kenya.",
            max_tokens=150,
            temperature=0.8
        )
        
        return response or f"A rental plot located in {area}."
    
    async def analyze_review_sentiment(self, review_text: str) -> dict:
        """Analyze sentiment and extract key points from a review."""
        prompt = f"Analyze this rental review and provide: 1) Sentiment (positive/negative/neutral), 2) Key points (max 3). Review: '{review_text}'"
        
        response = await self.generate_response(
            prompt=prompt,
            system_message="You are a review analysis assistant. Provide concise, structured analysis.",
            max_tokens=200,
            temperature=0.3
        )
        
        if response:
            return {"analysis": response, "ai_generated": True}
        return {"analysis": "Unable to analyze", "ai_generated": False}
    
    async def generate_dispute_response_suggestion(
        self, 
        review_text: str, 
        landlord_response: str
    ) -> str:
        """Generate a suggested admin response for a dispute."""
        prompt = f"""A landlord has disputed this review:
Review: "{review_text}"
Landlord's Response: "{landlord_response}"

Suggest a fair, professional admin response (2-3 sentences) that addresses both perspectives."""
        
        response = await self.generate_response(
            prompt=prompt,
            system_message="You are a fair mediator for rental disputes. Provide balanced, professional responses.",
            max_tokens=200,
            temperature=0.6
        )
        
        return response or "Please review both the original review and landlord's response carefully."
    
    async def generate_welcome_message(self, user_context: str = "") -> str:
        """Generate a personalized welcome message for the platform."""
        prompt = f"Generate a friendly welcome message (1-2 sentences) for new users visiting NestScore. {user_context}"
        
        response = await self.generate_response(
            prompt=prompt,
            system_message="You are a friendly community manager for NestScore.",
            max_tokens=100,
            temperature=0.9
        )
        
        return response or "Welcome to NestScore! Find honest reviews of rental plots."
    
    async def summarize_reviews(self, reviews: list[str]) -> str:
        """Generate a summary of multiple reviews."""
        if not reviews:
            return "No reviews available."
        
        reviews_text = "\n".join([f"- {r}" for r in reviews[:10]])  # Limit to 10 reviews
        prompt = f"Summarize the common themes from these rental reviews in 3-4 sentences:\n{reviews_text}"
        
        response = await self.generate_response(
            prompt=prompt,
            system_message="You are a data analyst summarizing user feedback.",
            max_tokens=250,
            temperature=0.5
        )
        
        return response or "Multiple reviews available for this plot."
    
    async def generate_suggestion_feedback(self, suggestion_name: str, area: str, notes: str) -> str:
        """Generate feedback for a plot suggestion."""
        prompt = f"A user suggested adding '{suggestion_name}' in {area}. Notes: '{notes}'. Provide brief feedback (2 sentences) on whether this seems like a valid suggestion."
        
        response = await self.generate_response(
            prompt=prompt,
            system_message="You are a community moderator evaluating plot suggestions.",
            max_tokens=150,
            temperature=0.6
        )
        
        return response or "Thank you for your suggestion. We'll review it."


# Global AI service instance
ai_service = AIService()
