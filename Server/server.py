import os
import socket
import json
import threading
import base64
import mysql.connector
from connectz import create_connection  # Ensure this connection utility is implemented correctly


# Server configuration
HOST = '127.0.0.1'
CHAT_SERVER_PORT = 6005
BUFFER_SIZE = 4096
ENCODING = 'utf-8'


def handle_client(client_socket):
    try:
        # Receive request data
        request = client_socket.recv(BUFFER_SIZE).decode(ENCODING)
        request_data = json.loads(request)

        # Process the request based on request type
        request_type = request_data.get("request_type")
        if request_type == "GET_CONTACTS":
            response = get_contacts(request_data["user_id"])
        elif request_type == "GET_MESSAGES":
            response = get_messages(request_data["conversation_id"])
        elif request_type == "SEND_MESSAGE":
            response = send_message(request_data["conversation_id"], request_data["sender_id"], request_data["message"])
        elif request_type == "GET_PROFILE_IMAGE":
            response = get_profile_image(request_data["user_id"])
        else:
            response = {"status": "ERROR", "message": "Invalid request type"}
        
        # Send response to client
        client_socket.sendall(json.dumps(response).encode(ENCODING))
    except Exception as e:
        print(f"Error handling request: {e}")
        response = {"status": "ERROR", "message": f"Error: {str(e)}"}
        client_socket.sendall(json.dumps(response).encode(ENCODING))
    finally:
        client_socket.close()
        
def get_contacts(user_id):
    try:
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        
        # SQL query to get contacts with profile picture paths
        query = """
            SELECT a.id AS user_id, a.firstname, a.lastname, i.image_path
            FROM friends f
            JOIN account a ON f.friend_id = a.id
            LEFT JOIN images i ON i.user_id = a.id AND i.image_type = 'profile_picture'
            WHERE f.user_id = %s AND f.status = 'accepted'
        """
        
        # Execute the query
        cursor.execute(query, (user_id,))
        contacts = cursor.fetchall()
        
        # Process image paths
        for contact in contacts:
            if contact["image_path"]:
                # Only prepend UPLOAD_FOLDER if it's not already in the path
                if not contact["image_path"].startswith:
                    contact["image_path"] = os.path.join( contact["image_path"])
            else:
                # Set a default placeholder image if no profile picture exists
                contact["image_path"] = os.path.join("default_profile.png")

        # Debugging statement
        print("Contacts with images:", contacts)
        
        return {"status": "SUCCESS", "contacts": contacts}
    except mysql.connector.Error as e:
        print(f"Database error: {e}")
        return {"status": "ERROR", "message": "Failed to retrieve contacts"}
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()



def get_messages(conversation_id):
    try:
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT sender_id, message, sent_at
            FROM messages
            WHERE conversation_id = %s
            ORDER BY sent_at ASC
        """
        cursor.execute(query, (conversation_id,))
        messages = cursor.fetchall()
        return {"status": "SUCCESS", "messages": messages}
    except mysql.connector.Error as e:
        print(f"Database error: {e}")
        return {"status": "ERROR", "message": "Failed to retrieve messages"}
    finally:
        cursor.close()
        conn.close()

def send_message(conversation_id, sender_id, message):
    try:
        conn = create_connection()
        cursor = conn.cursor()
        query = """
            INSERT INTO messages (conversation_id, sender_id, message, sent_at)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (conversation_id, sender_id, message, datetime.now()))
        conn.commit()
        return {"status": "SUCCESS", "message": "Message sent successfully"}
    except mysql.connector.Error as e:
        print(f"Database error: {e}")
        return {"status": "ERROR", "message": "Failed to send message"}
    finally:
        cursor.close()
        conn.close()

def get_profile_image(user_id):
    try:
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT image_path
            FROM images
            WHERE user_id = %s AND image_type = 'profile_picture'
        """
        cursor.execute(query, (user_id,))
        image = cursor.fetchone()
        if image and image["image_path"]:
            image["image_path"] = os.path.join(image["image_path"])
            return {"status": "SUCCESS", "image_path": image["image_path"]}
        else:
            return {"status": "SUCCESS", "image_path": None}
    except mysql.connector.Error as e:
        print(f"Database error: {e}")
        return {"status": "ERROR", "message": "Failed to retrieve profile image"}
    finally:
        cursor.close()
        conn.close()

def start_server():
    """Start the server to listen for client connections."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, CHAT_SERVER_PORT))
    server_socket.listen(5)
    print(f"Server listening on {HOST}:{CHAT_SERVER_PORT}")

    try:
        while True:
            client_socket, _ = server_socket.accept()
            threading.Thread(target=handle_client, args=(client_socket,)).start()
    except KeyboardInterrupt:
        print("Server shutting down.")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_server()
