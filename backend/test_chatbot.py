"""
Simple test script for the chatbot endpoint without database dependencies
"""
import asyncio
import sys
from app.chatbot.service import ask_chatbot

async def test_chatbot():
    print("Testing NestScore Chatbot...")
    print("-" * 50)
    
    # Test question
    question = "What is NestScore?"
    print(f"Question: {question}")
    print()
    
    # Get response
    response = await ask_chatbot(question)
    
    if response:
        print("Response:")
        print(response)
        print()
        print("✅ Chatbot is working correctly!")
        return 0
    else:
        print("❌ Chatbot failed to respond")
        print("Check if OPENROUTER_API_KEY is set correctly in .env")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(test_chatbot())
    sys.exit(exit_code)
