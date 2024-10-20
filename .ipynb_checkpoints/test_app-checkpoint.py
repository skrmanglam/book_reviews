import asyncio
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from pydantic import BaseModel

# Database setup
DATABASE_URL = "postgresql+asyncpg://postgres:1234@localhost/test_db"
engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

# Test client setup
from httpx import AsyncClient
client = AsyncClient(app=app, base_url="http://test")

# Test setup and teardown
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def teardown_db():
    pass

# Test function for full CRUD and other operations
async def test_api_endpoints():
    passed_tests = 0
    failed_tests = 0

    try:
        # 1. POST /books: Add a new book
        print("Testing: POST /books")
        response = await client.post("/books", json={
            "title": "Test Book",
            "author": "Author One",
            "genre": "Fiction",
            "year_published": 2022,
            "summary": "A fascinating tale."
        })
        if response.status_code == 200:
            passed_tests += 1
            book_data = response.json()
            book_id = book_data['id']
            print(f"Created Book: {book_data}")
        else:
            failed_tests += 1
            print(f"Test Failed: POST /books, Status Code: {response.status_code}")

        # 2. GET /books: Retrieve all books
        print("Testing: GET /books")
        response = await client.get("/books")
        if response.status_code == 200:
            passed_tests += 1
            print(f"Books: {response.json()}")
        else:
            failed_tests += 1
            print(f"Test Failed: GET /books, Status Code: {response.status_code}")

        # 3. GET /books/<id>: Retrieve a specific book by its ID
        print(f"Testing: GET /books/{book_id}")
        response = await client.get(f"/books/{book_id}")
        if response.status_code == 200:
            passed_tests += 1
            print(f"Book {book_id}: {response.json()}")
        else:
            failed_tests += 1
            print(f"Test Failed: GET /books/{book_id}, Status Code: {response.status_code}")

        # 4. PUT /books/<id>: Update a book's information by its ID
        print(f"Testing: PUT /books/{book_id}")
        response = await client.put(f"/books/{book_id}", json={
            "title": "Updated Test Book",
            "author": "Author One",
            "genre": "Non-fiction",
            "year_published": 2023,
            "summary": "Updated fascinating tale."
        })
        if response.status_code == 200:
            passed_tests += 1
            print(f"Updated Book {book_id}: {response.json()}")
        else:
            failed_tests += 1
            print(f"Test Failed: PUT /books/{book_id}, Status Code: {response.status_code}")

        # Continue other tests (add reviews, etc.)...

    except Exception as e:
        failed_tests += 1
        print(f"Test Failed with Exception: {str(e)}")

    return passed_tests, failed_tests

# Run the tests in Jupyter directly
async def run_tests():
    passed_tests = 0
    failed_tests = 0
    try:
        await setup_db()
        passed, failed = await test_api_endpoints()
        passed_tests += passed
        failed_tests += failed
    finally:
        await teardown_db()
        await client.aclose()

    print("\n--- Test Summary ---")
    print(f"Tests Passed: {passed_tests}")
    print(f"Tests Failed: {failed_tests}")

# # Run in a standalone script or Jupyter
# await run_tests()
# Main entry point for running the tests in a standalone Python script
if __name__ == "__main__":
    # Use asyncio.run() to run the asynchronous test function
    asyncio.run(run_tests())