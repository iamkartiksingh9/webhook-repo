import os
from datetime import datetime, timezone
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# MongoDB Configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = "techstax_db"
COLLECTION_NAME = "events"

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    # Check connection
    client.server_info()
    print(f"Connected to MongoDB at {MONGO_URI}")
except Exception as e:
    print(f"MongoDB not available: {e}")
    print("Falling back to IN-MEMORY storage for demonstration.")
    
    # Simple in-memory mock for demonstration purposes
    class InMemoryCollection:
        def __init__(self):
            self.data = []
        def insert_one(self, doc):
            self.data.append(doc)
        def find(self, query, projection=None):
            return self
        def sort(self, key, direction):
            # rudimentary sort by timestamp or insertion order
            return self
        def limit(self, n):
            return self.data[-n:][::-1] # return last n reversed
            
    collection = InMemoryCollection()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/webhook', methods=['POST'])
def webhook_receiver():
    data = request.json
    if not data:
        return jsonify({"msg": "No data received"}), 400

    event_type = request.headers.get('X-GitHub-Event')
    
    # Initialize document structure
    doc = {
        "request_id": "",
        "author": "",
        "action": "",
        "from_branch": "",
        "to_branch": "",
        "timestamp": ""
    }

    try:
        if event_type == 'push':
            doc['action'] = "PUSH"
            doc['request_id'] = data.get('after', '')
            doc['author'] = data.get('pusher', {}).get('name', 'unknown') or data.get('sender', {}).get('login', 'unknown')
            
            # Ref format is usually 'refs/heads/branch_name'
            ref = data.get('ref', '')
            branch_name = ref.replace('refs/heads/', '')
            doc['to_branch'] = branch_name
            doc['from_branch'] = "" # Push doesn't strictly have a 'from' in this context usually, or it's local. App logic treats 'to_branch' as the target.
            
            # Timestamp from head commit or current time
            head_commit = data.get('head_commit')
            if head_commit and 'timestamp' in head_commit:
                doc['timestamp'] = _format_dt(head_commit['timestamp'])
            else:
                doc['timestamp'] = _get_current_utc_str()

        elif event_type == 'pull_request':
            action = data.get('action')
            pr = data.get('pull_request', {})
            
            if action == 'closed' and pr.get('merged') is True:
                doc['action'] = "MERGE"
            elif action in ['opened', 'reopened', 'synchronize']:
                doc['action'] = "PULL_REQUEST"
            else:
                return jsonify({"msg": "Ignored PR action"}), 200

            doc['request_id'] = str(pr.get('id', ''))
            doc['author'] = pr.get('user', {}).get('login', 'unknown')
            doc['from_branch'] = pr.get('head', {}).get('ref', '')
            doc['to_branch'] = pr.get('base', {}).get('ref', '')
            doc['timestamp'] = _format_dt(pr.get('updated_at') or pr.get('created_at'))

        else:
             return jsonify({"msg": "Event type not handled"}), 200

        # Save to MongoDB
        if collection is not None:
            collection.insert_one(doc)
            # Remove _id before printing or returning if needed, but not strictly necessary here
            print(f"Stored event: {doc['action']} by {doc['author']}")
        else:
            print("MongoDB not available, skipping insert.")

        return jsonify({"msg": "Event received"}), 200

    except Exception as e:
        print(f"Error processing webhook: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/events', methods=['GET'])
def get_events():
    if collection is None:
        return jsonify([])
    
    # Fetch latest 10 events, sorted by _id (approx timestamp) descending
    # Or strict timestamp if we can parse it, but _id is natural order usually.
    # The requirement says "latest changes".
    events = list(collection.find({}, {'_id': 0}).sort('_id', -1).limit(20))
    return jsonify(events)

def _format_dt(iso_str):
    # Ensure standard format (e.g., "1st April 2021 - 9:30 PM UTC")
    # The prompt requests a specific format like "1st April 2021 - 9:30 PM UTC"
    # We will try to parse input and reformat.
    if not iso_str:
        return _get_current_utc_str()
    
    try:
        # Github sends ISO 8601
        dt = datetime.fromisoformat(iso_str.replace('Z', '+00:00'))
    except ValueError:
        dt = datetime.now(timezone.utc)
        
    return _custom_strftime(dt)

def _get_current_utc_str():
    dt = datetime.now(timezone.utc)
    return _custom_strftime(dt)

def _custom_strftime(dt):
    # Format: "1st April 2021 - 9:30 PM UTC"
    suffix = "th" if 11 <= dt.day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(dt.day % 10, "th")
    date_str = dt.strftime(f"%-d{suffix} %B %Y - %-I:%M %p UTC")
    return date_str

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, port=port)
