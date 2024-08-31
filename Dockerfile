# Use an official lightweight Python image.
# Replace '3.8-slim' with the specific Python version you need.
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# The bot doesn't need to expose a port since it's not serving HTTP requests,
# but if your bot does for some reason (e.g., webhooks), uncomment the next line.
# EXPOSE 8000

# Command to run the bot
CMD ["python", "main.py"]