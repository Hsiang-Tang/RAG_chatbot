import os
import openai
import fitz  # PyMuPDF
import re
from langdetect import detect
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
    try:
        with fitz.open(pdf_path) as pdf:
            for page in pdf:
                text += page.get_text("text") + "\n"
    except Exception as e:
        print(f"Error loading PDF: {e}")
        return ""

    # Ensure UTF-8 encoding and remove non-standard characters
    text = text.encode("utf-8", "ignore").decode("utf-8")
    text = re.sub(r"[^\x20-\x7E\u4E00-\u9FFF\u3000-\u303F\uFF00-\uFFEF]+", "", text)  # Keep only valid text
    text = text.replace("\u00A0", " ").replace("\u200B", "").replace("\uFEFF", "")  # Remove invisible spaces

    return text.strip()

# Load PDF content
pdf_text = load_pdf(pdf_path)

# Detect the language of the input
def detect_language(text):
    """ Detects if the input is in English or Traditional Chinese. """
    try:
        lang = detect(text)
        return "zh" if lang == "zh-tw" or lang == "zh-cn" else "en"
    except:
        return "en"

# Search for specific keywords in the PDF
def search_pdf(query):
    """ Searches for specific keywords in the PDF content. """
    query = query.strip()
    lines = pdf_text.split("\n")
    results = [line.strip() for line in lines if query.lower() in line.lower()]
    return "\n".join(results[:5]) if results else "No relevant data found."

# Generate AI response using OpenAI API
def generate_response(query):
    """ Uses OpenAI API to process the PDF content and generate an answer. """
    query = query.strip()

    if not pdf_text:
        return "No data available."

    # Detect input language
    lang = detect_language(query)

    # Set prompt based on language
    if lang == "zh":
        system_prompt = "你是一個 AI 財務專家，請基於提供的 PDF 文件內容回答問題。請使用繁體中文回覆。"
    else:
        system_prompt = "You are an AI financial expert. Answer questions based on the provided PDF document."

    prompt = f"""
    以下是來自 PDF 文件的部分內容：
    {pdf_text[:4000]}  # OpenAI GPT-4o has a token limit, so only part of the text is provided.
    ---
    根據這份文件，請回答以下問題：
    問題: {query}
    答案:
    """

    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500 
        )
        return response.choices[0].message.content
    except openai.AuthenticationError:
        return "Authentication error: Invalid API key."
    except openai.OpenAIError as e:
        return f"OpenAI API error: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"

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
