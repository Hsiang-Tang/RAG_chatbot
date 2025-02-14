# NVIDIA 財報查詢 Chatbot

本專案是一個基於 **RAG (檢索增強生成)** 技術的財報查詢 Chatbot，使用 **OpenAI GPT-4o** 和 **FAISS 向量資料庫** 來檢索 PDF 財報內容，並提供準確的回答。當 PDF 內部無法找到答案時，系統會自動使用 **SerpAPI** 進行網路搜尋。

## 主要功能
✅ **載入 PDF 財報並建立向量資料庫（FAISS）**  
✅ **使用 OpenAI `text-embedding-3-small` 產生詞嵌入**  
✅ **透過 FAISS 檢索最相關的財報內容**  
✅ **使用 GPT-4o 根據檢索結果生成回答**  
✅ **當財報內找不到資料時，自動使用 Google 搜尋 (SerpAPI)**  

---

## 1️⃣ 環境需求

### **Linux (WSL) / MacOS / Docker**

⚠ **注意：若在 MacOS 上運行，請確保沒有安裝 NVIDIA GPU 相關套件，避免與 CUDA 衝突！**

| 需求 | 版本 |
|------|------|
| **Python** | `>=3.8` |
| **FAISS** | `faiss-cpu` (MacOS 適用) |
| **FAISS (GPU 版)** | `faiss-gpu` (僅適用於 Linux，MacOS 請勿安裝) |
| **OpenAI API Key** | 需要 GPT-4o API 權限 |
| **SerpAPI Key** | (可選) 用於網路搜尋 |
| **Docker (可選)** | `>=20.10` |

---

## 2️⃣ 安裝步驟

### **📌 Linux (WSL) 安裝**
**1️⃣ 建立 Python 環境**
```sh
sudo apt update && sudo apt install python3 python3-pip -y
python3 -m venv env
source env/bin/activate
```

**2️⃣ 安裝依賴**
```sh
pip install -r requirements-linux.txt
```

**3️⃣ 設定 `.env` 環境變數**
```sh
echo "OPENAI_API_KEY=你的OpenAI API Key" >> .env
echo "SERP_API_KEY=你的SerpAPI Key（可選）" >> .env
```

**4️⃣ 啟動 Chatbot**
```sh
python chatbot.py
```

---

### **📌 MacOS 安裝**
**1️⃣ 安裝 Python**
```sh
brew install python
python3 -m venv env
source env/bin/activate
```

**2️⃣ 安裝依賴（MacOS 需使用 CPU 版 FAISS）**
```sh
pip install -r requirements-macos.txt
```

⚠ **請勿在 MacOS 安裝 `faiss-gpu`，僅需 `faiss-cpu`**

**3️⃣ 設定 `.env` 環境變數**
```sh
echo "OPENAI_API_KEY=你的OpenAI API Key" >> .env
echo "SERP_API_KEY=你的SerpAPI Key（可選）" >> .env
```

**4️⃣ 啟動 Chatbot**
```sh
python chatbot.py
```

---

### **📌 Docker 安裝**
**1️⃣ 檢查 Docker 是否安裝**
```sh
docker --version
```
如果未安裝，請參考 [官方安裝指南](https://docs.docker.com/get-docker/)。

**2️⃣ 構建 Docker Image**
```sh
docker build -t nvidia-chatbot .
```

**3️⃣ 運行容器**
```sh
docker run --rm -it --env OPENAI_API_KEY=你的OpenAI_API_Key --env SERP_API_KEY=你的SerpAPI_Key nvidia-chatbot
```

---

## 3️⃣ 依賴安裝 (`requirements`)

**🔹 Linux (WSL) 專用 (`requirements-linux.txt`)**
```
openai
pypdf2
faiss-gpu
langdetect
flask
python-dotenv
numpy
```

**🔹 MacOS 專用 (`requirements-macos.txt`)**
```
openai
pypdf2
faiss-cpu
langdetect
flask
python-dotenv
numpy
```

---

## 4️⃣ Dockerfile

```dockerfile
# 使用 Python 3.10 作為基礎
FROM python:3.10-slim

# 設定工作目錄
WORKDIR /app

# 複製專案文件
COPY . /app

# 安裝必要的套件
RUN pip install --no-cache-dir -r requirements-linux.txt

# 設定環境變數
ENV OPENAI_API_KEY=""
ENV SERP_API_KEY=""

# 指定啟動指令
CMD ["python", "chatbot.py"]
```

---

## 5️⃣ 使用方式

### **📌 CLI 模式**
啟動後，直接輸入財報相關問題：
```sh
python chatbot.py
```
示例：
```
請輸入你的問題: NVIDIA 在 2024 Q4 的營收是多少？
回答: 總營收為 $35,082 百萬美元 (約 350.82 億美元)
```

---

