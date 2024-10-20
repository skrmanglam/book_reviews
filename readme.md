# 📚 Book Review and Summary App
This project is a Book Review and Summary Application built with FastAPI for the backend, Streamlit for the frontend, and Ollama integration for generating book summaries using a local AI model. The application allows users to:

Add, view, update, and delete books.
Submit and view reviews for each book.
Generate summaries for book content using AI.
# 🛠️ Features
CRUD Operations for Books: Add new books, retrieve book lists, update book details, and delete books.
Book Reviews: Submit reviews and ratings for books.
AI-Powered Summary: Generate book summaries using Ollama's llama3.1 model.
Frontend: A user-friendly interface using Streamlit to interact with the backend.

# 🖥️ Technologies Used
FastAPI: Backend API framework.
Streamlit: Frontend interface.
SQLAlchemy: ORM for managing PostgreSQL database.
PostgreSQL: Database for storing book and review data.
Ollama: AI model for generating book summaries.
Docker: Containerization for easy deployment.

# 🚀 Setup Instructions
Prerequisites
Make sure you have the following installed:

Python 3.9+
PostgreSQL (with a database created for the app, e.g., book_review)
Docker (optional, for running in a containerized environment)
Git (for cloning the repository)
1. Clone the Repository
bash
Copy code
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
cd YOUR_REPOSITORY
2. Install Python Dependencies
Create a virtual environment and install the required Python packages:

bash
Copy code
#Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

#Install dependencies
pip install -r requirements.txt
3. Set Up PostgreSQL Database
Ensure PostgreSQL is installed and running.
Create a database named book_review (or any name you'd like) and set up your connection in backend/database.py.
sql
Copy code
CREATE DATABASE book_review;
Update the DATABASE_URL in backend/database.py if necessary:

python
Copy code
DATABASE_URL = "postgresql+asyncpg://postgres:1234@localhost/book_review"
4. Run the FastAPI App
Start the FastAPI app using Uvicorn:

bash
Copy code
uvicorn main:app --reload
The API will be available at: http://localhost:8000.

5. Run the Streamlit Frontend
To launch the Streamlit frontend, run:

bash
Copy code
streamlit run streamlit_app.py
The frontend will be available at: http://localhost:8501.

6. Optional: Running with Docker
To containerize the application using Docker:

Build the Docker image:
bash
Copy code
docker build -t fastapi-app .
Run the Docker container:
bash
Copy code
docker run -d -p 8000:8000 fastapi-app
Now, the FastAPI app should be accessible at http://localhost:8000.

# 🧪 Testing the Application
To run the unit tests, use pytest:

bash
Copy code
pytest test_app.py
This will execute the test suite to ensure everything is working correctly.

# 📝 API Endpoints
POST /books: Add a new book.
GET /books: Retrieve a list of all books.
GET /books/{book_id}: Retrieve a specific book by its ID.
PUT /books/{book_id}: Update a book's details.
DELETE /books/{book_id}: Delete a book by its ID.
POST /books/{book_id}/reviews: Add a review to a book.
POST /generate-summary: Generate a summary of book content using Ollama's AI model.
# 🎉 Features and Future Plans
Full support for CRUD operations on books and reviews.
Real-time summary generation using AI models.
Future enhancements:
Add user authentication and roles.
Expand support for more complex review aggregation and analysis.
Enhanced AI-based book recommendations.
# 📄 License
This project is licensed under the MIT License. See the LICENSE file for more details.

# 💡 Additional Notes
Frontend: The user-facing interface built with Streamlit allows users to add, view, update, and delete books, and generate summaries.
Backend: FastAPI serves as the backend API to handle database operations, book reviews, and interactions with the AI-powered summarization model.
Feel free to customize the project for your own use case, and contributions are welcome!
