from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "postgresql+asyncpg://postgres:1234@localhost/book_review"

engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)
Base = declarative_base()

# Define the Book and Review models
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

class Book(Base):
    __tablename__ = 'books'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    author = Column(String(255), nullable=False)
    genre = Column(String(100))
    year_published = Column(Integer)
    summary = Column(Text)
    reviews = relationship('Review', back_populates='book')

class Review(Base):
    __tablename__ = 'reviews'
    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey('books.id'), nullable=False)
    user_id = Column(Integer)
    review_text = Column(Text, nullable=False)
    rating = Column(Integer, nullable=False)
    book = relationship('Book', back_populates='reviews')
