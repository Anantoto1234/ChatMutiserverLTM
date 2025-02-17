import tkinter as tk
from tkinter import messagebox, Scrollbar, Canvas
import socket
import json
from PIL import Image, ImageTk
import os
from datetime import datetime
import threading
from session_manager import SessionManager

# Server configurations
HOST = "127.0.0.1"
CHAT_SERVER_PORT = 6005
BUFFER_SIZE = 4096
ENCODING = 'utf-8'

# Path for server images
SERVER_UPLOADS_PATH = r"D:\Documents\I_2024-25\LTM\Ck\LTM\Server"

# Initialize session manager
session_manager = SessionManager()
user_id = session_manager.get_user_id()

class ChatClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat Application")
        self.root.geometry("800x600")

        # Assume user_id is retrieved after login
        self.user_id = user_id

        # Initialize chat variables
        self.create_ui()
        self.selected_conversation = None
        self.contact_images = {}
        self.last_message_timestamp = None
        self.stop_event = threading.Event()
        self.is_group_chat = False  # Flag to track if current chat is a group chat

        # Start polling thread
        self.polling_thread = threading.Thread(target=self.poll_for_new_messages, daemon=True)
        self.polling_thread.start()

        # Load contacts and groups on startup
        self.load_contacts_and_groups()

    def create_ui(self):
        # Set up UI layout
        self.root.grid_columnconfigure(0, weight=1, minsize=200)
        self.root.grid_columnconfigure(1, weight=4)

        # Contacts list
        self.contacts_frame = tk.Frame(self.root, bg="white")
        self.contacts_frame.grid(row=0, column=0, sticky="nswe")

        contacts_label = tk.Label(self.contacts_frame, text="Contacts & Groups", font=("Arial", 14, "bold"), bg="white")
        contacts_label.pack(pady=5)

        self.contacts_canvas = Canvas(self.contacts_frame, bg="white", borderwidth=0, highlightthickness=0)
        self.contacts_canvas.pack(side="left", fill="both", expand=True)
        self.contacts_scrollbar = Scrollbar(self.contacts_frame, command=self.contacts_canvas.yview)
        self.contacts_scrollbar.pack(side="right", fill="y")
        self.contacts_canvas.configure(yscrollcommand=self.contacts_scrollbar.set)

        self.contacts_inner_frame = tk.Frame(self.contacts_canvas, bg="white")
        self.contacts_canvas.create_window((0, 0), window=self.contacts_inner_frame, anchor="nw")
        self.contacts_inner_frame.bind("<Configure>", lambda e: self.contacts_canvas.configure(scrollregion=self.contacts_canvas.bbox("all")))

        # Chat display area
        self.chat_frame = tk.Frame(self.root, bg="lightgray")
        self.chat_frame.grid(row=0, column=1, sticky="nswe", padx=5, pady=5)

        self.chat_display = tk.Text(self.chat_frame, wrap="word", state="disabled", bg="white", font=("Arial", 12), padx=10, pady=10)
        self.chat_display.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Message bubble and timestamp styling
        self.chat_display.tag_configure("right_bubble", justify="right", background="#DCF8C6", font=("Arial", 12), lmargin1=150, rmargin=10, spacing1=10, spacing3=10)
        self.chat_display.tag_configure("left_bubble", justify="left", background="#FFFFFF", font=("Arial", 12), lmargin1=10, rmargin=150, spacing1=10, spacing3=10)
        self.chat_display.tag_configure("right_timestamp", justify="right", font=("Arial", 8, "italic"), foreground="grey", spacing1=2)
        self.chat_display.tag_configure("left_timestamp", justify="left", font=("Arial", 8, "italic"), foreground="grey", spacing1=2)

        # Message entry box
        self.message_entry = tk.Entry(self.root, font=("Arial", 14))
        self.message_entry.grid(row=1, column=1, sticky="we", padx=10, pady=5)
        self.message_entry.bind("<Return>", self.send_message)

    def load_contacts_and_groups(self):
        contacts = self.get_contacts_and_groups_from_server()
        if contacts:
            for contact in contacts:
                self.display_contact(contact)

    def display_contact(self, contact):
        contact_frame = tk.Frame(self.contacts_inner_frame, bg="white", pady=5)
        contact_frame.pack(fill="x", padx=5)

        user_id = contact.get("user_id")
        is_group_chat = contact.get("is_group_chat", False)

        if not is_group_chat:
            profile_photo = self.get_profile_image(contact.get("image_path"))
        else:
            profile_photo = ImageTk.PhotoImage(Image.new("RGBA", (40, 40), (0, 150, 255, 255)))  # Use a default group image

        self.contact_images[user_id] = profile_photo
        contact_image_label = tk.Label(contact_frame, image=profile_photo, bg="white")
        contact_image_label.image = profile_photo
        contact_image_label.pack(side="left", padx=5)

        contact_name = contact.get("name") or f"{contact['firstname']} {contact['lastname']}"
        contact_label = tk.Label(contact_frame, text=contact_name, font=("Arial", 12), bg="white")
        contact_label.pack(side="left")

        # Set `self.is_group_chat` based on the contact selected
        contact_frame.bind("<Button-1>", lambda e, c=contact: self.on_contact_select(c))

    def on_contact_select(self, contact):
        self.selected_conversation = contact
        self.is_group_chat = contact.get("is_group_chat", False)  # Set group chat status based on selection
        self.last_message_timestamp = None
        self.chat_display.config(state="normal")
        self.chat_display.delete(1.0, tk.END)
        self.chat_display.config(state="disabled")
        self.load_messages(contact.get("id", contact.get("user_id")))

    def poll_for_new_messages(self):
        while not self.stop_event.is_set():
            if self.selected_conversation:
                self.load_messages(self.selected_conversation.get("id", self.selected_conversation.get("user_id")))
            self.stop_event.wait(2)

    def load_messages(self, conversation_id):
        # Fetch messages only after the last timestamp to avoid duplicates
        response = self.get_messages_from_server(conversation_id, self.last_message_timestamp)
        if response.get("status") == "SUCCESS":
            new_messages = response["messages"]

            if new_messages:
                self.chat_display.config(state="normal")
                for message in new_messages:
                    # Check to avoid appending duplicate messages
                    if message["timestamp"] > (self.last_message_timestamp or ""):
                        sender = "You" if message["sender_id"] == self.user_id else message.get("sender_name", "Them")
                        timestamp = message["timestamp"]
                        content = message["content"]
                        image_path = message.get("image_path", "")

                        self.append_message(sender, content, timestamp, image_path)
                        self.last_message_timestamp = timestamp
                self.chat_display.config(state="disabled")
                self.chat_display.see(tk.END)

    def append_message(self, sender, content, timestamp="", image_path=None):
        profile_photo = self.get_profile_image(image_path) if image_path else self.get_default_profile_image()

        if sender == "You":
            self.chat_display.insert(tk.END, f"{content}\n", "right_bubble")
            self.chat_display.insert(tk.END, f"{timestamp}\n", "right_timestamp")
        else:
            if profile_photo:
                self.chat_display.image_create(tk.END, image=profile_photo, padx=5)

            # Use `self.is_group_chat` to show sender name for group chats
            display_name = f"{sender}: " if self.is_group_chat else ""
            self.chat_display.insert(tk.END, f"{display_name}{content}\n", "left_bubble")
            self.chat_display.insert(tk.END, f"{timestamp}\n", "left_timestamp")

    def get_profile_image(self, image_path):
        if not isinstance(image_path, str) or not image_path:
            return self.get_default_profile_image()

        full_image_path = os.path.join(SERVER_UPLOADS_PATH, image_path)
        if full_image_path in self.contact_images:
            return self.contact_images[full_image_path]
        elif os.path.exists(full_image_path):
            try:
                image = Image.open(full_image_path).resize((40, 40), Image.LANCZOS)
                profile_photo = ImageTk.PhotoImage(image)
                self.contact_images[full_image_path] = profile_photo
                return profile_photo
            except Exception as e:
                print(f"[ERROR] Error loading profile image at {full_image_path}: {e}")
                return self.get_default_profile_image()
        else:
            print(f"[ERROR] Image file not found at path: {full_image_path}. Using default image.")
            return self.get_default_profile_image()

    def get_default_profile_image(self):
        if "default" not in self.contact_images:
            default_image = Image.new("RGBA", (40, 40), (200, 200, 200, 255))
            self.contact_images["default"] = ImageTk.PhotoImage(default_image)
        return self.contact_images["default"]

    def get_contacts_and_groups_from_server(self):
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((HOST, CHAT_SERVER_PORT))
            request_data = json.dumps({"request_type": "GET_CONTACTS_AND_GROUPS", "user_id": self.user_id})
            client.sendall(request_data.encode(ENCODING))
            response = client.recv(BUFFER_SIZE).decode(ENCODING)
            response_data = json.loads(response)
            client.close()
            return response_data.get("contacts", []) if response_data.get("status") == "SUCCESS" else []
        except Exception as e:
            messagebox.showinfo("Info", f"Failed to connect to server: {str(e)}")
            return []

    def get_messages_from_server(self, conversation_id, since=None):
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((HOST, CHAT_SERVER_PORT))
            request_data = json.dumps({"request_type": "GET_MESSAGES", "conversation_id": conversation_id, "since": since})
            client.sendall(request_data.encode(ENCODING))
            response = client.recv(BUFFER_SIZE).decode(ENCODING)
            client.close()
            return json.loads(response)
        except Exception as e:
            print(f"Failed to connect to server: {e}")
            return {"status": "ERROR", "message": str(e)}

    def send_message(self, event=None):
        if not self.selected_conversation:
            messagebox.showinfo("Info", "Please select a contact or group to send a message.")
            return

        message = self.message_entry.get().strip()
        if message == "":
            messagebox.showinfo("Info", "Cannot send an empty message.")
            return

        # Send message to the server and only append if successful
        if self.send_message_to_server(self.selected_conversation.get("id", self.selected_conversation.get("user_id")), message):
            self.append_message("You", message, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            self.message_entry.delete(0, tk.END)

    def send_message_to_server(self, conversation_id, message):
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((HOST, CHAT_SERVER_PORT))
            request_data = json.dumps({"request_type": "SEND_MESSAGE", "conversation_id": conversation_id, "sender_id": self.user_id, "message": message})
            client.sendall(request_data.encode(ENCODING))
            response = client.recv(BUFFER_SIZE).decode(ENCODING)
            response_data = json.loads(response)
            client.close()
            return response_data.get("status") == "SUCCESS"
        except Exception as e:
            messagebox.showinfo("Info", f"Failed to connect to server: {str(e)}")
            return False

    def stop_client(self):
        self.stop_event.set()
        self.root.after(100, self.root.quit)

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = ChatClient(root)
    root.protocol("WM_DELETE_WINDOW", app.stop_client)
    root.mainloop()
