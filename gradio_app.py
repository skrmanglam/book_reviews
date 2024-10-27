import gradio as gr
import requests
import asyncio
from backend.ollama_integration import generate_summary
from main import add_book, view_book, fetch_book_summary, summarize_with_ollama  # Import the combined function

from backend.database import SessionLocal, Book
from sqlalchemy.exc import SQLAlchemyError

import asyncio
from backend.database import Book
from backend.ollama_integration import generate_summary

# Assuming FastAPI is running locally on port 8000
BASE_URL = "http://127.0.0.1:8000"

# Functions for CRUD operations with FastAPI endpoints

# ---- Book Functions ----
def add_book(title, author, genre, year, summary):
    response = requests.post(f"{BASE_URL}/books", json={
        "title": title,
        "author": author,
        "genre": genre,
        "year_published": int(year),
        "summary": summary
    })
    if response.status_code == 200:
        return f"Book '{title}' added successfully!"
    else:
        return f"Failed to add book: {response.text}"

def view_book(book_id):
    response = requests.get(f"{BASE_URL}/books/{book_id}")
    if response.status_code == 200:
        book = response.json()
        return f"Title: {book['title']}\nAuthor: {book['author']}\nGenre: {book['genre']}\nYear Published: {book['year_published']}\nSummary: {book['summary']}"
    else:
        return "Book not found."

def update_book(book_id, title, author, genre, year, summary):
    # Ensure genre is a string before passing
    genre_str = str(genre) if genre else ""
    response = requests.put(f"{BASE_URL}/books/{book_id}", json={
        "title": title,
        "author": author,
        "genre": genre,
        "year_published": int(year),
        "summary": summary
    })
    if response.status_code == 200:
        return f"Book ID {book_id} updated successfully!"
    else:
        return f"Failed to update book: {response.text}"

def delete_book(book_id):
    response = requests.delete(f"{BASE_URL}/books/{book_id}")
    if response.status_code == 200:
        return f"Book ID {book_id} deleted successfully!"
    else:
        return f"Failed to delete book: {response.text}"

async def generate_summary_ui(title, author):
    summary = await fetch_book_summary(title, author)
    final_summary = await summarize_with_ollama(summary)
    return final_summary

# ---- Review Functions ----
def add_review(book_id, user_id, review_text, rating):
    response = requests.post(f"{BASE_URL}/books/{book_id}/reviews", json={
        "user_id": user_id,
        "review_text": review_text,
        "rating": rating
    })
    if response.status_code == 200:
        return "Review added successfully!"
    else:
        return f"Failed to add review: {response.text}"

def view_reviews(book_id):
    response = requests.get(f"{BASE_URL}/books/{book_id}/reviews")
    if response.status_code == 200:
        reviews = response.json()
        if reviews:
            return "\n\n".join([f"User ID: {r['user_id']}, Rating: {r['rating']}\n{r['review_text']}" for r in reviews])
        else:
            return "No reviews found for this book."
    else:
        return "Failed to fetch reviews."

def delete_review(review_id):
    response = requests.delete(f"{BASE_URL}/reviews/{review_id}")
    if response.status_code == 200:
        return "Review deleted successfully!"
    else:
        return f"Failed to delete review: {response.text}"


def generate_summary(title, author):
    # Call the combined function to fetch and optionally summarize the book content
    summary = fetch_and_summarize_book(title, author)
    return summary

# UI button interactions
def add_book_ui(title, author, genre, year_published, summary):
    # Ensure genre is a string before passing
    genre_str = str(genre) if genre else ""
    return add_book(title, author, genre, year_published, summary)

def view_book_ui(book_id):
    result = view_book(book_id)
    if "Book not found" in result:
        return "Book ID not found. Please check and try again."
    return result

# Gradio UI
with gr.Blocks() as app:
    gr.Markdown("# Book & Review Management")

    with gr.Tabs():
        # Book Tab
        with gr.Tab("Books"):
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### Add Book")
                    title = gr.Textbox(label="Title")
                    author = gr.Textbox(label="Author")
                    genre = gr.Dropdown(["Fiction", "Non-fiction", "Science", "Fantasy", "Mystery", "Biography", "Unkown"],
                                        label="Genre", value = "Unkown")
                    year_published = gr.Number(label="Year Published", value=2023)
                    summary = gr.Textbox(label="Summary", lines=5)

                    # Generate Summary Button
                    generate_button = gr.Button("Generate Summary")
                    generate_button.click(generate_summary_ui, [title, author], summary)

                    # Add Book Button
                    add_book_button = gr.Button("Add Book")
                    add_book_result = gr.Textbox(label="Result")
                    add_book_button.click(add_book_ui, [title, author, genre, year_published, summary], add_book_result)

                with gr.Column():
                    gr.Markdown("### View / Update / Delete Book")
                    book_id = gr.Number(label="Enter Book ID")
                    view_book_button = gr.Button("View Book")
                    book_info = gr.Textbox(label="Book Information", lines=10)
                    view_book_button.click(view_book_ui, [book_id], book_info)

                    update_book_button = gr.Button("Update Book")
                    delete_book_button = gr.Button("Delete Book")
                    update_result = gr.Textbox(label="Result")
                    update_book_button.click(update_book, [book_id, title, author, genre, year_published, summary],
                                             update_result)
                    delete_book_button.click(delete_book, [book_id], update_result)

            # Review Tab
        with gr.Tab("Reviews"):
            with gr.Row():
                with gr.Column():
                        gr.Markdown("### Add Review")
                        review_book_id = gr.Number(label="Book ID")
                        user_id = gr.Number(label="User ID")
                        review_text = gr.Textbox(label="Review Text", lines=4)
                        rating = gr.Slider(1, 5, label="Rating", step=1)

                        add_review_button = gr.Button("Add Review")
                        add_review_result = gr.Textbox(label="Result")
                        add_review_button.click(add_review, [review_book_id, user_id, review_text, rating],
                                                add_review_result)

                with gr.Column():
                        gr.Markdown("### View / Delete Reviews")
                        view_review_book_id = gr.Number(label="Book ID")
                        view_reviews_button = gr.Button("View Reviews")
                        review_info = gr.Textbox(label="Review Information", lines=10)
                        view_reviews_button.click(view_reviews, [view_review_book_id], review_info)

                        delete_review_id = gr.Number(label="Review ID")
                        delete_review_button = gr.Button("Delete Review")
                        delete_review_result = gr.Textbox(label="Result")
                        delete_review_button.click(delete_review, [delete_review_id], delete_review_result)


app.launch()