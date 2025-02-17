import mysql.connector
from mysql.connector import Error

def create_connection():
    """Tạo và trả về kết nối CSDL."""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",  # Đặt mật khẩu của bạn ở đây
            database="ltm"
        )
        if connection.is_connected():
            print("Connected to MySQL database")
            return connection
    except Error as e:
        print(f"Error: {e}")
        return None

# Kiểm tra kết nối
if __name__ == "__main__":
    conn = create_connection()
    if conn:
        conn.close()
