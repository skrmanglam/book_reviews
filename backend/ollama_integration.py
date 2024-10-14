import ollama

async def generate_summary(book_content: str):
    response = ollama.chat(
        model="llama3.1",
        messages=[
            {
                "role": "user",
                "content": f"Summarize the following book content: {book_content}",
            },
        ],
    )
    return response.get("message", {}).get("content", "No summary available")
