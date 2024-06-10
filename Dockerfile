# Use the official Python image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Set environment variables for Bybit API keys
ENV BYBIT_API_KEY=
ENV BYBIT_API_SECRET=

# Run the bot
CMD ["python", "src/bot.py"]
