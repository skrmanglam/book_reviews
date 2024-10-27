import gradio as gr
import asyncio
from backend.ollama_integration import generate_summary, index_books, search_by_summary
import nest_asyncio

# Apply nest_asyncio to allow nested async loops
nest_asyncio.apply()

# Launch Gradio asynchronously
async def run_gradio_app():
    await index_books()  # Ensure ChromaDB is populated

    # Gradio UI
    with gr.Blocks() as app:
        gr.Markdown("# Book & Review Management")

        with gr.Tabs():
            with gr.Tab("Search"):
                with gr.Row():
                    # Search by Summary (Embedding Search)
                    summary_search = gr.Textbox(label="Search by Summary")
                    search_by_summary_button = gr.Button("Search by Summary")
                    summary_search_result = gr.Textbox(label="Search Results", lines=10)
                    search_by_summary_button.click(search_by_summary, [summary_search], summary_search_result)

    app.launch()

if __name__ == "__main__":
    asyncio.run(run_gradio_app())

