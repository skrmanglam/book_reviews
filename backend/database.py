# Import necessary modules for database and API settings
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.future import select
from fastapi import HTTPException, Depends, status
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
import ollama
from dotenv import load_dotenv
import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine


# # Database setup with SQLAlchemy
# DATABASE_URL = "postgresql+psycopg2://postgres:1234@localhost/book_review" # Replace with your actual database URL

# Replace with your database URL, ensuring it uses asyncpg for async PostgreSQL support
DATABASE_URL = "postgresql+asyncpg://postgres:1234@localhost/book_review"

# Access the DATABASE_URL environment variable
# print(os.getcwd())
# env_path = Path('.') / '.env'
# load_dotenv(dotenv_path=env_path)
# DATABASE_URL = os.getenv("DATABASE_URL")
# print("Database URL:", DATABASE_URL)


# # engine = create_async_engine(DATABASE_URL, echo=True) # Asynchronous engine for database interaction
# # SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession) # Session configuration for async operations
# # Base = declarative_base() # Base class for defining models
#
# # Create synchronous engine and session
# engine = create_engine(DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#
# Base = declarative_base()

# Create an async engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Base class for models
Base = declarative_base()

# Async session local factory
SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Define the Book model (represents the books table in the database)
class Book(Base):
    __tablename__ = 'books'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    author = Column(String(255), nullable=False)
    genre = Column(String(100))
    year_published = Column(Integer)
    summary = Column(Text)
    reviews = relationship('Review', back_populates='book') # Relationship with the Review model

# Define the Review model (represents the reviews table in the database)
class Review(Base):
    __tablename__ = 'reviews'
    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey('books.id'), nullable=False) # Foreign key to the books table
    user_id = Column(Integer)
    review_text = Column(Text, nullable=False)
    rating = Column(Integer, nullable=False)
    book = relationship('Book', back_populates='reviews')  # Back-reference to the Book model
