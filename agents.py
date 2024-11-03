from enum import Enum
from typing import List, Dict, Optional


class IntentType(Enum):
    SEARCH = "search"
    RECOMMEND = "recommend"
    SUMMARIZE = "summarize"
    REVIEW = "review"
    GENERAL = "general"


class BookAgent:
    def __init__(self, rag_system: BookRAG):
        self.rag = rag_system

    async def detect_intent(self, query: str) -> IntentType:
        # Use Ollama to classify intent
        response = ollama.chat(
            model="llama3.1",
            messages=[
                {
                    "role": "system",
                    "content": "Classify the following query into one of these categories: search, recommend, summarize, review, general"
                },
                {
                    "role": "user",
                    "content": query
                }
            ]
        )
        intent = response["message"]["content"].lower().strip()
        return IntentType(intent)

    async def process_query(self, query: str) -> Dict:
        # Detect intent
        intent = await self.detect_intent(query)

        # Route to appropriate handler
        if intent == IntentType.SEARCH:
            return await self.handle_search(query)
        elif intent == IntentType.RECOMMEND:
            return await self.handle_recommendation(query)
        elif intent == IntentType.SUMMARIZE:
            return await self.handle_summary(query)
        elif intent == IntentType.REVIEW:
            return await self.handle_review(query)
        else:
            return await self.handle_general(query)

    async def handle_search(self, query: str) -> Dict:
        contexts = await self.rag.retrieve_relevant_context(query)
        return {
            "type": "search",
            "results": contexts
        }

    async def handle_recommendation(self, query: str) -> Dict:
        # Implement recommendation logic
        pass

    async def handle_summary(self, query: str) -> Dict:
        # Use existing summary generation
        pass

    async def handle_review(self, query: str) -> Dict:
        # Implement review analysis
        pass

    async def handle_general(self, query: str) -> Dict:
        response = await self.rag.chat(query)
        return {
            "type": "general",
            "response": response
        }