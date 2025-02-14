import os
import openai
import fitz  # PyMuPDF
import faiss
import numpy as np
import re
from langdetect import detect
from dotenv import load_dotenv
from flask import Flask, request, jsonify

# 讀取環境變數
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("請設定 OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

# PDF 檔案路徑
PDF_PATH = "NV.pdf"

# 查詢擴展對應表
QUERY_EXPANSION_MAP = {
    "淨利": ["Net Income", "Profit", "Earnings"],
    "營收": ["Revenue", "Total Revenue"],
    "毛利率": ["Gross Margin", "Gross Profit"],
    "研發支出": ["R&D Expenses", "Research and Development"],
    "現金及等值現金資產": ["Cash and Cash Equivalents"],
    "股票回購": ["Stock Buyback", "Repurchase"],
    "客戶": ["Major Customers", "Clients"]
}

# 清理文本
def clean_text(text):
    """ 清理特殊字符，確保文本格式正常 """
    text = text.replace("\u00A0", " ").replace("\u200B", "").replace("\uFEFF", "")
    text = re.sub(r"[^\x20-\x7E\u4E00-\u9FFF\u3000-\u303F\uFF00-\uFFEF]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

# 讀取 PDF 並分段
def load_pdf_and_chunk(pdf_path, chunk_size=1000):
    """ 讀取 PDF，清理並分割內容為段落 """
    text = ""
    with fitz.open(pdf_path) as pdf:
        for page in pdf:
            text += clean_text(page.get_text("text")) + "\n"

    # 根據換行或句點分割
    paragraphs = re.split(r"(?:(?:\n\s*){2,}|(?<=\.\s))", text)
    chunks = []
    buffer = ""

    for para in paragraphs:
        if len(buffer) + len(para) < chunk_size:
            buffer += " " + para
        else:
            chunks.append(buffer.strip())
            buffer = para

    if buffer:
        chunks.append(buffer.strip())

    return chunks

# 生成向量嵌入 (批量)
def generate_batch_embeddings(texts):
    """ 批量處理詞嵌入，加快索引建立 """
    response = openai.embeddings.create(
        model="text-embedding-3-small",
        input=texts
    )
    return np.array([r.embedding for r in response.data], dtype=np.float32)

# 建立 FAISS 向量索引
def build_faiss_index(chunks):
    """ 建立 FAISS 向量索引，提升檢索速度 """
    dimension = 1536  
    index = faiss.IndexFlatL2(dimension)

    batch_size = 5
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]
        embeddings = generate_batch_embeddings(batch)
        index.add(embeddings)

    return index, chunks

# 擴展查詢，提高關鍵詞匹配度
def expand_query(query):
    """ 查詢擴展，提高檢索準確度 """
    for key, values in QUERY_EXPANSION_MAP.items():
        if key in query:
            query += " " + " ".join(values)
    return query

# 查詢 FAISS 向量資料庫
def search_faiss(query, top_k=3):
    """ 查詢 FAISS，找出最相關的內容 """
    expanded_query = expand_query(query)
    query_embedding = generate_batch_embeddings([expanded_query]).reshape(1, -1)
    _, idxs = faiss_index.search(query_embedding, top_k)
    return [chunk_texts[i] for i in idxs[0] if i < len(chunk_texts)]

# 使用 GPT 回應
def query_gpt(query, context):
    """ 使用 GPT 生成回答，並參考 FAISS 提供的內文 """
    prompt = f"""
    根據以下提供的財報內容，回答用戶的問題：
    
    財報內容：
    {context}
    
    問題：
    {query}

    回答：
    """

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500
    )
    
    return response.choices[0].message.content.strip()

# 查詢處理流程
def get_answer(query):
    """ 先檢索 FAISS，再使用 GPT 生成答案 """
    results = search_faiss(query)
    
    if results:
        return query_gpt(query, "\n\n".join(results))
    
    return "查無相關資料，建議您查閱完整財報文件。"

# 初始化 Flask
app = Flask(__name__)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    query = data.get("query", "").strip()
    answer = get_answer(query)
    return jsonify({"query": query, "response": answer})

# CLI 模式
def interactive_chat():
    print("===== NVIDIA 財報 Chatbot =====")
    while True:
        query = input("請輸入你的問題: ").strip()
        if query.lower() in ["exit", "quit"]:
            break
        answer = get_answer(query)
        print(f"回答:\n{answer}\n")

# 載入 PDF 並建立 FAISS
chunks = load_pdf_and_chunk(PDF_PATH)
faiss_index, chunk_texts = build_faiss_index(chunks)

if __name__ == "__main__":
    interactive_chat()
