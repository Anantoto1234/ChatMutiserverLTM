from tkinter import *
from tkinter import messagebox
import bcrypt
import subprocess
import socket
import json
import requests

from Main import create_main_window


HOST = "127.0.0.1"
AUTH_SERVER_PORT = 6001
BUFFER_SIZE = 4096
ENCODING = 'utf-8'
# Windows Size and Placement

AccountSystem = Tk()
AccountSystem.rowconfigure(0,weight=1)
AccountSystem.columnconfigure(0, weight=1)
height =650
width =1240
x = (AccountSystem.winfo_screenwidth()//2)-(width//2)
y = (AccountSystem.winfo_screenheight()//4)-(height//4)

AccountSystem.geometry('{}x{}+{}+{}'.format(width, height, x, y))

AccountSystem.title("ACCOUNT SYSTEM")

#Navigation through windows

sign_in =Frame(AccountSystem)
sign_up =Frame(AccountSystem)

for frame in(sign_in,sign_up):
    frame.grid(row=0,column=0,sticky='nsew')
    
def show_frame(frame):
    frame.tkraise()
    
show_frame(sign_in)


# ================================================
#=================SIGN PAGE STARTS HERE ==========
#==================================================

# sign up text variables 
FirstName = StringVar()
LastName = StringVar()
Email = StringVar()
Password =StringVar()
ConfirmPassword =StringVar()
OTP = StringVar()  # Lưu mã OTP
sign_up.configure(bg="#525561")

# ================Background Image ====================
backgroundImage = PhotoImage(file="assets\\image_1.png")
bg_image = Label(
    sign_up,
    image=backgroundImage, 
    bg="#525561"
)
bg_image.place(x=120, y=28)

# ================ Header Text Left ====================
headerText_image_left = PhotoImage(file="assets\\headerText_image.png")
headerText_image_label1 = Label(
    bg_image,
    image=headerText_image_left,
    bg="#272A37"
)
headerText_image_label1.place(x=60, y=45)

headerText1 = Label(
    bg_image,
    text="PyWork",
    fg="#FFFFFF",
    font=("yu gothic ui bold", 20 * -1),
    bg="#272A37"
)
headerText1.place(x=110, y=45)

# ================ Header Text Right ====================
headerText_image_right = PhotoImage(file="assets\\headerText_image.png")
headerText_image_label2 = Label(
    bg_image,
    image=headerText_image_right,
    bg="#272A37"
)
headerText_image_label2.place(x=400, y=45)

headerText2 = Label(
    bg_image,
    anchor="nw",
    text="Chat, Họp & Kết Nối Trong Công Việc",
    fg="#FFFFFF",
    font=("yu gothic ui Bold", 20 * -1),
    bg="#272A37"
)
headerText2.place(x=450, y=45)

# ================ CREATE ACCOUNT HEADER ====================
createAccount_header = Label(
    bg_image,
    text="Create new account",
    fg="#FFFFFF",
    font=("yu gothic ui Bold", 28 * -1),
    bg="#272A37"
)
createAccount_header.place(x=75, y=121)

# ================ ALREADY HAVE AN ACCOUNT TEXT ====================
text = Label(
    bg_image,
    text="Already a member?",
    fg="#FFFFFF",
    font=("yu gothic ui Regular", 15 * -1),
    bg="#272A37"
)
text.place(x=75, y=187)

# ================ GO TO LOGIN ====================
switchLogin = Button(
    bg_image,
    text="Login",
    fg="#206DB4",
    font=("yu gothic ui Bold", 15 * -1),
    bg="#272A37",
    bd=0,
    cursor="hand2",
    activebackground="#272A37",
    activeforeground="#ffffff",
    command=lambda: show_frame(sign_in)
)
switchLogin.place(x=230, y=185, width=50, height=35)

# ================ First Name Section ====================
firstName_image = PhotoImage(file="assets\\input_img.png")
firstName_image_Label = Label(
    bg_image,
    image=firstName_image,
    bg="#272A37"
)
firstName_image_Label.place(x=80, y=242)

firstName_text = Label(
    firstName_image_Label,
    text="First name",
    fg="#FFFFFF",
    font=("yu gothic ui SemiBold", 13 * -1),
    bg="#3D404B"
)
firstName_text.place(x=25, y=0)

firstName_icon = PhotoImage(file="assets\\name_icon.png")
firstName_icon_Label = Label(
    firstName_image_Label,
    image=firstName_icon,
    bg="#3D404B"
)
firstName_icon_Label.place(x=159, y=15)

firstName_entry = Entry(
    firstName_image_Label,
    bd=0,
    bg="#3D404B",
    highlightthickness=0,
    font=("yu gothic ui SemiBold", 16 * -1),
    textvariable= FirstName
)
firstName_entry.place(x=8, y=17, width=140, height=27)


# ================ Last Name Section ====================
lastName_image = PhotoImage(file="assets\\input_img.png")
lastName_image_Label = Label(
    bg_image,
    image=lastName_image,
    bg="#272A37"
)
lastName_image_Label.place(x=293, y=242)

lastName_text = Label(
    lastName_image_Label,
    text="Last name",
    fg="#FFFFFF",
    font=("yu gothic ui SemiBold", 13 * -1),
    bg="#3D404B"
    
)
lastName_text.place(x=25, y=0)

lastName_icon = PhotoImage(file="assets\\name_icon.png")
lastName_icon_Label = Label(
    lastName_image_Label,
    image=lastName_icon,
    bg="#3D404B"
)
lastName_icon_Label.place(x=159, y=15)

lastName_entry = Entry(
    lastName_image_Label,
    bd=0,
    bg="#3D404B",
    highlightthickness=0,
    font=("yu gothic ui SemiBold", 16 * -1),
    textvariable=LastName
)
lastName_entry.place(x=8, y=17, width=140, height=27)

# ================ Email Name Section ====================
emailName_image = PhotoImage(file="assets\\email.png")
emailName_image_Label = Label(
    bg_image,
    image=emailName_image,
    bg="#272A37"
)
emailName_image_Label.place(x=80, y=311)

emailName_text = Label(
    emailName_image_Label,
    text="Email account",
    fg="#FFFFFF",
    font=("yu gothic ui SemiBold", 13 * -1),
    bg="#3D404B"
)
emailName_text.place(x=25, y=0)

emailName_icon = PhotoImage(file="assets\\email-icon.png")
emailName_icon_Label = Label(
    emailName_image_Label,
    image=emailName_icon,
    bg="#3D404B"
)
emailName_icon_Label.place(x=370, y=15)

emailName_entry = Entry(
    emailName_image_Label,
    bd=0,
    bg="#3D404B",
    highlightthickness=0,
    font=("yu gothic ui SemiBold", 16 * -1),
    textvariable=Email
)
emailName_entry.place(x=8, y=17, width=354, height=27)


# ================ Password Name Section ====================
passwordName_image = PhotoImage(file="assets\\input_img.png")
passwordName_image_Label = Label(
    bg_image,
    image=passwordName_image,
    bg="#272A37"
)
passwordName_image_Label.place(x=80, y=380)

passwordName_text = Label(
    passwordName_image_Label,
    text="Password",
    fg="#FFFFFF",
    font=("yu gothic ui SemiBold", 13 * -1),
    bg="#3D404B"
)
passwordName_text.place(x=25, y=0)

passwordName_icon = PhotoImage(file="assets\\pass-icon.png")
passwordName_icon_Label = Label(
    passwordName_image_Label,
    image=passwordName_icon,
    bg="#3D404B"
)
passwordName_icon_Label.place(x=159, y=15)

passwordName_entry = Entry(
    passwordName_image_Label,
    bd=0,
    bg="#3D404B",
    highlightthickness=0,
    font=("yu gothic ui SemiBold", 16 * -1),
    textvariable=Password,
    show="*"
)
passwordName_entry.place(x=8, y=17, width=140, height=27)


# ================ Confirm Password Name Section ====================
confirm_passwordName_image = PhotoImage(file="assets\\input_img.png")
confirm_passwordName_image_Label = Label(
    bg_image,
    image=confirm_passwordName_image,
    bg="#272A37"
)
confirm_passwordName_image_Label.place(x=293, y=380)

confirm_passwordName_text = Label(
    confirm_passwordName_image_Label,
    text="Confirm Password",
    fg="#FFFFFF",
    font=("yu gothic ui SemiBold", 13 * -1),
    bg="#3D404B"
)
confirm_passwordName_text.place(x=25, y=0)

confirm_passwordName_icon = PhotoImage(file="assets\\pass-icon.png")
confirm_passwordName_icon_Label = Label(
    confirm_passwordName_image_Label,
    image=confirm_passwordName_icon,
    bg="#3D404B"
)
confirm_passwordName_icon_Label.place(x=159, y=15)

confirm_passwordName_entry = Entry(
    confirm_passwordName_image_Label,
    bd=0,
    bg="#3D404B",
    highlightthickness=0,
    font=("yu gothic ui SemiBold", 16 * -1),
    textvariable=ConfirmPassword,
    show="*"
)
confirm_passwordName_entry.place(x=8, y=17, width=140, height=27)

# =============== Submit Button ====================
submit_buttonImage = PhotoImage(
    file="assets\\button_1.png")
submit_button = Button(
    bg_image,
    image=submit_buttonImage,
    borderwidth=0,
    highlightthickness=0,
    relief="flat",
    activebackground="#272A37",
    cursor="hand2",
   command= lambda: signup(FirstName.get(), LastName.get(), Email.get(), Password.get(), ConfirmPassword.get())
)
submit_button .place(x=130, y=460, width=333, height=65)

# ================ Header Text Down ====================
headerText_image_down = PhotoImage(file="assets\\headerText_image.png")
headerText_image_label3 = Label(
    bg_image,
    image=headerText_image_down,
    bg="#272A37"
)
headerText_image_label3.place(x=650, y=530)

headerText3 = Label(
    bg_image,
    text="Designed by An",
    fg="#FFFFFF",
    font=("yu gothic ui bold", 20 * -1),
    bg="#272A37"
)
headerText3.place(x=700, y=530)


FirstName.set("")
LastName.set("")
Password.set("")
ConfirmPassword.set("")
Email.set("")
OTP.set("") 

# ========================================
# Database connection for sign up
def clear():
    FirstName.set("")
    LastName.set("")
    Password.set("")
    ConfirmPassword.set("")
    Email.set("")
    OTP.set("") 

# Trường nhập OTP (ban đầu ẩn)

# OTP Widgets (Hidden Initially)
otp_label = Label(sign_up, text="Enter OTP:", font=("Arial", 14), bg="#272A37", fg="white")
otp_entry = Entry(sign_up, textvariable=OTP, font=("Arial", 14))
submit_otp_button = Button(
    sign_up, text="Verify OTP", font=("Arial", 14), bg="green", fg="white",
    command=lambda: verify_otp(Email.get(), OTP.get())
)

def show_otp_widgets():
    """Hiển thị các widget OTP ở giữa màn hình."""
    # Hide registration widgets
    firstName_image_Label.place_forget()
    lastName_image_Label.place_forget()
    emailName_image_Label.place_forget()
    passwordName_image_Label.place_forget()
    confirm_passwordName_image_Label.place_forget()
    submit_button.place_forget()

    # Center OTP Widgets
    otp_label.place(relx=0.5, rely=0.4, anchor="center")
    otp_entry.place(relx=0.5, rely=0.5, anchor="center", width=200)
    submit_otp_button.place(relx=0.5, rely=0.6, anchor="center", width=160, height=40)

def clear():
    """Clear all fields."""
    FirstName.set("")
    LastName.set("")
    Email.set("")
    Password.set("")
    ConfirmPassword.set("")
    OTP.set("")

def signup(firstname, lastname, email, password, confirm_password):
    """Gửi dữ liệu đăng ký người dùng đến server."""
    if not firstname or not lastname or not email or not password or not confirm_password:
        messagebox.showerror("Error", "All fields are required.")
        return
    if password != confirm_password:
        messagebox.showerror("Error", "Passwords do not match.")
        return

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((HOST, AUTH_SERVER_PORT))
        data = f"REGISTER,{firstname},{lastname},{email},{password},{confirm_password}"
        client.send(data.encode(ENCODING))
        response = client.recv(BUFFER_SIZE).decode(ENCODING)
        response_parts = response.split(',', 1)

        if response_parts[0] == 'error':
            messagebox.showerror("Register Failed", response_parts[1])
        elif response_parts[0] == 'success':
            messagebox.showinfo("Register Successful", response_parts[1])
            show_otp_widgets()
    except ConnectionError:
        messagebox.showerror("Connection Error", "Could not connect to the server.")
    finally:
        client.close()

def verify_otp(email, otp):
    """Gửi OTP để xác minh với server."""
    if not email or not otp:
        messagebox.showerror("Error", "Email and OTP are required.")
        return

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((HOST, AUTH_SERVER_PORT))  # Kết nối đến server

        # Chuẩn bị dữ liệu gửi
        data = f"VERIFY_OTP,{email},{otp}"
        client.send(data.encode(ENCODING))

        # Nhận phản hồi từ server
        response = client.recv(BUFFER_SIZE).decode(ENCODING)

        # Phân tích phản hồi
        response_parts = response.split(',', 1)
        if len(response_parts) < 2:
            messagebox.showerror("Error", "Invalid response from server.")
            return

        if response_parts[0] == 'error':
            messagebox.showerror("Verification Failed", response_parts[1])
        elif response_parts[0] == 'success':
            messagebox.showinfo("Verification Successful", response_parts[1])

            # Xóa các giá trị đầu vào
            clear()

            # Hiển thị lại tất cả các widget trong giao diện đăng ký
            firstName_image_Label.place(x=80, y=242)
            lastName_image_Label.place(x=293, y=242)
            emailName_image_Label.place(x=80, y=311)
            passwordName_image_Label.place(x=80, y=380)
            confirm_passwordName_image_Label.place(x=293, y=380)
            submit_button.place(x=130, y=460, width=333, height=65)

            # Ẩn các widget liên quan đến OTP
            otp_label.place_forget()
            otp_entry.place_forget()
            submit_otp_button.place_forget()

    except ConnectionError:
        messagebox.showerror("Connection Error", "Could not connect to the server. Please try again later.")
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {e}")
    finally:
        client.close()


     
# ================================================
#=================LOGIN PAGE STARTS HERE ==========
#==================================================

email = StringVar()
password = StringVar()

sign_in.configure(bg="#525561")

# ================Background Image ====================
Login_backgroundImage = PhotoImage(file="assets\\image_1.png")
bg_imageLogin = Label(
    sign_in,
    image=Login_backgroundImage,
    bg="#525561"
)
bg_imageLogin.place(x=120, y=28)

# ================ Header Text Left ====================
Login_headerText_image_left = PhotoImage(file="assets\\headerText_image.png")
Login_headerText_image_label1 = Label(
    bg_imageLogin,
    image=Login_headerText_image_left,
    bg="#272A37"
)
Login_headerText_image_label1.place(x=60, y=45)

Login_headerText1 = Label(
    bg_imageLogin,
    text="PyWork",
    fg="#FFFFFF",
    font=("yu gothic ui bold", 20 * -1),
    bg="#272A37"
)
Login_headerText1.place(x=110, y=45)

# ================ Header Text Right ====================
Login_headerText_image_right = PhotoImage(file="assets\\headerText_image.png")
Login_headerText_image_label2 = Label(
    bg_imageLogin,
    image=Login_headerText_image_right,
    bg="#272A37"
)
Login_headerText_image_label2.place(x=400, y=45)

Login_headerText2 = Label(
    bg_imageLogin,
    anchor="nw",
    text="Well Come To PyWork",
    fg="#FFFFFF",
    font=("yu gothic ui Bold", 20 * -1),
    bg="#272A37"
)
Login_headerText2.place(x=450, y=45)

# ================ LOGIN TO ACCOUNT HEADER ====================
loginAccount_header = Label(
    bg_imageLogin,
    text="Login to continue",
    fg="#FFFFFF",
    font=("yu gothic ui Bold", 28 * -1),
    bg="#272A37"
)
loginAccount_header.place(x=75, y=121)

# ================ NOT A MEMBER TEXT ====================
loginText = Label(
    bg_imageLogin,
    text="Not a member?",
    fg="#FFFFFF",
    font=("yu gothic ui Regular", 15 * -1),
    bg="#272A37"
)
loginText.place(x=75, y=187)

# ================ GO TO SIGN UP ====================
switchSignup = Button(
    bg_imageLogin,
    text="Sign Up",
    fg="#206DB4",
    font=("yu gothic ui Bold", 15 * -1),
    bg="#272A37",
    bd=0,
    cursor="hand2",
    activebackground="#272A37",
    activeforeground="#ffffff",
        command=lambda: show_frame(sign_up)
)
switchSignup.place(x=220, y=185, width=70, height=35)


# ================ Email Name Section ====================
# ================ Email Section ====================
Login_emailName_image = PhotoImage(file="assets\\email.png")
Login_emailName_image_Label = Label(
    bg_imageLogin,
    image=Login_emailName_image,
    bg="#272A37"
)
Login_emailName_image_Label.place(x=76, y=242)

Login_emailName_text = Label(
    Login_emailName_image_Label,
    text="Email account",
    fg="#FFFFFF",
    font=("yu gothic ui SemiBold", 13 * -1),
    bg="#3D404B"
)
Login_emailName_text.place(x=25, y=0)

Login_emailName_icon = PhotoImage(file="assets\\email-icon.png")
Login_emailName_icon_Label = Label(
    Login_emailName_image_Label,
    image=Login_emailName_icon,
    bg="#3D404B"
)
Login_emailName_icon_Label.place(x=370, y=15)

Login_emailName_entry = Entry(
    Login_emailName_image_Label,
    bd=0,
    bg="#3D404B",
    highlightthickness=0,
    font=("yu gothic ui SemiBold", 16 * -1),
    textvariable = email
)
Login_emailName_entry.place(x=8, y=17, width=354, height=27)


# ================ Password Section ====================
Login_passwordName_image = PhotoImage(file="assets\\email.png")
Login_passwordName_image_Label = Label(
    bg_imageLogin,
    image=Login_passwordName_image,
    bg="#272A37"
)
Login_passwordName_image_Label.place(x=80, y=330)

Login_passwordName_text = Label(
    Login_passwordName_image_Label,
    text="Password",
    fg="#FFFFFF",
    font=("yu gothic ui SemiBold", 13 * -1),
    bg="#3D404B"
)
Login_passwordName_text.place(x=25, y=0)

Login_passwordName_icon = PhotoImage(file="assets\\pass-icon.png")
Login_passwordName_icon_Label = Label(
    Login_passwordName_image_Label,
    image=Login_passwordName_icon,
    bg="#3D404B"
)
Login_passwordName_icon_Label.place(x=370, y=15)

Login_passwordName_entry = Entry(
    Login_passwordName_image_Label,
    bd=0,
    bg="#3D404B",
    highlightthickness=0,
    font=("yu gothic ui SemiBold", 16 * -1),
    textvariable= password,
    show="*"  # This hides the password input
)
Login_passwordName_entry.place(x=8, y=17, width=354, height=27)

# =============== Submit Button ====================
Login_button_image_1 = PhotoImage(file="assets\\button_1.png")
Login_button_1 = Button(
    bg_imageLogin,
    image=Login_button_image_1,
    borderwidth=0,
    highlightthickness=0,
    relief="flat",
    activebackground="#272A37",
    cursor="hand2",
    command=lambda: login(email=email.get(),password=password.get())
)
Login_button_1.place(x=120, y=445, width=333, height=65)

# ================ Header Text Down ====================
Login_headerText_image_down = PhotoImage(file="assets\\headerText_image.png")
Login_headerText_image_label3 = Label(
    bg_imageLogin,
    image=Login_headerText_image_down,
    bg="#272A37"
)
Login_headerText_image_label3.place(x=650, y=530)

Login_headerText3 = Label(
    bg_imageLogin,
    text="Designed by An",
    fg="#FFFFFF",
    font=("yu gothic ui bold", 20 * -1),
    bg="#272A37"
)
Login_headerText3.place(x=700, y=530)

#=================Clear login fields=============================

def clear_login():
    """Xóa thông tin đăng nhập."""
    email.set("")  # Đặt lại giá trị của biến email
    password.set("")  # Đặt lại giá trị của biến password

# ========================================

import subprocess
from session_manager import SessionManager

session_manager = SessionManager() 
def login(email, password):
    """Handles user login and communicates with the server."""
    if not email or not password:
        messagebox.showerror("Error", "All fields are required")
        return  # Prevent further action if information is missing

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((HOST,AUTH_SERVER_PORT))
        data = f"LOGIN,{email},{password}"  # Data to be sent
        client.send(data.encode('utf-8'))

        response = client.recv(4096).decode('utf-8')
        print(response)  # Print the server's response

        # Process response
        response_data = json.loads(response)  # Parse JSON response

        if 'error' in response_data:
            messagebox.showerror("Login Failed", response_data['error'])  # Get error message
        elif response_data.get('status') == "SUCCESS":
            user_id = response_data.get("user_id")
            print(f"Login successful! User ID: {user_id}")
            session_token = response_data.get("session_token")

            # Save session details
            session_manager.save_session(user_id, session_token)
            print(f"Login successful! User ID: {user_id}, Session Token: {session_token}")
            AccountSystem.destroy() 
            create_main_window()

            # Mở cửa sổ chính
            # open_main_window()
       

            # Clear login fields if necessary
            # clear_login()
            # AccountSystem.destroy() 
            # Run the main application
            # subprocess.run(['python', 'Main.py'])
            # subprocess.Popen(['python', 'Main.py'])  # Sử dụng Popen để mở mà không chờ

        else:
            messagebox.showerror("Error", "Unexpected response from server")

    except json.JSONDecodeError:
        messagebox.showerror("Error", "Failed to decode server response.")
    except Exception as e:
        print(f"An error occurred: {e}")
        messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
    finally:
        client.close()  # Ensure socket is closed on client side

# ================ Forgot Password ====================
forgotPassword = Button(
    bg_imageLogin,
    text="Forgot Password",
    fg="#206DB4",
    font=("yu gothic ui Bold", 15 * -1),
    bg="#272A37",
    bd=0,
    activebackground="#272A37",
    activeforeground="#ffffff",
    cursor="hand2",
    command=lambda: forgot_password(),
)
forgotPassword.place(x=210, y=400, width=150, height=35)


def forgot_password():

    win = Toplevel()
    window_width = 350
    window_height = 350
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    position_top = int(screen_height / 4 - window_height / 4)
    position_right = int(screen_width / 2 - window_width / 2)
    win.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')

    win.title('Forgot Password')
    # win.iconbitmap('images\\aa.ico')
    win.configure(background='#272A37')
    win.resizable(False, False)

    # ====== Email ====================
    email_entry3 = Entry(win, bg="#3D404B", font=("yu gothic ui semibold", 12), highlightthickness=1,
                         bd=0)
    email_entry3.place(x=40, y=80, width=256, height=50)
    email_entry3.config(highlightbackground="#3D404B", highlightcolor="#206DB4")
    email_label3 = Label(win, text='• Email', fg="#FFFFFF", bg='#272A37',
                         font=("yu gothic ui", 11, 'bold'))
    email_label3.place(x=40, y=50)

    # ====  New Password ==================
    new_password_entry = Entry(win, bg="#3D404B", font=("yu gothic ui semibold", 12), show='•', highlightthickness=1,
                               bd=0)
    new_password_entry.place(x=40, y=180, width=256, height=50)
    new_password_entry.config(highlightbackground="#3D404B", highlightcolor="#206DB4")
    new_password_label = Label(win, text='• New Password', fg="#FFFFFF", bg='#272A37',
                               font=("yu gothic ui", 11, 'bold'))
    new_password_label.place(x=40, y=150)

    # ======= Update password Button ============
    # ======= Update password Button ============
    update_pass = Button(win, fg='#f8f8f8', text='Update Password', bg='#1D90F5', font=("yu gothic ui", 12, "bold"),
                     cursor='hand2', relief="flat", bd=0, highlightthickness=0, activebackground="#1D90F5",
                     command=lambda: change_password(email_entry3.get(),new_password_entry.get())
                 )
    update_pass.place(x=40, y=260, width=256, height=45)

    def exit_window():
      win.destroy()

# Database connection for forgot password with password hashing
def change_password(email,new_password):
    if email == "" or new_password == "":
        messagebox.showerror("Error", "All fields are required")
        return

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((HOST,AUTH_SERVER_PORT))
        data = f"FORGOT_PASSWORD,{email},{new_password}"  # Dữ liệu gửi đi
        client.send(data.encode('utf-8'))

        response = client.recv(4096).decode('utf-8')
        print(response)  # In ra phản hồi từ server

        # Xử lý phản hồi từ server
        if 'error' in response:
            messagebox.showerror("Password Update Failed", response.split(',')[1])  # Lấy thông báo lỗi
        elif 'success' in response:
            messagebox.showinfo("Password Updated", response.split(',')[1])  # Lấy thông báo thành công

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        client.close()  # Đảm bảo đóng socket



AccountSystem.resizable(False,False)
AccountSystem.mainloop()




