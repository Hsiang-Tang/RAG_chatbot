# Chatbot with PDF Processing

This project is a chatbot that reads and analyzes a given PDF file using OpenAI's GPT-4o model. It supports both **CLI mode** and **API mode**.

---

## **📌 Prerequisites**
Before you begin, ensure you have the following installed:
- **Docker** (https://docs.docker.com/get-docker/)
- **Git** (https://git-scm.com/downloads)
- An **OpenAI API key** (https://platform.openai.com/)

---

## **🚀 Quick Start**
Follow these steps to set up and run the chatbot:

```bash
# 1️⃣ Clone the repository
git clone https://github.com/YOUR_GITHUB_USERNAME/YOUR_REPOSITORY.git
cd YOUR_REPOSITORY

# 2️⃣ Create and configure the .env file (Replace 'your-api-key-here' with your actual OpenAI API key)
echo "OPENAI_API_KEY=your-api-key-here" > .env

# 3️⃣ Build the Docker image
docker build -t chatbot-app .

# 4️⃣ Run the chatbot in CLI mode
docker run --rm -it --env-file .env chatbot-app

# 5️⃣ (Optional) Run the chatbot as an API service
docker run --rm -it -p 5000:5000 --env-file .env chatbot-app

# 6️⃣ (Optional) Test the API server using curl
curl -X POST "http://127.0.0.1:5000/chat" -H "Content-Type: application/json" -d '{"query": "Give me a summary of the NVIDIA 2024 Q3 financial report"}'

# 7️⃣ Stop the container (if running interactively)
CTRL + C
