import json
import os

SESSION_FILE = "session.json"

class SessionManager:
    def __init__(self):
        self.session_data = self.load_session()

    def save_session(self, user_id, session_token):
        """Save session details to a file."""
        self.session_data = {
            "user_id": user_id,
            "session_token": session_token
        }
        with open(SESSION_FILE, "w") as f:
            json.dump(self.session_data, f)
        print("Session saved.")

    def load_session(self):
        """Load session details from the file."""
        if os.path.exists(SESSION_FILE):
            with open(SESSION_FILE, "r") as f:
                return json.load(f)
        return None

    def get_user_id(self):
        """Retrieve user_id from the session data."""
        if self.session_data:
            return self.session_data.get("user_id")
        return None

    def get_session_token(self):
        """Retrieve session token from the session data."""
        if self.session_data:
            return self.session_data.get("session_token")
        return None

    def clear_session(self):
        """Clear the session data and delete the session file."""
        self.session_data = None
        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)
        print("Session cleared.")
