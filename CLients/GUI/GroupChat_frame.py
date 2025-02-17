import socket
import threading
import random
import tkinter as tk
from tkinter import scrolledtext, messagebox

SERVER_IP = "127.0.0.1"
SERVER_PORT = 5000
CLIENT_PORT = random.randint(10000, 20000)

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.bind(("127.0.0.1", CLIENT_PORT))

# Hàm gửi yêu cầu tham gia vào server
def join_chat():
    username = username_entry.get()
    if username:
        client_socket.sendto(f"JOIN {username}".encode('utf-8'), (SERVER_IP, SERVER_PORT))
        chat_log.insert(tk.END, "Bạn đã tham gia phòng chat\n")
    else:
        messagebox.showwarning("Lỗi", "Vui lòng nhập tên")

# Hàm gửi tin nhắn đến client khác
def send_message():
    target_ip = target_ip_entry.get()
    target_port = int(target_port_entry.get())
    message = message_entry.get()
    
    if message:
        client_socket.sendto(message.encode('utf-8'), (target_ip, target_port))
        chat_log.insert(tk.END, f"Bạn: {message}\n")
        message_entry.delete(0, tk.END)
    else:
        messagebox.showwarning("Lỗi", "Vui lòng nhập tin nhắn")

# Hàm nhận tin nhắn từ các client khác
def receive_messages():
    while True:
        message, address = client_socket.recvfrom(1024)
        chat_log.insert(tk.END, f"Từ {address}: {message.decode('utf-8')}\n")

# Khởi động luồng nhận tin nhắn
threading.Thread(target=receive_messages, daemon=True).start()

# Thiết lập giao diện với tkinter
root = tk.Tk()
root.title("Chat Room UDP - Client")
root.geometry("400x500")

# Khung nhập tên
tk.Label(root, text="Tên của bạn:").pack(pady=5)
username_entry = tk.Entry(root)
username_entry.pack(pady=5)

# Nút tham gia chat
join_button = tk.Button(root, text="Tham gia Chat", command=join_chat)
join_button.pack(pady=5)

# Khung nhật ký chat
chat_log = scrolledtext.ScrolledText(root, width=50, height=20, state="normal")
chat_log.pack(pady=5)

# Khung nhập IP và cổng người nhận
tk.Label(root, text="IP của người nhận:").pack(pady=5)
target_ip_entry = tk.Entry(root)
target_ip_entry.pack(pady=5)

tk.Label(root, text="Cổng của người nhận:").pack(pady=5)
target_port_entry = tk.Entry(root)
target_port_entry.pack(pady=5)

# Khung nhập tin nhắn
tk.Label(root, text="Tin nhắn của bạn:").pack(pady=5)
message_entry = tk.Entry(root, width=50)
message_entry.pack(pady=5)

# Nút gửi tin nhắn
send_button = tk.Button(root, text="Gửi", command=send_message)
send_button.pack(pady=5)

root.mainloop()
