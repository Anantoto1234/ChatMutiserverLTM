import os
import socket
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import time
import base64
import subprocess
import json
import logging
from session_manager import SessionManager

# Initialize the session manager and retrieve the user_id
session_manager = SessionManager()
user_id = session_manager.get_user_id()

# Constants
HOST = "127.0.0.1"
UPLOAD_SERVER_PORT = 6003
BUFFER_SIZE = 4096
ENCODING = 'utf-8'

# Set up logging

# Set up logging
logging.basicConfig(level=logging.INFO)

# Initialize customtkinter appearance settings
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

def update_clock(clock_label):
    """Updates the clock every second."""
    current_time = time.strftime("%I:%M:%S %p")
    clock_label.configure(text=current_time)
    clock_label.after(1000, update_clock, clock_label)
# Set up logging
logging.basicConfig(level=logging.INFO)

def send_image_to_server(image_path, user_id, image_type):
    if not os.path.isfile(image_path):
        print("Error: Image file not found.")
        return

    filename = os.path.basename(image_path)
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect((HOST, UPLOAD_SERVER_PORT))

        # Read and encode image as Base64
        with open(image_path, 'rb') as image_file:
            image_data = image_file.read()
            base64_image = base64.b64encode(image_data).decode('utf-8')

        # Prepare metadata as a JSON object
        metadata = {
            "request_type": "UPLOAD_IMAGE",
            "user_id": user_id,
            "filename": filename,
            "image_type": image_type,
            "base64_data": base64_image
        }

        # Convert metadata to JSON and add a newline character to indicate the end of the message
        metadata_json = json.dumps(metadata) + "\n"
        print(f"Client => sending JSON metadata: {metadata_json[:100]}...")  # Print first 100 chars for confirmation

        # Send metadata as JSON
        client.sendall(metadata_json.encode(ENCODING))
        print("Client => waiting for Server response...")

        # Receive response
        response = client.recv(BUFFER_SIZE).decode(ENCODING)
        print("Client => received Server response:", response)

        response_data = json.loads(response)
        if response_data.get("status") == "SUCCESS":
            print("Image uploaded successfully!")
        else:
            print("Error from server:", response_data.get("message", "Unknown error"))
    except Exception as e:
        print(f"An error occurred while sending the image: {e}")
    finally:
        client.close()  # Ensure the client connection is closed



def update_profile_picture():
    """Opens a file dialog for profile picture update and sends it to the server."""
    file_path = filedialog.askopenfilename(title="Choose Profile Picture", filetypes=[("Image Files", "*.jpg;*.jpeg;*.png")])
    if file_path:
        user_id = session_manager.get_user_id()
        if user_id is None:
            messagebox.showerror("Error", "User ID not found. Please log in first.")
            return

        image = Image.open(file_path).convert("RGBA")
        size = 50
        circle_image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        mask = Image.new("L", (size, size), 0)

        for x in range(size):
            for y in range(size):
                if (x - size // 2) ** 2 + (y - size // 2) ** 2 <= (size // 2) ** 2:
                    mask.putpixel((x, y), 255)

        image = image.resize((size, size), Image.LANCZOS)
        circle_image.paste(image, (0, 0), mask)

        profile_image = ImageTk.PhotoImage(circle_image)
        profile_icon.configure(image=profile_image)
        profile_icon.image = profile_image

        send_image_to_server(file_path, user_id, image_type="profile")



def open_friend(event=None):
    """Opens the Friend window and passes the user_id."""
    user_id = session_manager.get_user_id()
    if user_id is None:
        messagebox.showerror("Error", "User ID not found. Please log in first.")
        return
    subprocess.Popen(["python", "Friend.py", str(user_id)])

def contacts():
    """Opens the Contacts window."""
    try:
        from Contact import open_friend_window
        open_friend_window()
    except Exception as e:
        logging.error(f"Error opening contacts window: {e}")
        messagebox.showerror("Error", "Failed to open contacts")

def open_meeting_app(event=None):
    """Opens the meeting application."""
    try:
        subprocess.Popen(["python", os.path.join("flask_video_call", "app.py")])
    except Exception as e:
        logging.error(f"Error opening meeting app: {e}")
        messagebox.showerror("Error", "Failed to open meeting application")

def open_send_email(event=None):
    """Opens the email sending application."""
    try:
        subprocess.Popen(["python", "Gmail.py"])
    except Exception as e:
        logging.error(f"Error opening email app: {e}")
        messagebox.showerror("Error", "Failed to open email application")

def open_share_screen(event=None):
    """Opens the screen-sharing application."""
    try:
        subprocess.Popen(["python", "Share.py"])
    except Exception as e:
        logging.error(f"Error opening screen-sharing app: {e}")
        messagebox.showerror("Error", "Failed to open screen-sharing application")
def open_chat(event =None):
    """Opens the Friend window and passes the user_id."""
    user_id = session_manager.get_user_id()
    if user_id is None:
        messagebox.showerror("Error", "User ID not found. Please log in first.")
        return
    subprocess.Popen(["python", "Chat.py", str(user_id)])
        
def create_main_window():
    """Creates the main window of the application."""
    root = ctk.CTk()
    root.geometry("1000x650")
    root.title("Zoom-like Interface")

    top_frame = ctk.CTkFrame(root, height=60, fg_color="#007bff", corner_radius=0)
    top_frame.pack(side="top", fill="x")

    nav_buttons = {
        "Home": None,
        "Chat": open_chat,
        "Friend": open_friend,
        "Meetings": open_meeting_app,
        "Contacts": contacts
    }
    for btn_text, command in nav_buttons.items():
        btn = ctk.CTkButton(top_frame, text=btn_text, width=120, height=40, fg_color="#007bff", text_color="white", corner_radius=10, command=command)
        btn.pack(side="left", padx=25, pady=10)

    global profile_icon
    profile_icon = tk.Label(top_frame, text="👤", bg="#007bff", font=("Arial", 20), fg="white")
    profile_icon.pack(side="right", padx=10, pady=10)
    profile_icon.bind("<Button-1>", lambda e: update_profile_picture())

    main_frame = ctk.CTkFrame(root, fg_color="white")
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)

    left_frame = ctk.CTkFrame(main_frame, fg_color="white")
    left_frame.grid(row=0, column=0, padx=20, pady=20)
    button_info = [
        ("New Meeting", "#f69256", open_meeting_app), 
        ("Chat", "#28a745", open_chat), 
        ("Send Email", "#007bff", open_send_email), 
        ("Share Screen", "#ffc107", open_share_screen)
    ]
    for text, color, command in button_info:
        btn = ctk.CTkButton(left_frame, text=text, width=200, height=60, fg_color=color, text_color="white", corner_radius=10, command=command)
        btn.pack(pady=15)

    right_frame = ctk.CTkFrame(main_frame, fg_color="white")
    right_frame.grid(row=0, column=1, padx=100, pady=20)

    clock_label = tk.Label(right_frame, font=("Arial", 48), bg="white", fg="#343a40")
    clock_label.pack(pady=20, padx=100)
    update_clock(clock_label)

    date_label = tk.Label(right_frame, text=time.strftime("%A, %B %d, %Y"), font=("Arial", 24), bg="white", fg="#6c757d")
    date_label.pack(pady=10)

    calendar_label = tk.Label(right_frame, text="Add a calendar", font=("Arial", 14), bg="white", fg="#6c757d")
    calendar_label.pack(pady=30)

    root.mainloop()

if __name__ == "__main__":
    create_main_window()
