from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.database import Book, Review

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

async def delete_book(db: AsyncSession, book_id: int):
    book = await get_book_by_id(db, book_id)
    if book:
        await db.delete(book)
        await db.commit()
        return True
    return False
