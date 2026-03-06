# 1. Use an official, lightweight Python image
FROM python:3.12-slim

# 2. Prevent Python from writing .pyc files and buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Set the working directory
WORKDIR /app

# 4. Copy ONLY requirements first (Best Practice for Docker cache)
COPY requirements.txt .

# 5. Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy the rest of the application code
COPY . .

# 7. Security Best Practice: Create a non-root user and switch to it
RUN adduser --disabled-password --gecos '' metronuser
USER metronuser

# 8. Expose the API port
EXPOSE 8000

# 9. Start the server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]