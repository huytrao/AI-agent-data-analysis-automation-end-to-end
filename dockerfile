FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application
COPY . .

# Expose port for Streamlit
EXPOSE 8501

# Run the Streamlit app
ENTRYPOINT ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]