# Use the official Python base image
FROM python:3.11

# Set the working directory
WORKDIR /app

# Copy the project files into the container
COPY . /app

# Install required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Define an environment variable (API key should be provided via .env)
ENV OPENAI_API_KEY=""

# Run the chatbot in CLI mode
CMD ["python", "chatbot.py"]
