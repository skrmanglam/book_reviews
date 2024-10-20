from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import engine, Base, SessionLocal
from backend.crud import get_books, create_book, get_book_by_id, create_review, delete_book
from backend.schemas import BookCreate, BookRead, ReviewCreate, ReviewRead
from backend.ollama_integration import generate_summary
from pydantic import BaseModel
import requests

app = FastAPI()

# Dependency to get the database session
async def get_db():
    async with SessionLocal() as session:
        yield session

# Initialize the database on startup
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Endpoint to add a new book
@app.post("/books", response_model=BookRead)
async def create_book_endpoint(book: BookCreate, db: AsyncSession = Depends(get_db)):
    return await create_book(db, book)

# Endpoint the get all books
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

# Request body schema for generating the summary
class BookSummaryRequest(BaseModel):
    title: str
    author: str


# Webhook to fetch the book summary from an external API like Google Books
def fetch_book_summary(title: str, author: str):
    google_books_api = f"https://www.googleapis.com/books/v1/volumes?q=intitle:{title}+inauthor:{author}"
    response = requests.get(google_books_api)
    print('response from book_api', response)

    if response.status_code == 200:
        data = response.json()
        if "items" in data and len(data["items"]) > 0:
            # Extract the description of the first book that matches
            book_info = data["items"][0]["volumeInfo"]
            return book_info.get("description", "No summary available for this book.")
        else:
            return "No summary found for this book."
    else:
        return "Error fetching summary from Google Books."


# Endpoint to generate a summary based on title and author using Google Books API
@app.post("/generate-summary")
async def generate_summary_endpoint(book_info: BookSummaryRequest):
    summary = fetch_book_summary(book_info.title, book_info.author)

    if summary:
        return {"summary": summary}
    else:
        raise HTTPException(status_code=404, detail="Summary not found for this book.")

