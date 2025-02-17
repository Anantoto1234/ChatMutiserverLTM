import socket
from threading import Thread
from vidstream import CameraClient, VideoStream

class VideoClient:
    def __init__(self, server_ip):
        self.server_ip = server_ip
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Kết nối đến server
        try:
            self.client_socket.connect((self.server_ip, 9999))
            print("Kết nối đến server thành công.")
        except Exception as e:
            print(f"Không thể kết nối đến server: {e}")
            return

    def start_stream(self):
        # Bắt đầu streaming camera
        self.camera_client = CameraClient(self.server_ip, 9999)
        self.camera_client.start_stream()

    def stop_stream(self):
        self.camera_client.stop_stream()
        self.client_socket.send("exit".encode())
        self.client_socket.close()

    def run(self):
        self.start_stream()

        # Đợi người dùng nhập lệnh để dừng
        while True:
            command = input("Nhập 'exit' để tắt cuộc gọi: ")
            if command.lower() == 'exit':
                self.stop_stream()
                break

if __name__ == "__main__":
    server_ip = 'localhost'  # Thay đổi nếu cần
    video_client = VideoClient(server_ip)
    video_client.run()
