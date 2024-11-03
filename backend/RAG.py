from typing import List, Dict, Optional
import ollama
from sentence_transformers import SentenceTransformer
from backend.database import SessionLocal
from backend.ollama_integration import collection, model

class BookRAG:
    def __init__(self):
        self.collection = collection
        self.model = model
        self.sessions = {}  # Dictionary to maintain context by session ID

    async def retrieve_relevant_context(self, query: str,session_id: str, k: int = 3) -> List[Dict]:
        # Manage sessions
        if session_id not in self.sessions:
            self.sessions[session_id] = []

        # generate embedding for the query
        query_embedding = self.model.encode(query).tolist()

        # search ChromaDB for similar content
        results = self.collection.query(
            [query_embedding],
            n_results=k
        )

        # format the context
        contexts = []
        for metadata, distance in zip(results["metadatas"][0], results["distances"][0]):
            context = {
                "content": f"Title: {metadata['title']}\nAuthor: {metadata['author']}\nSummary: {metadata['summary']}",
                "relevance_score": 1 - distance  # Convert distance to similarity score
            }
        contexts.append(context)
        self.sessions[session_id].append(context)  # Append new context to session history

        return contexts

    async def generate_response(self, query: str,session_id: str) -> str:
        contexts = self.sessions.get(session_id, [])
        # Prepare prompt with context
        prompt = self._prepare_prompt(query, contexts)

        # Generate response using Ollama
        response = ollama.chat(
            model = "llama3.1",
            messages= [
            {
                "role" : "system",
                "content" : "You are a chatty and a helpful sales assistant specificallly knowledgebale about books.Be polite and try to help the users. Use the provided context to answer questions about books."
                            "Provided context may contain information about books, authors and their summary. Recommend books on your knowledge and be poliste like: I am afraid I do not have this particular book with me."
            },
            {
                "role" : "user",
                "content": prompt
            }
             ]
         )

        return response["message"]["content"]

    def _prepare_prompt(self, query: str, contexts: List[Dict]) -> str:
        # Combine contexts, weighted by relevance
        context_text = '\n\n'.join([
            f"Relevance: {ctx['relevance_score']:.2f}\n{ctx['content']}"
            for ctx in sorted(contexts, key = lambda x: x['relevance_score'],reverse = True)
        ])

        return f"""Context information is below:
                  {context_text}

                Given the context information, please answer the following question:
                {query}

                If the answer cannot be found in the context, please say "I don't have enough inforamtion to answer that question." Please do not provide additional reasoing to your answers.
                """

    async def chat(self, query: str, session_id: str) -> str:
        # Retrieve relevant context
        contexts = await self.retrieve_relevant_context(query, session_id)

        # Generate response
        response = await self.generate_response(query, session_id)

        return response