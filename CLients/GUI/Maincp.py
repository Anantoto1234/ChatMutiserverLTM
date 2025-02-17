import os
import socket
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import time,base64
import json
HOST = "127.0.0.1"
SERVER_PORT = 12345  # Thay đổi cổng để khớp với server
FORMAT = "utf8"
import json

# Initialize customtkinter appearance settings
ctk.set_appearance_mode("light")  # Modes: system (default), light, dark
ctk.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

# Function to update the clock
def update_clock(clock_label):
    current_time = time.strftime("%I:%M:%S %p")  # Get current time in HH:MM:SS AM/PM format
    clock_label.configure(text=current_time)  # Update label text
    clock_label.after(1000, update_clock, clock_label)  # Call this function again in 1 second

# Function to send the image to the server
def send_image_to_server(image_path, user_id, image_type):
    if not os.path.isfile(image_path):
        print("Error: Image file not found.")
        return

    filename = os.path.basename(image_path)
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect((HOST, SERVER_PORT))
        # initial_data = f"UPLOAD_IMAGE,{user_id},{filename},{image_type}"
        # client.sendall(initial_data.encode("utf-8"))

        # with open(image_path, 'rb') as f:
        #     image_data = f.read()
        #     client.sendall(image_data)  # Gửi dữ liệu hình ảnh

        # client.sendall(b'EOF')  # Gửi dấu hiệu kết thúc
        with open(image_path, 'rb') as image_file:
            image_data = image_file.read()
            base64_image = base64.b64encode(image_data).decode('utf-8')  # Chuyển đổi thành Base64

        # Gửi dữ liệu metadata cùng với hình ảnh dưới dạng Base64
        initial_data = f"UPLOAD_IMAGE,{user_id},{filename},{image_type},{base64_image}"
        client.sendall(initial_data.encode("utf-8"))
        print("Client => waiting Server response...")
        response = client.recv(4096).decode("utf-8")
        print("Client => rec Server response:", response)
        
        response_data = json.loads(response)
        if response_data.get("status") == "SUCCESS":
            print("Image uploaded successfully!")
        else:
            print("Error from server:", response_data.get("error", "Unknown error"))
    except Exception as e:
        print(f"An error occurred while sending the image: {e}")
    finally:
        client.close()  # Đảm bảo kết nối client được đóng
        

# Function to update the profile picture
def update_profile_picture():
    print("-----Onpress upload profile picture-----")
    file_path = filedialog.askopenfilename(title="Chọn ảnh đại diện", filetypes=[("Image Files", "*.jpg;*.jpeg;*.png")])
    if file_path:
        # Open image and convert for display
        image = Image.open(file_path).convert("RGBA")

        # Create a circular mask and apply to the image
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

        # Update profile icon
        profile_icon.configure(image=profile_image)
        profile_icon.image = profile_image

        # Send image to server
        send_image_to_server(file_path, user_id=4, image_type="profile")  # Thêm user_id và image_type

''''def perform_search():
    search_term = search_box.get()
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect((HOST, SERVER_PORT))
        search_request = f"SEARCH,{search_term}"
        client.sendall(search_request.encode(FORMAT))

        print("Client => waiting for Server response...")
        response = client.recv(4096).decode(FORMAT)

        response_data = json.loads(response)
        if response_data.get("status") == "SUCCESS":
            user_list = response_data.get("data", [])
            update_search_results(user_list)
        else:
            print("Error from server:", response_data.get("error", "Unknown error"))
    except Exception as e:
        print(f"An error occurred while sending the search request: {e}")
    finally:
        client.close()  # Ensure the client connection is closed
        
#def update_search_results(user_list):
 #   results_frame.delete(0, tk.END)  # Clear old search results
 #   for user in user_list:
 #       results_frame.insert(tk.END, user)  # Add user names to Listbox
  '''      
        
# Function to create the main window
def create_main_window():
    print("-----Welcome to main screen-----")
    try:
        root = ctk.CTk()  # Create a window
        root.geometry("1000x650")  # Set window size
        root.title("Zoom-like Interface")

        # Create the top navigation bar
        top_frame = ctk.CTkFrame(root, height=60, fg_color="#007bff", corner_radius=0)
        top_frame.pack(side="top", fill="x")

        nav_buttons = ["Home", "Chat", "Phone", "Meetings", "Contacts"]
        for btn_text in nav_buttons:
            btn = ctk.CTkButton(top_frame, text=btn_text, width=120, height=40, fg_color="#007bff", hover_color="#0056b3", text_color="white", corner_radius=10)
            btn.pack(side="left", padx=15, pady=10)

        # Create search box and profile icon (right side)
      #  global search_box
        search_box = ctk.CTkEntry(top_frame, placeholder_text="Search", width=150, height=40, corner_radius=10) #command=perform_search)
        search_box.pack(side="right", padx=10, pady=10)
      #  global results_frame
      #  results_frame = tk.Listbox(right_frame, width=50)
       # results_frame.pack(pady=20)
        
        global profile_icon  # Define profile_icon globally
        profile_icon = tk.Label(top_frame, text="👤", bg="#007bff", font=("Arial", 20), fg="white")
        profile_icon.pack(side="right", padx=10, pady=10)
        profile_icon.bind("<Button-1>", lambda e: update_profile_picture())  # Handle profile picture click event

        # Main content area: Left (buttons) and Right (clock & calendar)
        main_frame = ctk.CTkFrame(root, fg_color="white")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Left section (Buttons: New Meeting, Join, Schedule, Share Screen)
        left_frame = ctk.CTkFrame(main_frame, fg_color="white")
        left_frame.grid(row=0, column=0, padx=20, pady=20)

        button_info = [("New Meeting", "#f69256"), ("Join", "#28a745"), ("Schedule", "#007bff"), ("Share Screen", "#ffc107")]

        for text, color in button_info:
            btn = ctk.CTkButton(left_frame, text=text, width=200, height=60, fg_color=color, text_color="white", corner_radius=10)
            btn.pack(pady=15)

        # Right section (Clock, Date, Calendar placeholder)
        right_frame = ctk.CTkFrame(main_frame, fg_color="white")
        right_frame.grid(row=0, column=1, padx=100, pady=20)

        # Clock (live update)
        clock_label = tk.Label(right_frame, font=("Arial", 48), bg="white", fg="#343a40")
        clock_label.pack(pady=20, padx=100)
        update_clock(clock_label)  # Call function to update the clock

        # Date
        date_label = tk.Label(right_frame, text=time.strftime("%A, %B %d, %Y"), font=("Arial", 24), bg="white", fg="#6c757d")
        date_label.pack(pady=10)

        # Calendar placeholder
        calendar_label = tk.Label(right_frame, text="Add a calendar", font=("Arial", 14), bg="white", fg="#6c757d")
        calendar_label.pack(pady=30)

        root.mainloop()
    except Exception as e:
        print("Service error: ", e)

# Run the application
# if __name__ == "__main__":
#     create_main_window()
