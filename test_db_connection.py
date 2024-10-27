from sqlalchemy.orm import sessionmaker
from backend.database import engine, Book

# Initialize session
Session = sessionmaker(bind=engine)
session = Session()

# Test book details
new_book = Book(
    title="Test Book",
    author="Test Author",
    genre="Fiction",
    year_published=2022,
    summary="Test summary"
)

# Add book to the database
try:
    session.add(new_book)
    session.commit()
    print("Book added successfully!")
except Exception as e:
    session.rollback()
    print(f"Error adding book: {e}")
finally:
    session.close()
