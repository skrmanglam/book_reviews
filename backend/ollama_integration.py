import ollama
import nest_asyncio
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sentence_transformers import SentenceTransformer
from backend.database import SessionLocal, Book
import chromadb
import numpy as np

############### connection to locally running ollama_infrence #######################################################
async def generate_summary(book_content: str):
    response = ollama.chat(
        model="llama3.1",
        messages=[
            {
                "role": "user",
                "content": f"Summarize the following book content: {book_content}",
            },
        ],
    )
    return response.get("message", {}).get("content", "No summary available")

######################################################################################################################

#nest_asyncio.apply()

# Initialize ChromaDB client and collection
client = chromadb.Client()
collection = client.get_or_create_collection("books")

# Initialize the embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')
dimension = 384  # Dimension for the 'all-MiniLM-L6-v2' model



# Function to index books in ChromaDB
async def index_books():
    async with SessionLocal() as session:
        result = await session.execute(select(Book))
        books = result.scalars().all()

    for book in books:
        text = f"{book.title} {book.author} {book.summary}"
        embedding = model.encode(text).tolist()  # Encode and convert to list
        # Add document with embedding to ChromaDB
        collection.add(
            documents=[text],
            metadatas=[{"title": book.title, "author": book.author, "summary": book.summary}],
            ids=[str(book.id)],
            embeddings=[embedding]
        )

    print("Indexing complete")
    print("Total books in ChromaDB:", len(books))

# Function to search by summary using ChromaDB
async def search_by_summary(query: str):
    # Generate embedding for the query
    query_embedding = model.encode(query).tolist()
    # Search ChromaDB for similar embeddings
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3
    )
    # Format results, assuming `results["metadatas"]` is a list of lists
    formatted_results = [
        f"Title: {doc.get('title', 'N/A')}, Author: {doc.get('author', 'N/A')}, Summary: {doc.get('summary', 'N/A')}"
        for match in results["metadatas"]  # Loop over each list of matches
        for doc in match  # Each doc is a dictionary within the list
    ]

    return "\n\n".join(formatted_results)

if __name__ == "__main__":
    import asyncio
    asyncio.run(index_books())