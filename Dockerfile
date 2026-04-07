# 1. Use a lightweight, official Python image as the foundation
FROM python:3.11-slim

# 2. Set the working directory inside the container to /app
WORKDIR /app

# 3. Copy only the requirements first (this makes rebuilding faster)
COPY requirements.txt .

# 4. Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of your project files into the container
# Note: We will handle the .env file separately for security!
COPY . .

# 6. Set the default command to run your interactive script
# We use the exact same command you used in your terminal
CMD ["python", "-m", "main"]