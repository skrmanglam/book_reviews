from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.database import Book, Review
from sqlalchemy.future import select
from sqlalchemy import or_


async def get_books(db: AsyncSession):
    result = await db.execute(select(Book))
    return result.scalars().all()

async def create_book(db: AsyncSession, book):
    new_book = Book(**book.dict())
    db.add(new_book)
    await db.commit()
    await db.refresh(new_book)
    return new_book

async def get_book_by_id(db: AsyncSession, book_id: int):
    result = await db.execute(select(Book).where(Book.id == book_id))
    return result.scalar_one_or_none()

async def create_review(db: AsyncSession, book_id: int, review):
    new_review = Review(book_id=book_id, **review.dict())
    db.add(new_review)
    await db.commit()
    await db.refresh(new_review)
    return new_review

async def delete_book(db: AsyncSession, book_id: int) -> bool:
    """Delete a single book by its ID."""
    # Fetch the book by ID
    result = await db.execute(select(Book).where(Book.id == book_id))
    book = result.scalar_one_or_none()

    # If the book exists, delete it
    if book:
        await db.delete(book)
        await db.commit()
        return True
    return False


async def search_by_author(db: AsyncSession, author_name: str):
    result = await db.execute(select(Book).where(Book.author.like(f"%{author_name}%")))
    books =  result.scalars().all()
    # Format books into a list of dictionaries
    return [{"title": book.title, "author": book.author, "summary": book.summary} for book in books]

async def search_by_book_name(db: AsyncSession, book_name: str):
    result = await db.execute(select(Book).where(Book.title.like(f"%{book_name}%")))
    books = result.scalars().all()
    # Format books into a list of dictionaries
    return [{"title": book.title, "author": book.author, "summary": book.summary} for book in books]