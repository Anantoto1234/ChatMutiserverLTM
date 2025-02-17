import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import customtkinter as ctk
from tkinter import filedialog, messagebox


def send_email():
    email = sender_email_entry.get()
    password = password_entry.get()
    receiver_email = receiver_email_entry.get()
    subject = subject_entry.get()
    message = message_entry.get("1.0", ctk.END)

    email_message = MIMEMultipart()
    email_message["From"] = email
    email_message["To"] = receiver_email
    email_message["Subject"] = subject
    email_message.attach(MIMEText(message, "plain"))

    if attached_file_path.get():
        try:
            file_path = attached_file_path.get()
            with open(file_path, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename={file_path.split('/')[-1]}")
            email_message.attach(part)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể đính kèm file: {e}")
            return

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(email, password)
        server.sendmail(email, receiver_email, email_message.as_string())
        messagebox.showinfo("Thành công", f"Email đã được gửi tới {receiver_email}")
    except Exception as e:
        messagebox.showerror("Lỗi", f"Đã xảy ra lỗi: {e}")
    finally:
        server.quit()


def attach_file():
    file_path = filedialog.askopenfilename(title="Chọn file để đính kèm")
    if file_path:
        attached_file_path.set(file_path)
        file_label.configure(text=f"File: {file_path.split('/')[-1]}")


# Tùy chỉnh giao diện với CustomTkinter
ctk.set_appearance_mode("Light")  # Nền sáng
ctk.set_default_color_theme("blue")  # Màu chủ đề xanh

root = ctk.CTk()
root.title("Gửi Email")
root.geometry("500x650")
root.resizable(False, False)

attached_file_path = ctk.StringVar()

# Tạo khung cuộn
scrollable_frame = ctk.CTkScrollableFrame(root, width=480, height=620, corner_radius=10, fg_color="white")
scrollable_frame.pack(pady=10, padx=10, fill="both", expand=True)

# Tiêu đề
title_label = ctk.CTkLabel(scrollable_frame, text="Gửi Email", font=("Arial", 20, "bold"), text_color="black")
title_label.pack(pady=10)

# Email người gửi
ctk.CTkLabel(scrollable_frame, text="Email người gửi:", font=("Arial", 12, "bold"), text_color="black").pack(pady=(10, 5), anchor="w", padx=10)
sender_email_entry = ctk.CTkEntry(scrollable_frame, width=450, height=35, corner_radius=10)
sender_email_entry.pack(pady=5)
sender_email_entry.insert(0, "anltt.22it@vku.udn.vn")

# Mật khẩu ứng dụng
ctk.CTkLabel(scrollable_frame, text="Mật khẩu ứng dụng:", font=("Arial", 12, "bold"), text_color="black").pack(pady=(10, 5), anchor="w", padx=10)
password_entry = ctk.CTkEntry(scrollable_frame, show="*", width=450, height=35, corner_radius=10)
password_entry.pack(pady=5)
password_entry.insert(0, "jihh kyjb ywsh jmep")

# Email người nhận
ctk.CTkLabel(scrollable_frame, text="Email người nhận:", font=("Arial", 12, "bold"), text_color="black").pack(pady=(10, 5), anchor="w", padx=10)
receiver_email_entry = ctk.CTkEntry(scrollable_frame, width=450, height=35, corner_radius=10)
receiver_email_entry.pack(pady=5)

# Chủ đề
ctk.CTkLabel(scrollable_frame, text="Chủ đề:", font=("Arial", 12, "bold"), text_color="black").pack(pady=(10, 5), anchor="w", padx=10)
subject_entry = ctk.CTkEntry(scrollable_frame, width=450, height=35, corner_radius=10)
subject_entry.pack(pady=5)

# Nội dung email
ctk.CTkLabel(scrollable_frame, text="Nội dung:", font=("Arial", 12, "bold"), text_color="black").pack(pady=(10, 5), anchor="w", padx=10)

# Tạo khung viền bao quanh Textbox
message_frame = ctk.CTkFrame(scrollable_frame, width=450, height=120, corner_radius=5, fg_color="#e8e8e8")
message_frame.pack(pady=5)
message_entry = ctk.CTkTextbox(message_frame, width=440, height=110, corner_radius=5, fg_color="white", text_color="black")
message_entry.pack(pady=5, padx=5)


# Nút đính kèm file
attach_button = ctk.CTkButton(scrollable_frame, text="Đính kèm file", command=attach_file, height=35, width=150, fg_color="#1A73E8", text_color="white")
attach_button.pack(pady=(10, 5))

# Hiển thị file đính kèm
file_label = ctk.CTkLabel(scrollable_frame, text="Chưa có file nào được đính kèm", font=("Arial", 10, "bold"), text_color="gray")
file_label.pack(pady=5)

# Nút gửi email
send_button = ctk.CTkButton(scrollable_frame, text="Gửi Email", command=send_email, height=40, width=200, fg_color="#1A73E8", text_color="white")
send_button.pack(pady=20)

# Chạy vòng lặp chính của GUI
root.mainloop()
