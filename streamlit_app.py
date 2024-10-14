import streamlit as st
import requests

BASE_URL = "http://localhost:8000"

st.title("Book Review App")

# Helper function to fetch books
def fetch_books():
    response = requests.get(f"{BASE_URL}/books")
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error fetching books: {response.status_code}")
        return []

# Tabbed interface for different operations
tab1, tab2, tab3, tab4 = st.tabs(["Add Book", "View Books", "Update Book", "Delete Book"])

# Tab 1: Add a new book
with tab1:
    st.header("Add a new book")
    book_title = st.text_input("Title")
    book_author = st.text_input("Author")
    book_genre = st.text_input("Genre")
    year_published = st.number_input("Year Published", min_value=1000, max_value=9999, value=2022)
    book_summary = st.text_area("Summary")

    if st.button("Submit"):
        response = requests.post(f"{BASE_URL}/books", json={
            "title": book_title,
            "author": book_author,
            "genre": book_genre,
            "year_published": year_published,
            "summary": book_summary
        })
        if response.status_code == 200:
            st.success(f"Book '{book_title}' added successfully!")
        else:
            st.error(f"Error: {response.status_code}")

# Tab 2: View all books
with tab2:
    st.header("View Books")
    books = fetch_books()
    if books:
        for book in books:
            st.subheader(f"{book['title']} by {book['author']}")
            st.write(f"Genre: {book['genre']}, Year: {book['year_published']}")
            st.write(f"Summary: {book['summary']}")

# Tab 3: Update an existing book
with tab3:
    st.header("Update a Book")
    books = fetch_books()
    book_titles = [book["title"] for book in books]

    if books:
        selected_book = st.selectbox("Select a book to update", book_titles)
        if selected_book:
            book_to_update = next(book for book in books if book["title"] == selected_book)
            book_id = book_to_update["id"]
            updated_title = st.text_input("New Title", book_to_update["title"])
            updated_author = st.text_input("New Author", book_to_update["author"])
            updated_genre = st.text_input("New Genre", book_to_update["genre"])
            updated_year = st.number_input("New Year Published", min_value=1000, max_value=9999, value=book_to_update["year_published"])
            updated_summary = st.text_area("New Summary", book_to_update["summary"])

            if st.button("Update Book"):
                response = requests.put(f"{BASE_URL}/books/{book_id}", json={
                    "title": updated_title,
                    "author": updated_author,
                    "genre": updated_genre,
                    "year_published": updated_year,
                    "summary": updated_summary
                })
                if response.status_code == 200:
                    st.success(f"Book '{updated_title}' updated successfully!")
                else:
                    st.error(f"Error updating book: {response.status_code}")

# Tab 4: Delete a book
with tab4:
    st.header("Delete a Book")
    books = fetch_books()
    book_titles = [book["title"] for book in books]

    if books:
        selected_book = st.selectbox("Select a book to delete", book_titles)
        if selected_book:
            book_to_delete = next(book for book in books if book["title"] == selected_book)
            book_id = book_to_delete["id"]

            if st.button(f"Delete {selected_book}"):
                response = requests.delete(f"{BASE_URL}/books/{book_id}")
                if response.status_code == 200:
                    st.success(f"Book '{selected_book}' deleted successfully!")
                else:
                    st.error(f"Error deleting book: {response.status_code}")

# Separate section for generating summaries
st.header("Generate Book Summary")
book_content = st.text_area("Enter book content to summarize")

if st.button("Generate Summary"):
    response = requests.post(f"{BASE_URL}/generate-summary", json={"book_content": book_content})
    if response.status_code == 200:
        summary = response.json().get("summary", "No summary available")
        st.write(f"Summary: {summary}")
    else:
        st.error(f"Error generating summary: {response.status_code}")
