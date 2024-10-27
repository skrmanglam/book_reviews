from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.database import engine, Base, SessionLocal, Book, Review
from backend.crud import get_books, create_book, get_book_by_id, create_review, delete_book
from backend.schemas import BookCreate, BookRead, ReviewCreate, ReviewRead
from backend.schemas import BookSummaryRequest
from backend.ollama_integration import generate_summary
from pydantic import BaseModel
import requests
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import SessionLocal
from backend.database import Base, engine
import httpx

app = FastAPI()


# Function to initialize the database
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Dependency for accessing database session
# Dependency to get the database session
async def get_db():
    async with SessionLocal() as session:  # Ensure this uses async with
        yield session

# On app startup, initialize the database
# Startup event to initialize the database
# Startup event to initialize the database
@app.on_event("startup")
async def startup():
    await init_db()

# --- API Endpoints ---

# Endpoint to add a new book
@app.post("/books", response_model=BookRead)
async def create_book_endpoint(book: BookCreate, db: AsyncSession = Depends(get_db)):
    return await create_book(db, book)


# Endpoint to get all books
@app.get("/books", response_model=list[BookRead])
async def get_books_endpoint(db: AsyncSession = Depends(get_db)):
    return await get_books(db)


# Endpoint to get a specific book by ID
@app.get("/books/{book_id}", response_model=BookRead)
async def get_book_endpoint(book_id: int, db: AsyncSession = Depends(get_db)):
    book = await get_book_by_id(db, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


# Endpoint to create a review for a specific book
@app.post("/books/{book_id}/reviews", response_model=ReviewRead)
async def create_review_endpoint(book_id: int, review: ReviewCreate, db: AsyncSession = Depends(get_db)):
    book = await get_book_by_id(db, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return await create_review(db, book_id, review)


# Endpoint to delete a book by its ID
@app.delete("/books/{book_id}")
async def delete_book_endpoint(book_id: int, db: AsyncSession = Depends(get_db)):
    success = await delete_book(db, book_id)
    if not success:
        raise HTTPException(status_code=404, detail="Book not found")
    return {"message": "Book deleted successfully"}


# Function to fetch the book summary from an external API like Google Books
# Function to fetch summary from Google Books API asynchronously
async def fetch_book_summary(title: str, author: str):
    google_books_api = f"https://www.googleapis.com/books/v1/volumes?q=intitle:{title}+inauthor:{author}"
    async with httpx.AsyncClient() as client:
        response = await client.get(google_books_api)
    if response.status_code == 200:
        data = response.json()
        #print(data) for future use of retireving ISBN info.
        if "items" in data and len(data["items"]) > 0:
            book_info = data["items"][0]["volumeInfo"]
            return book_info.get("description", "No summary available for this book.")
    return "Error fetching summary from Google Books."


# Endpoint to generate a summary based on title and author using Google Books API
@app.post("/generate-summary")
async def generate_summary_endpoint(book_info: BookSummaryRequest):
    summary = fetch_book_summary(book_info.title, book_info.author)
    if summary:
        return {"summary": summary}
    else:
        raise HTTPException(status_code=404, detail="Summary not found for this book.")


# Endpoint to update a book by ID
@app.put("/books/{book_id}", response_model=BookRead)
async def update_book(book_id: int, book_data: BookCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Book).where(Book.id == book_id))
    book = result.scalar_one_or_none()

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    # Update the book's fields
    for key, value in book_data.dict().items():
        setattr(book, key, value)

    await db.commit()
    await db.refresh(book)
    return book


# --- Missing Review Endpoints ---

# Endpoint to add a review for a book
@app.post("/books/{book_id}/reviews", response_model=ReviewRead)
async def add_review(book_id: int, review: ReviewCreate, db: AsyncSession = Depends(get_db)):
    # Ensure the book exists
    book = await get_book_by_id(db, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    # Create the new review
    return await create_review(db, book_id, review)


# Endpoint to retrieve all reviews for a specific book
@app.get("/books/{book_id}/reviews", response_model=list[ReviewRead])
async def get_reviews(book_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Review).where(Review.book_id == book_id))
    reviews = result.scalars().all()
    return reviews


# Endpoint to get recommendations (mocked for now)
@app.get("/recommendations")
async def get_recommendations():
    recommendations = [
        {"title": "1984", "author": "George Orwell", "genre": "Dystopian"},
        {"title": "To Kill a Mockingbird", "author": "Harper Lee", "genre": "Classic Fiction"},
        {"title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "genre": "Classic Fiction"},
    ]
    return recommendations


import asyncio
from backend.ollama_integration import generate_summary as ollama_generate_summary


# Summarize using Ollama if the summary is too long
async def summarize_with_ollama(summary_text):
    if len(summary_text) > 300:  # Adjust length check if needed
        response = await generate_summary(summary_text)
        return response
    return summary_text

# Add a new book to the database
async def add_book(title: str, author: str, genre: str, year_published: int, summary: str, db: AsyncSession):
    book_data = BookCreate(title=title, author=author, genre=genre, year_published=year_published, summary=summary)
    new_book = await create_book(db, book_data)
    return new_book

# Retrieve a book by its ID
async def view_book(book_id: int, db: AsyncSession):
    book = await get_book_by_id(db, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

