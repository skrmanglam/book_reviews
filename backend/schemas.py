from pydantic import BaseModel

# Pydantic schema for API requests and responses
class BookCreate(BaseModel):
    title: str
    author: str
    genre: str
    year_published: int
    summary: str

class ReviewCreate(BaseModel):
    user_id: int
    review_text: str
    rating: int

class BookRead(BookCreate):
    id: int

class ReviewRead(ReviewCreate):
    id: int

# Pydantic schema for the book content 
class BookContent(BaseModel):
    book_content: str

# Define BookSummaryRequest schema
class BookSummaryRequest(BaseModel):
    title: str
    author: str