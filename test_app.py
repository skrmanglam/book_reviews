from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_create_book():
    response = client.post("/books", json={
        "title": "Sample Book",
        "author": "John Doe",
        "genre": "Fiction",
        "year_published": 2022,
        "summary": "A sample book"
    })
    assert response.status_code == 200
    assert response.json()["title"] == "Sample Book"

def test_get_books():
    # Create a book first
    client.post("/books", json={
        "title": "Sample Book",
        "author": "John Doe",
        "genre": "Fiction",
        "year_published": 2022,
        "summary": "A sample book"
    })
    
    # Retrieve all books
    response = client.get("/books")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["title"] == "Sample Book"

def test_generate_summary():
    response = client.post("/generate-summary", json={
        "book_content": "a brief history of time"
    })
    assert response.status_code == 200
    assert "summary" in response.json()
