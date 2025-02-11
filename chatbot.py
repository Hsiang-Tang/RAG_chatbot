import os
import openai
import fitz  # PyMuPDF
import re
from dotenv import load_dotenv
from flask import Flask, request, jsonify

# Load environment variables from .env file
load_dotenv()

# Retrieve OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is missing. Please set it in the .env file.")

# Initialize Flask application
app = Flask(__name__)

# Set PDF file path (ensure the path is correct in the Docker environment)
pdf_path = "NV.pdf"

# Read and clean PDF content
def load_pdf(pdf_path):
    """ Reads the PDF and removes non-visible characters. """
    text = ""
    with fitz.open(pdf_path) as pdf:
        for page in pdf:
            text += page.get_text("text") + "\n"

    # Ensure UTF-8 encoding and remove non-ASCII characters
    text = text.encode("utf-8", "ignore").decode("utf-8")
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)

    return text.strip()

# Load PDF content
pdf_text = load_pdf(pdf_path)

# Search for specific keywords in the PDF
def search_pdf(query):
    """ Searches for specific keywords in the PDF content. """
    lines = pdf_text.split("\n")
    results = [line.strip() for line in lines if query.lower() in line.lower()]
    return "\n".join(results[:5]) if results else "No relevant data found."

# Generate AI response using OpenAI API
def generate_response(query):
    """ Uses OpenAI API to process the PDF content and generate an answer. """
    if not pdf_text.strip():
        print("PDF content is empty. Unable to generate a response.")
        return "No data available."

    prompt = f"""
    The following is extracted text from a PDF document:
    {pdf_text[:4000]}  # OpenAI GPT-4o has a token limit, so only part of the text is provided.
    ---
    Based on this document, please answer the following question:
    Question: {query}
    Answer:
    """

    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an AI financial expert. Answer questions based on the provided PDF document."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500 
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Failed to generate a response: {e}"

# API endpoint for chatbot interaction
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    query = data.get("query", "").strip()
    answer = generate_response(query)
    return jsonify({"query": query, "response": answer})

# Command-line interface mode
def interactive_chat():
    while True:
        query = input("Enter your question: ").strip()
        if query.lower() in ["exit", "quit"]:
            break
        answer = generate_response(query)
        print(f"Response: {answer}\n")

# Run in CLI mode
if __name__ == "__main__":
    interactive_chat()
