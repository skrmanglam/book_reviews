import streamlit as st
import requests
import asyncio
from sqlalchemy.orm import sessionmaker
from backend.database import engine, Book, SessionLocal
from backend.ollama_integration import generate_summary

# Google Books API URL
GOOGLE_BOOKS_API_URL = "https://www.googleapis.com/books/v1/volumes"

# Function to fetch summary from Google Books API
def fetch_summary_from_google_books(title: str, author: str):
    response = requests.get(f"{GOOGLE_BOOKS_API_URL}?q=intitle:{title}+inauthor:{author}")
    if response.status_code == 200:
        data = response.json()
        if "items" in data:
            volume_info = data["items"][0]["volumeInfo"]
            return volume_info.get("description", "No description available.")
    return None

# Streamlit UI for adding a book
st.title("Add a New Book")

# Book addition form fields
title = st.text_input("Book Title")
author = st.text_input("Author Name")
genre = st.selectbox("Genre", ["Fiction", "Non-fiction", "Fantasy", "Mystery", "Biography", "Science Fiction"])
year_published = st.number_input("Year Published", min_value=0, max_value=2023, step=1)
summary = ""

# Generate summary when button clicked
if st.button("Generate Summary") and title and author:
    st.write("Fetching summary from Google Books API...")
    google_summary = fetch_summary_from_google_books(title, author)

    if google_summary:
        # Check if the summary is lengthy; if so, summarize it using Llama
        if len(google_summary) > 300:
            st.write("Summary is long; summarizing with Llama API...")
            summary = asyncio.run(generate_summary(google_summary))
        else:
            summary = google_summary
        st.success("Summary generated!")
        st.text_area("Generated Summary", summary, height=150)
    else:
        st.warning("No summary found in Google Books API.")

# Book submission button
if st.button("Add Book") and title and author and summary:
    # Each time, open a new session to avoid shared session issues
    session = SessionLocal()
    try:
        new_book = Book(title=title, author=author, genre=genre, year_published=year_published, summary=summary)
        session.add(new_book)
        session.commit()
        st.success(f"Book '{title}' by {author} added successfully!")
        print("Book added successfully!")  # Debugging print statement

        # Check database directly after commit
        result = session.query(Book).filter_by(title=title, author=author).first()
        if result:
            print("Book found in database:", result.title, result.author)
        else:
            print("Book not found in database after commit.")

    except Exception as e:
        session.rollback()  # Rollback in case of an error
        st.error("Failed to add book to the database.")
        print(f"Error: {e}")  # Print the error to the console for debugging

    finally:
        session.close()  # Close the session after each operation
