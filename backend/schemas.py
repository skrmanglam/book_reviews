from pydantic import BaseModel

# Pydantic models for books
class BookCreate(BaseModel):
    title: str
    author: str
    genre: str
    year_published: int
    summary: str

class BookRead(BookCreate):
    id: int

# Pydantic models for reviews
class ReviewCreate(BaseModel):
    user_id: int
    review_text: str
    rating: int

class ReviewRead(ReviewCreate):
    id: int
