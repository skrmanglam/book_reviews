from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import engine, Base, SessionLocal
from backend.crud import get_books, create_book, get_book_by_id, create_review, delete_book
from backend.schemas import BookCreate, BookRead, ReviewCreate, ReviewRead
from backend.ollama_integration import generate_summary

app = FastAPI()

# Dependency
async def get_db():
    async with SessionLocal() as session:
        yield session

# Initialize the database
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.post("/books", response_model=BookRead)
async def create_book_endpoint(book: BookCreate, db: AsyncSession = Depends(get_db)):
    return await create_book(db, book)

@app.get("/books", response_model=list[BookRead])
async def get_books_endpoint(db: AsyncSession = Depends(get_db)):
    return await get_books(db)

@app.get("/books/{book_id}", response_model=BookRead)
async def get_book_endpoint(book_id: int, db: AsyncSession = Depends(get_db)):
    book = await get_book_by_id(db, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@app.post("/books/{book_id}/reviews", response_model=ReviewRead)
async def create_review_endpoint(book_id: int, review: ReviewCreate, db: AsyncSession = Depends(get_db)):
    book = await get_book_by_id(db, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return await create_review(db, book_id, review)

@app.delete("/books/{book_id}")
async def delete_book_endpoint(book_id: int, db: AsyncSession = Depends(get_db)):
    success = await delete_book(db, book_id)
    if not success:
        raise HTTPException(status_code=404, detail="Book not found")
    return {"message": "Book deleted successfully"}

@app.post("/generate-summary")
async def generate_summary_endpoint(book_content: str):
    return {"summary": await generate_summary(book_content)}
