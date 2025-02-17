import socket
import mysql.connector
import base64
import json
import os
import logging
import threading
from connectz import create_connection  # Ensure this connection utility is implemented correctly

# Constants
UPLOAD_SERVER_PORT = 6003
BUFFER_SIZE = 4096
ENCODING = 'utf-8'
UPLOAD_FOLDER = 'uploads'
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def save_image_from_base64(image_base64, file_path):
    """Save base64 image data to a file."""
    try:
        image_data = base64.b64decode(image_base64)
        with open(file_path, "wb") as image_file:
            image_file.write(image_data)
        logging.info(f"Image saved at {file_path}")
    except Exception as e:
        logging.error(f"Failed to decode Base64 data: {e}")
        raise ValueError("Failed to decode Base64 data")

def upload_image(client_socket, request):
    """Handle image upload from the client."""
    user_id = request.get("user_id")
    filename = request.get("filename")
    image_type = request.get("image_type")
    base64_image = request.get("base64_data")

    if not user_id or not filename or not image_type or not base64_image:
        response = {"status": "error", "message": "Missing required fields"}
        client_socket.sendall(json.dumps(response).encode(ENCODING))
        return

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    file_path = os.path.join(UPLOAD_FOLDER, f"{user_id}_{filename}")
    try:
        save_image_from_base64(base64_image, file_path)
    except ValueError as e:
        response = {"status": "error", "message": str(e)}
        client_socket.sendall(json.dumps(response).encode(ENCODING))
        return

    db = create_connection()
    if db:
        try:
            cursor = db.cursor()
            cursor.execute(
                "INSERT INTO images (user_id, image_type, image_path) VALUES (%s, %s, %s) "
                "ON DUPLICATE KEY UPDATE image_path = VALUES(image_path)",
                (user_id, image_type, file_path)
            )
            db.commit()
            response = {"status": "SUCCESS", "message": "Image uploaded successfully"}
            logging.info("Image successfully saved and database updated.")
        except mysql.connector.Error as db_err:
            response = {"status": "error", "message": f"Database error: {db_err}"}
            logging.error(f"Database error: {db_err}")
        finally:
            cursor.close()
            db.close()
    else:
        response = {"status": "error", "message": "Failed to connect to database"}
        logging.error("Database connection failed.")
    
    client_socket.sendall(json.dumps(response).encode(ENCODING))


def handle_client(client_socket):
    """Handle incoming requests from clients."""
    try:
        received_data = ""
        while True:
            chunk = client_socket.recv(BUFFER_SIZE).decode(ENCODING)
            if not chunk:
                break
            received_data += chunk
            if "\n" in received_data:
                break

        request_data = received_data.strip()
        logging.info(f"Received request: {request_data[:100]}...")

        try:
            request = json.loads(request_data)
        except json.JSONDecodeError:
            response = {"status": "error", "message": "Invalid JSON format"}
            client_socket.sendall(json.dumps(response).encode(ENCODING))
            return

        request_type = request.get("request_type")
        if request_type == 'UPLOAD_IMAGE':
            logging.info("Handling UPLOAD_IMAGE request")
            upload_image(client_socket, request)
        
        else:
            response = {"status": "error", "message": "Invalid request type"}
            client_socket.sendall(json.dumps(response).encode(ENCODING))
    except Exception as e:
        response = {"status": "error", "message": f"An unexpected error occurred: {str(e)}"}
        logging.error(f"Error handling request: {response}")
        client_socket.sendall(json.dumps(response).encode(ENCODING))
    finally:
        client_socket.close()

def start_upload_server():
    """Start the upload server."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', UPLOAD_SERVER_PORT))
    server_socket.listen(5)
    logging.info(f"Upload Server is running on port {UPLOAD_SERVER_PORT}...")

    try:
        while True:
            client_socket, addr = server_socket.accept()
            logging.info(f"Connection from {addr}")
            threading.Thread(target=handle_client, args=(client_socket,)).start()
    except KeyboardInterrupt:
        logging.info("Upload Server is shutting down...")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_upload_server()
