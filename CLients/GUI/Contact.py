import socket
import json
import customtkinter as ctk
from tkinter import messagebox, ttk
import logging

# Logging configuration
logging.basicConfig(level=logging.INFO)

# Constants for server connection
SERVER_HOST = 'localhost'
SERVER_PORT = 6002
BUFFER_SIZE = 4096
ENCODING = 'utf-8'

# Function to handle search requests
def search_friends():
    friend_name = search_box.get().strip()  # Get and trim the friend's name from the search box
    if friend_name:
        try:
            # Establish a TCP socket connection
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((SERVER_HOST, SERVER_PORT))  # Connect to the search server
            
            # Send search request to the server
            message = f"SEARCH,{friend_name}".encode(ENCODING)
            logging.info(f"Sending search request with keyword: {friend_name}")
            client_socket.sendall(message)

            # Receive the server's response
            response = client_socket.recv(BUFFER_SIZE).decode(ENCODING)
            friends_data = json.loads(response)  # Parse the JSON response from the server

            # Clear previous search results in the table
            for row in result_table.get_children():
                result_table.delete(row)

            # Display results in the table or show an error message
            if isinstance(friends_data, dict) and "error" in friends_data:
                messagebox.showinfo("Search Results", friends_data["error"])
            else:
                for friend in friends_data:
                    result_table.insert("", "end", values=(friend['id'], friend['firstname'], friend['lastname']))
                logging.info(f"Received response from server: {friends_data}")

        except Exception as e:
            logging.error(f"Connection error: {e}")
            messagebox.showerror("Connection Error", f"Error: {str(e)}")
        finally:
            client_socket.close()  # Ensure socket is closed after completion

# Function to initialize the UI
def open_friend_window():
    ctk.set_appearance_mode("Light")  # Set light mode appearance
    ctk.set_default_color_theme("blue")  # Set blue color theme for UI consistency

    # Create the main window
    window = ctk.CTk()
    window.title("Friend Management")
    window.geometry("600x700")
    window.configure(bg="#F5F5F5")  # Light grey background color

    # Top frame containing search box and search button
    top_frame = ctk.CTkFrame(window, corner_radius=15, fg_color="#FFFFFF")  # White background for search bar
    top_frame.pack(pady=20, padx=20, fill="x")

    # Search box entry field
    global search_box
    search_box = ctk.CTkEntry(top_frame, placeholder_text="Enter friend's name", width=300, height=40, corner_radius=20, fg_color="#F1F3F4", placeholder_text_color="grey")
    search_box.pack(side="left", padx=10)

    # Search button
    search_button = ctk.CTkButton(top_frame, text="🔍 Search", command=search_friends, height=40, width=120, fg_color="#1A73E8", text_color="white", corner_radius=20)
    search_button.pack(side="left", padx=5)

    # Label for search results section
    result_title = ctk.CTkLabel(window, text="Search Results", text_color="#5F6368", font=("Roboto", 16, "bold"))
    result_title.pack(pady=(10, 5))

    # Table for displaying search results
    global result_table
    columns = ("ID", "First Name", "Last Name")
    result_table = ttk.Treeview(window, columns=columns, show="headings", height=12)
    result_table.heading("ID", text="ID")
    result_table.heading("First Name", text="First Name")
    result_table.heading("Last Name", text="Last Name")
    result_table.column("ID", anchor="center", width=50)
    result_table.column("First Name", anchor="center", width=200)
    result_table.column("Last Name", anchor="center", width=200)
    result_table.pack(pady=10, padx=20)

    # Vertical scrollbar for the result table
    scrollbar = ttk.Scrollbar(window, orient="vertical", command=result_table.yview)
    result_table.configure(yscroll=scrollbar.set)
    scrollbar.pack(side="right", fill="y", padx=(0, 20))

    # Footer section
    footer_frame = ctk.CTkFrame(window, corner_radius=10, fg_color="#F5F5F5")
    footer_frame.pack(fill="x", pady=(20, 0))
    footer_label = ctk.CTkLabel(footer_frame, text="© 2024 Friend Management", text_color="#5F6368", font=("Roboto", 10))
    footer_label.pack(pady=10)

    window.mainloop()

# Run the UI
if __name__ == "__main__":
    open_friend_window()
