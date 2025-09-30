
import os
from groq import Groq
from sentence_transformers import SentenceTransformer
import faiss
from pathlib import Path
import numpy as np
from dotenv import load_dotenv
from typing import Dict, Any

# Load .env from project root
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

class ChatbotService:
    def __init__(self):
        # Initialize Groq client
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        self.client = Groq(api_key=api_key)
        
        # Load embedding model for RAG
        try:
            self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
            self.embedder_loaded = True
        except Exception as e:
            print(f"Warning: Could not load embedding model: {e}")
            self.embedder = None
            self.embedder_loaded = False
        
        # Fitness knowledge base
        self.knowledge_texts = [
            "Drink at least 8 glasses of water daily for hydration.",
            "For fat loss, a calorie deficit of 300-500 kcal/day is ideal.",
            "Aim for 150 minutes of moderate exercise weekly.",
            "Protein intake should be around 1.6-2.2 g/kg of body weight for muscle gain.",
            "Squats strengthen legs, core, and improve overall stability.",
            "Rest days are crucial for muscle recovery and growth.",
            "Cardio exercises like running, cycling help improve cardiovascular health.",
            "Strength training increases metabolism and bone density.",
            "A balanced diet includes proteins, carbs, healthy fats, and micronutrients.",
            "Sleep 7-9 hours per night for optimal recovery and performance.",
            "Warm-up before exercise prevents injuries and improves performance.",
            "Progressive overload is key to building muscle and strength.",
            "HIIT workouts are effective for burning fat in less time.",
            "Consistency is more important than intensity for long-term results.",
            "Track your progress with measurements, not just scale weight."
        ]
        
        # Create FAISS index for RAG
        if self.embedder_loaded:
            self._create_knowledge_index()
    
    def _create_knowledge_index(self):
        """Create FAISS index from knowledge base"""
        try:
            knowledge_embeddings = self.embedder.encode(
                self.knowledge_texts, 
                convert_to_numpy=True
            )
            self.index = faiss.IndexFlatL2(knowledge_embeddings.shape[1])
            self.index.add(knowledge_embeddings)
        except Exception as e:
            print(f"Warning: Could not create FAISS index: {e}")
            self.index = None
    
    def _retrieve_context(self, query: str, k: int = 2) -> str:
        """Retrieve relevant context using RAG"""
        if not self.embedder_loaded or self.index is None:
            return ""
        
        try:
            query_vector = self.embedder.encode([query], convert_to_numpy=True)
            D, I = self.index.search(query_vector, k=k)
            retrieved_context = "\n".join([self.knowledge_texts[i] for i in I[0]])
            return retrieved_context
        except Exception as e:
            print(f"Warning: Context retrieval failed: {e}")
            return ""
    
    async def get_chat_response(self, user_query: str) -> str:
        """Generate chatbot response using Groq API with RAG"""
        
        # Retrieve relevant context
        retrieved_context = self._retrieve_context(user_query)
        
        # System prompt
        system_prompt = """You are a supportive AI fitness coach named FitAI. 
        
Your role:
- Provide practical, motivational fitness and nutrition advice
- Be encouraging and supportive
- Give specific, actionable recommendations
- Keep responses concise (2-4 sentences typically)
- If a question is outside fitness/health, politely redirect to fitness topics
- If uncertain about medical advice, recommend consulting a healthcare professional

Your expertise includes:
- Workout programming and exercise form
- Nutrition and meal planning
- Weight management (loss/gain)
- Muscle building and strength training
- Cardiovascular fitness
- Recovery and injury prevention
- Motivation and habit formation

Always be positive, clear, and helpful!"""

        # Construct user message with context
        user_message = f"User question: {user_query}"
        if retrieved_context:
            user_message += f"\n\nRelevant fitness knowledge:\n{retrieved_context}"
        
        try:
            # Call Groq API
            completion = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=300
            )
            
            return completion.choices[0].message.content.strip()
        
        except Exception as e:
            return f"I'm having trouble processing your request right now. Error: {str(e)}"
    
    def check_service_health(self) -> Dict[str, Any]:
        """Check chatbot service health"""
        groq_configured = bool(os.getenv("GROQ_API_KEY"))
        
        return {
            "service_ready": groq_configured and self.embedder_loaded,
            "groq_api_configured": groq_configured,
            "embedder_loaded": self.embedder_loaded
        }

# Create singleton instance
chatbot_service = ChatbotService()