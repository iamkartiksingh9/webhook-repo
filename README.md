# Webhook Receiver Repo

This project implements the `webhook-repo` for the TechStax assessment. It receives Github Actions webhooks, stores them in MongoDB, and displays them in a live-updating UI.

## Prerequisites
- Python 3.x
- MongoDB (Running locally or a URI)

## Installation

1. Create a virtual environment (optional but recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure Environment:
   - The app defaults to `mongodb://localhost:27017/`.
   - If using a cloud instance, create a `.env` file:
     ```
     MONGO_URI=mongodb+srv://<user>:<password>@cluster.mongodb.net/?retryWrites=true&w=majority
     ```

## Running the Application

1. Start MongoDB (if local).
2. Run the Flask app:
   ```bash
   python3 app.py
   ```
3. Open `http://localhost:5000` in your browser.

## Testing with Simulator
Since connecting a real Github repo to localhost requires tunneling (Ngrok), a simulator script is provided.

1. Ensure the app is running in one terminal.
2. In a second terminal, run:
   ```bash
   python3 simulate_webhook.py
   ```
3. Watch the UI at `http://localhost:5000` update automatically.

## Project Structure
- `app.py`: Flask backend & MongoDB logic.
- `static/`: CSS and JS for the UI.
- `templates/`: HTML files.
- `simulate_webhook.py`: Test script to send dummy Push/PR/Merge events.
