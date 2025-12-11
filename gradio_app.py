import gradio as gr
from rag_qa_ollama import build_chain

def ask_question(message, history):
    """
    Callback for Gradio ChatInterface.
    message: The current user message.
    history: List of [user_msg, bot_msg] from previous turns.
    """
    try:
        chain = build_chain()
        response = chain.invoke(message)
        return response.content
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    # Create a ChatInterface
    demo = gr.ChatInterface(
        fn=ask_question,
        title="Migration & Refugee Law Assistant",
        description="Ask questions about migration and refugee laws. The assistant uses a RAG system with Ollama (Qwen3).",
        examples=[
            "What is the definition of a refugee?",
            "How do I apply for asylum?",
            "What are the grounds for persecution?",
        ],
    )
    
    # Launch the app
    # server_name="0.0.0.0" allows access from other machines if needed
    # Let Gradio find an available port automatically
    demo.launch(server_name="127.0.0.1", share=False)

if __name__ == "__main__":
    main()
