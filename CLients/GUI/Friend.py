import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import socket
import json
from session_manager import SessionManager

# Constants
HOST = "127.0.0.1"
FRIEND_SERVER_PORT = 6004
BUFFER_SIZE = 4096
ENCODING = 'utf-8'

# Set the global appearance mode for a light theme
ctk.set_appearance_mode("light") 

# Initialize session manager to retrieve user ID
session_manager = SessionManager()
user_id = session_manager.get_user_id()

class FriendApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Friends List")
        self.root.geometry("600x400")
        
        # Heading
        heading_label = ctk.CTkLabel(self.root, text="Friends List", font=("Arial", 24), text_color="#333333")
        heading_label.pack(pady=10)

        # Frame to contain friend list
        self.friend_list_frame = ctk.CTkFrame(self.root, fg_color="white")  # Light frame color
        self.friend_list_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Load friends on startup
        self.load_friends()

    def load_friends(self):
        """Fetch and display friends from the server."""
        for widget in self.friend_list_frame.winfo_children():
            widget.destroy()  # Clear frame
        friends = self.get_friend_list()
        if friends:
            for friend in friends:
                self.display_friend(friend)
        else:
            no_friends_label = ctk.CTkLabel(self.friend_list_frame, text="No friends found.", font=("Arial", 14), text_color="#666666")
            no_friends_label.pack(pady=10)

    def get_friend_list(self):
        """Request friend list from the server."""
        if user_id is None:
            messagebox.showerror("Error", "User ID not found. Please log in first.")
            return None

        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((HOST, FRIEND_SERVER_PORT))
            request_data = json.dumps({
                "request_type": "GET_FRIEND_LIST",
                "user_id": user_id
            })
            client.sendall(request_data.encode(ENCODING))

            response = client.recv(BUFFER_SIZE).decode(ENCODING)
            response_data = json.loads(response)
            client.close()

            if response_data.get("status") == "SUCCESS":
                return response_data.get("friends", [])
            else:
                messagebox.showerror("Error", response_data.get("message", "Failed to retrieve friends."))
                return None
        except Exception as e:
            messagebox.showerror("Error", f"Failed to connect to server: {str(e)}")
            return None

    def display_friend(self, friend):
        """Display a single friend with options to accept, decline, or remove."""
        friend_frame = ctk.CTkFrame(self.friend_list_frame, fg_color="#f9f9f9", corner_radius=10)  # Light gray background for friend frames
        friend_frame.pack(fill="x", padx=5, pady=5)

        # Display friend information with name and status
        friend_name = friend.get("name", f"Friend ID: {friend['friend_id']}")  # Default to ID if name is missing
        friend_status = friend.get("status", "unknown")
        friend_info = f"{friend_name} - Status: {friend_status}"
        label = ctk.CTkLabel(friend_frame, text=friend_info, font=("Arial", 14), text_color="#333333", fg_color="#f9f9f9")
        label.pack(side="left", padx=10, pady=5)

        # Button styling
        button_style = {
            "width": 80,
            "height": 30,
            "corner_radius": 8,
            "text_color": "white"
        }

        # Add action buttons based on status
        if friend_status == "pending":
            accept_btn = ctk.CTkButton(friend_frame, text="Accept", command=lambda: self.accept_friend(friend['friend_id']), fg_color="#5cb85c", hover_color="#4cae4c", **button_style)
            decline_btn = ctk.CTkButton(friend_frame, text="Decline", command=lambda: self.decline_friend(friend['friend_id']), fg_color="#d9534f", hover_color="#c9302c", **button_style)
            accept_btn.pack(side="right", padx=5, pady=5)
            decline_btn.pack(side="right", padx=5, pady=5)
        elif friend_status == "accepted":
            remove_btn = ctk.CTkButton(friend_frame, text="Remove", command=lambda: self.remove_friend(friend['friend_id']), fg_color="#d9534f", hover_color="#c9302c", **button_style)
            remove_btn.pack(side="right", padx=5, pady=5)

    def send_friend_action(self, action, friend_id):
        """Send friend action request (accept, decline, remove) to server."""
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((HOST, FRIEND_SERVER_PORT))
            request_data = json.dumps({
                "request_type": action,
                "user_id": user_id,
                "friend_id": friend_id
            })
            client.sendall(request_data.encode(ENCODING))

            response = client.recv(BUFFER_SIZE).decode(ENCODING)
            response_data = json.loads(response)
            client.close()

            if response_data.get("status") == "SUCCESS":
                self.load_friends()
            else:
                messagebox.showerror("Error", response_data.get("message", "Failed to update friend status."))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to connect to server: {str(e)}")

    def accept_friend(self, friend_id):
        """Accept a friend request."""
        self.send_friend_action("ACCEPT_FRIEND_REQUEST", friend_id)

    def decline_friend(self, friend_id):
        """Decline a friend request."""
        self.send_friend_action("DECLINE_FRIEND_REQUEST", friend_id)

    def remove_friend(self, friend_id):
        """Remove a friend."""
        self.send_friend_action("REMOVE_FRIEND", friend_id)

# Run the application
if __name__ == "__main__":
    root = ctk.CTk()
    app = FriendApp(root)
    root.mainloop()
