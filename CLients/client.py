

def send_image_to_server(image_path, user_id, image_type):
    """Gửi hình ảnh từ client đến server."""
    
    # Kiểm tra nếu tệp có tồn tại
    if not os.path.isfile(image_path):
        print("Error: File does not exist.")
        return
    
    # Tạo socket kết nối đến server
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client.connect((HOST, SERVER_PORT))  # Kết nối đến server
        
        # Tạo dữ liệu yêu cầu
        request_data = f"UPLOAD_IMAGE,{user_id},{image_type},{os.path.basename(image_path)}"
        client.sendall(request_data.encode('utf-8'))  # Gửi yêu cầu
        
        # Gửi dữ liệu hình ảnh
        with open(image_path, 'rb') as image_file:
            while True:
                # Đọc một khối dữ liệu từ hình ảnh
                data = image_file.read(1024)
                if not data:
                    break  # Kết thúc khi không còn dữ liệu
                client.sendall(data)  # Gửi dữ liệu đến server

        print("Image sent successfully.")
    except Exception as e:
        print(f"Error sending image: {e}")
    finally:
        client.close()  # Đóng kết nối

# Hàm để cập nhật ảnh hồ sơ
def update_profile_picture():
    # Mở hộp thoại để chọn tệp hình ảnh
    file_path = filedialog.askopenfilename(title="Select Profile Picture",
                                            filetypes=[("Image Files", "*.jpg;*.jpeg;*.png")])
    if not file_path:
        return  # Nếu không chọn tệp nào

    user_id = 1  # Thay thế với giá trị user_id thực tế
    image_type = 'profile_picture'  # Loại hình ảnh

    # Gọi hàm gửi hình ảnh với đủ tham số
    send_image_to_server(file_path, user_id, image_type)