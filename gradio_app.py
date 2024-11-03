import gradio as gr
import requests
import asyncio
from backend.ollama_integration import generate_summary
from main import add_book, view_book, fetch_book_summary, summarize_with_ollama  # Import the combined function
from backend.crud import search_by_author, search_by_book_name
from backend.ollama_integration import search_by_summary
from backend.database import SessionLocal
from backend.database import SessionLocal, Book
from sqlalchemy.exc import SQLAlchemyError

import asyncio
from backend.database import Book
from backend.ollama_integration import generate_summary
from backend.ollama_integration import generate_summary, index_books, search_by_summary
import nest_asyncio
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import Book, SessionLocal
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.RAG import BookRAG
import uuid

# Generate a unique session ID
session_id = str(uuid.uuid4())

rag_instance = BookRAG()

# Apply nest_asyncio to allow nested async loops
nest_asyncio.apply()


# Ensure index_books runs at startup
# async def initialize_app():
#     await index_books()

# # Run initialization before launching the app
# asyncio.run(initialize_app())

# Replace with your database URL, ensuring it uses asyncpg for async PostgreSQL support
DATABASE_URL = "postgresql+asyncpg://postgres:1234@localhost/book_review"

# Create a session factory for concurrent operations
async_engine = create_async_engine(
    "postgresql+asyncpg://postgres:1234@localhost/book_review",
    echo=True,
    pool_size=20,
    max_overflow=0
)

AsyncSessionFactory = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

@asynccontextmanager
async def get_session():
    """Create a new session for each operation"""
    async with AsyncSessionFactory() as session:
        try:
            yield session
        finally:
            await session.close()

async def run_db_query(query_func, *args):
    """
    Helper function to properly manage database sessions for queries
    """
    async with SessionLocal() as session:
        async with session.begin():
            try:
                result = await query_func(session, *args)
                return result
            except Exception as e:
                await session.rollback()
                raise e


async def search_books_by_author(author_name: str) -> List[Dict[str, Any]]:
    """
    Search for books by author name with proper concurrent handling
    """
    async with get_session() as session:
        try:
            query = select(Book).where(Book.author.ilike(f"%{author_name}%"))
            result = await session.execute(query)
            books = result.scalars().all()

            if not books:
                return [
                    {"title": "No books found", "author": "N/A", "summary": "No matching books found for this author"}]

            return [
                {
                    "title": book.title,
                    "author": book.author,
                    "summary": book.summary if book.summary else "No summary available"
                }
                for book in books
            ]
        except Exception as e:
            print(f"Database error in search_by_author: {str(e)}")
            return [{"title": "Error", "author": "N/A", "summary": f"Search error: {str(e)}"}]


async def search_books_by_name(book_name: str) -> List[Dict[str, Any]]:
    """
    Search for books by book name with proper concurrent handling
    """
    async with get_session() as session:
        try:
            query = select(Book).where(Book.title.ilike(f"%{book_name}%"))
            result = await session.execute(query)
            books = result.scalars().all()

            if not books:
                return [
                    {"title": "No books found", "author": "N/A", "summary": "No matching books found with this title"}]

            return [
                {
                    "title": book.title,
                    "author": book.author,
                    "summary": book.summary if book.summary else "No summary available"
                }
                for book in books
            ]
        except Exception as e:
            print(f"Database error in search_by_book_name: {str(e)}")
            return [{"title": "Error", "author": "N/A", "summary": f"Search error: {str(e)}"}]


def create_sync_search_handler(search_func):
    """
    Create a synchronous handler for async search functions with semaphore control
    """
    semaphore = asyncio.Semaphore(5)  # Limit concurrent operations

    def sync_wrapper(search_term: str) -> str:
        async def wrapped():
            async with semaphore:  # Control concurrent access
                try:
                    results = await search_func(search_term)
                    return "\n\n".join([
                        f"Title: {book['title']}\nAuthor: {book['author']}\nSummary: {book['summary']}"
                        for book in results
                    ])
                except Exception as e:
                    return f"Search error: {str(e)}"

        # Create a new event loop for each search operation
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(wrapped())
        finally:
            loop.close()

    return sync_wrapper


def create_sync_handler(async_func):
    """
    Create a synchronous handler for async database functions
    """
    def sync_wrapper(*args, **kwargs):
        async def wrapped():
            try:
                result = await run_db_query(async_func, *args)
                if isinstance(result, list):
                    return "\n\n".join([
                        f"Title: {book.title}, Author: {book.author}, Summary: {book.summary}"
                        for book in result
                    ])
                return str(result)
            except Exception as e:
                return f"Error: {str(e)}"

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(wrapped())
        finally:
            loop.close()

    return sync_wrapper

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


# def generate_summary(title, author):
#     # Call the combined function to fetch and optionally summarize the book content
#     summary = fetch_and_summarize_book(title, author)
#     return summary

# UI button interactions
# def add_book_ui(title, author, genre, year_published, summary):
#     # Ensure genre is a string before passing
#     genre_str = str(genre) if genre else ""
#     return add_book(title, author, genre, year_published, summary)

# def view_book_ui(book_id):
#     result = view_book(book_id)
#     if "Book not found" in result:
#         return "Book ID not found. Please check and try again."
#     return result

# ---- Async Functions for CRUD Operations ----

import asyncio

# def sync_search_by_author(author_name: str):
#     try:
#         # Try to get the running event loop
#         loop = asyncio.get_running_loop()
#         # Use `ensure_future` for safe scheduling in the existing loop
#         future = asyncio.ensure_future(async_search_by_author(author_name))
#         return loop.run_until_complete(future)
#     except RuntimeError:
#         # If no loop is running, create a new one
#         return asyncio.run(async_search_by_author(author_name))
#
# def sync_search_by_book_name(book_name: str):
#     try:
#         loop = asyncio.get_running_loop()
#         future = asyncio.ensure_future(async_search_by_book_name(book_name))
#         return loop.run_until_complete(future)
#     except RuntimeError:
#         return asyncio.run(async_search_by_book_name(book_name))
#
# def sync_search_by_summary(summary_text: str):
#     try:
#         loop = asyncio.get_running_loop()
#         future = asyncio.ensure_future(async_search_by_summary(summary_text))
#         return loop.run_until_complete(future)
#     except RuntimeError:
#         return asyncio.run(async_search_by_summary(summary_text))



# ---- Async Functions for CRUD Operations ----

async def async_search_by_author(author_name: str):
    async with SessionLocal() as db:
        books = await search_by_author(db, author_name)
    return "\n\n".join([f"Title: {book['title']}, Author: {book['author']}, Summary: {book['summary']}" for book in books])

async def async_search_by_book_name(book_name: str):
    async with SessionLocal() as db:
        books = await search_by_book_name(db, book_name)
    return "\n\n".join([f"Title: {book['title']}, Author: {book['author']}, Summary: {book['summary']}" for book in books])

async def async_search_by_summary(summary_text: str):
    return await search_by_summary(summary_text)

# Modify the search functions to properly handle async operations
# def search_by_author_sync(author_name: str):
#     async def async_search():
#         async with SessionLocal() as db:
#             books = await search_by_author(db, author_name)
#             return "\n\n".join([
#                 f"Title: {book['title']}, Author: {book['author']}, Summary: {book['summary']}"
#                 for book in books
#             ])
#     return run_async(async_search())
#
# def search_by_book_name_sync(book_name: str):
#     async def async_search():
#         async with SessionLocal() as db:
#             books = await search_by_book_name(db, book_name)
#             return "\n\n".join([
#                 f"Title: {book['title']}, Author: {book['author']}, Summary: {book['summary']}"
#                 for book in books
#             ])
#     return run_async(async_search())

# def search_by_summary_sync(summary_text: str):
#     async def async_search():
#         results = await search_by_summary(summary_text)
#         return results
#     return run_async(async_search())

# # Create synchronized search functions
# search_by_author_sync = create_sync_search_handler(search_books_by_author)
# search_by_book_name_sync = create_sync_search_handler(search_books_by_name)


# ---- Gradio UI Functions ----

def add_book_ui(title, author, genre, year_published, summary):
    response = requests.post(f"{BASE_URL}/books", json={
        "title": title,
        "author": author,
        "genre": genre,
        "year_published": int(year_published),
        "summary": summary
    })
    if response.status_code == 200:
        return f"Book '{title}' added successfully!"
    else:
        return f"Failed to add book: {response.text}"

def view_book_ui(book_id):
    response = requests.get(f"{BASE_URL}/books/{book_id}")
    if response.status_code == 200:
        book = response.json()
        return f"Title: {book['title']}\nAuthor: {book['author']}\nGenre: {book['genre']}\nYear Published: {book['year_published']}\nSummary: {book['summary']}"
    else:
        return "Book not found."


# Create synchronized search functions
search_by_author_sync = create_sync_search_handler(search_books_by_author)
search_by_book_name_sync = create_sync_search_handler(search_books_by_name)

# Special handler for summary search since it doesn't use the database session
def search_by_summary_sync(summary_text: str):
    async def handler():
        try:
            return await search_by_summary(summary_text)
        except Exception as e:
            return f"Error: {str(e)}"

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(handler())
    finally:
        loop.close()


# Define async function for chatbot interaction
async def send_message_to_chatbot(message, history, session_id=None):
    # Generate a session ID if one is not provided
    if not session_id:
        session_id = str(uuid.uuid4())

    # Call the chat function and get response
    response = await rag_instance.chat(message, session_id)
    if response:
        history.append((message, response))
        return history, session_id
    else:
        history.append((message, "Failed to fetch response from chatbot"))
        return history, session_id


# Define a sync wrapper for sending a message to the chatbot
def wrap_chat_function(message, history, session_id=None):
    return asyncio.run(send_message_to_chatbot(message, history, session_id))

# Launch Gradio asynchronously
# Gradio app setup
def create_gradio_app():

    #await index_books()  # Ensure ChromaDB is populated

    # Gradio UI
    with gr.Blocks() as app:
        gr.Markdown("# Book & Review Management")

        # Chat Tab
        with gr.Tabs():
            with gr.Tab("Chatbot"):
                with gr.Column():
                    gr.Markdown("### Chat with Our Book Bot")
                    chatbot = gr.Chatbot()
                    input_message = gr.Textbox(label="Your Message")
                    session_id = gr.State()
                    send_button = gr.Button("Send")

                    # Bind the button click to the chatbot function with session management
                    send_button.click(
                        wrap_chat_function,
                        inputs=[input_message, chatbot, session_id],
                        outputs=[chatbot, session_id]
                    )

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

                    # New "Search" Tab
            with gr.Tab("Search"):
                with gr.Row():
                    # Search by Book ID
                    with gr.Column():
                        gr.Markdown("### Search by Book ID")
                        book_id_search = gr.Number(label="Book ID")
                        search_by_id_button = gr.Button("Search by ID", size="small")
                        book_info_by_id = gr.Textbox(label="Book Information", lines=5)
                        search_by_id_button.click(view_book_ui, [book_id_search], book_info_by_id)


                    # Search by ISBN
                    with gr.Column():
                        gr.Markdown("### Search by ISBN")
                        isbn_search = gr.Textbox(label="ISBN")
                        search_by_isbn_button = gr.Button("Search by ISBN", size="small")
                        isbn_result = gr.Textbox(label="Book Information", lines=5)
                        search_by_isbn_button.click(lambda x: "Feature not yet implemented", [isbn_search],
                                                    isbn_result)

                    # Search by Author Name
                    with gr.Column():
                        gr.Markdown("### Search by Author Name")
                        author_search = gr.Textbox(
                            label="Author Name",
                            placeholder="Enter author name..."
                        )
                        search_by_author_button = gr.Button("Search by Author", variant= "primary", size="small")
                        author_result = gr.Textbox(label="Books Found", lines=5, show_label=True)
                        #search_by_author_button.click(async_search_by_author, [author_search], author_result)
                        # Use the sync wrapper
                        search_by_author_button.click(
                            fn = search_by_author_sync,
                            inputs=[author_search],
                            outputs=author_result
                        )

                with gr.Row():
                    # Search by Book Name
                    with gr.Column():
                        gr.Markdown("### Search by Book Name")
                        book_name_search = gr.Textbox(
                            label="Book Name",
                            placeholder="Enter book title..."
                        )
                        search_by_name_button = gr.Button("Search by Book Name", variant= "primary", size="small")
                        book_name_result = gr.Textbox(label="Books Found", lines=5, show_label=True)
                        #search_by_name_button.click(async_search_by_book_name, [book_name_search], book_name_result)
                        # Use the sync wrapper
                        search_by_name_button.click(
                            fn = search_by_book_name_sync,
                            inputs=[book_name_search],
                            outputs=book_name_result
                        )



                    # Search by Summary (Embedding Search)
                    with gr.Column():
                        gr.Markdown("### Search by Summary")
                        summary_search = gr.Textbox(label="Summary Keywords")
                        search_by_summary_button = gr.Button("Search by Summary", size="small")
                        summary_search_result = gr.Textbox(label="Search Results", lines=5)
                        #search_by_summary_button.click(async_search_by_summary, [summary_search], summary_search_result)
                        # Use the sync wrapper
                        search_by_summary_button.click(
                            search_by_summary_sync,
                            inputs=[summary_search],
                            outputs=summary_search_result
                        )



    return app

# Initialize the database and launch the app
async def init_db():
    try:
        await index_books()
    except Exception as e:
        print(f"Error initializing database: {e}")

def main():
    # Initialize the database in a new event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(init_db())
    finally:
        loop.close()

    # Create and launch the Gradio app
    app = create_gradio_app()
    app.launch()

if __name__ == "__main__":
    main()