FROM python:3.11-slim

WORKDIR /app

# Copy requirement parameters
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project folders over
COPY . .

# Expose port 7860 (Hugging Face standard port requirement)
EXPOSE 7860

# Run the app binding it to global traffic on port 7860
CMD ["python", "Backend/app.py"]