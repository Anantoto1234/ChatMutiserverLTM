import os
import socket
import json
import threading
import mysql.connector
from datetime import datetime
from connectz import create_connection
# Server configuration
HOST = '127.0.0.1'
CHAT_SERVER_PORT = 6005
BUFFER_SIZE = 4096
ENCODING = 'utf-8'

# Default profile image path
DEFAULT_PROFILE_IMAGE = "default_profile.png"

# Function to create a MySQL database connection

# Main request handler function for each client
def handle_client(client_socket):
    try:
        request = client_socket.recv(BUFFER_SIZE).decode(ENCODING)
        request_data = json.loads(request)
        request_type = request_data.get("request_type")

        print(f"[DEBUG] Received request type: {request_type}")

        response = {}

        if request_type == "GET_CONTACTS_AND_GROUPS":
            response = get_contacts_and_groups(request_data["user_id"])
        elif request_type == "GET_OR_CREATE_CONVERSATION":
            response = get_or_create_conversation(request_data["user_id"], request_data["friend_id"])
        elif request_type == "CREATE_GROUP_CONVERSATION":
            response = create_group_conversation(request_data["user_id"], request_data["group_name"], request_data["member_ids"])
        elif request_type == "GET_MESSAGES":
            response = get_messages(request_data["conversation_id"], request_data.get("since"))
        elif request_type == "SEND_MESSAGE":
            response = send_message(request_data["conversation_id"], request_data["sender_id"], request_data["message"])
        elif request_type == "GET_PROFILE_IMAGE":
            print("[DEBUG] Calling get_profile_image function")
            response = get_profile_image(request_data["user_id"])
        else:
            response = {"status": "ERROR", "message": "Invalid request type"}

        client_socket.sendall(json.dumps(response).encode(ENCODING))
    except Exception as e:
        print(f"[ERROR] Error handling request: {e}")
    finally:
        client_socket.close()

# Function to fetch contacts and groups
def get_contacts_and_groups(user_id):
    try:
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)

        # Fetch individual contacts
        query_contacts = """
            SELECT a.id AS user_id, a.firstname, a.lastname, COALESCE(i.image_path, %s) AS image_path, FALSE AS is_group_chat
            FROM friends f
            JOIN account a ON f.friend_id = a.id
            LEFT JOIN images i ON i.user_id = a.id AND i.image_type = 'profile_picture'
            WHERE f.user_id = %s AND f.status = 'accepted'
        """
        cursor.execute(query_contacts, (DEFAULT_PROFILE_IMAGE, user_id))
        contacts = cursor.fetchall()

        # Fetch group chats
        query_groups = """
            SELECT c.id AS id, c.group_name AS name, TRUE AS is_group_chat
            FROM conversations c
            JOIN participants p ON c.id = p.conversation_id
            WHERE p.user_id = %s AND c.is_group_chat = TRUE
        """
        cursor.execute(query_groups, (user_id,))
        groups = cursor.fetchall()

        return {"status": "SUCCESS", "contacts": contacts + groups}
    except mysql.connector.Error as e:
        print(f"[ERROR] Database error: {e}")
        return {"status": "ERROR", "message": "Failed to retrieve contacts and groups"}
    finally:
        cursor.close()
        conn.close()

# Function to get or create a one-on-one conversation
def get_or_create_conversation(user_id, friend_id):
    try:
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)

        # Check if a conversation already exists between the two users
        query = """
            SELECT c.id FROM conversations c
            JOIN participants p1 ON c.id = p1.conversation_id
            JOIN participants p2 ON c.id = p2.conversation_id
            WHERE p1.user_id = %s AND p2.user_id = %s AND c.is_group_chat = FALSE
            LIMIT 1
        """
        cursor.execute(query, (user_id, friend_id))
        conversation = cursor.fetchone()

        if conversation:
            return {"status": "SUCCESS", "conversation_id": conversation["id"]}

        # Create a new conversation if one does not exist
        insert_conversation_query = "INSERT INTO conversations (is_group_chat, created_at) VALUES (FALSE, NOW())"
        cursor.execute(insert_conversation_query)
        conn.commit()
        new_conversation_id = cursor.lastrowid

        # Add both users as participants
        insert_participants_query = """
            INSERT INTO participants (conversation_id, user_id, joined_at)
            VALUES (%s, %s, NOW()), (%s, %s, NOW())
        """
        cursor.execute(insert_participants_query, (new_conversation_id, user_id, new_conversation_id, friend_id))
        conn.commit()

        return {"status": "SUCCESS", "conversation_id": new_conversation_id}
    except mysql.connector.Error as e:
        print(f"[ERROR] Database error: {e}")
        return {"status": "ERROR", "message": "Failed to retrieve or create conversation"}
    finally:
        cursor.close()
        conn.close()

# Function to create a new group conversation
def create_group_conversation(user_id, group_name, member_ids):
    try:
        conn = create_connection()
        cursor = conn.cursor()

        # Insert the new group conversation
        insert_conversation_query = "INSERT INTO conversations (is_group_chat, group_name, created_at) VALUES (TRUE, %s, NOW())"
        cursor.execute(insert_conversation_query, (group_name,))
        conn.commit()
        group_conversation_id = cursor.lastrowid

        # Add the creator and other members as participants
        insert_participant_query = "INSERT INTO participants (conversation_id, user_id, joined_at) VALUES (%s, %s, NOW())"
        
        # Add creator
        cursor.execute(insert_participant_query, (group_conversation_id, user_id))
        
        # Add other members
        for member_id in member_ids:
            cursor.execute(insert_participant_query, (group_conversation_id, member_id))
        
        conn.commit()

        return {"status": "SUCCESS", "conversation_id": group_conversation_id}
    except mysql.connector.Error as e:
        print(f"[ERROR] Database error: {e}")
        return {"status": "ERROR", "message": "Failed to create group conversation"}
    finally:
        cursor.close()
        conn.close()

# Function to fetch messages
def get_messages(conversation_id, since=None):
    """Fetch messages after a specific timestamp."""
    try:
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT m.id, m.sender_id, a.firstname AS sender_name, m.message, m.sent_at,
                   COALESCE(i.image_path, %s) AS image_path
            FROM messages m
            JOIN account a ON m.sender_id = a.id
            LEFT JOIN images i ON m.sender_id = i.user_id AND i.image_type = 'profile_picture'
            WHERE m.conversation_id = %s
        """
        params = [DEFAULT_PROFILE_IMAGE, conversation_id]
        if since:
            query += " AND m.sent_at > %s"
            params.append(since)
        query += " ORDER BY m.sent_at ASC"

        cursor.execute(query, params)
        messages = cursor.fetchall()

        formatted_messages = [
            {
                "id": msg["id"],
                "sender_id": msg["sender_id"],
                "sender_name": msg["sender_name"],
                "content": msg["message"],
                "timestamp": msg["sent_at"].strftime("%Y-%m-%d %H:%M:%S"),
                "image_path": msg["image_path"]
            } for msg in messages
        ]

        return {"status": "SUCCESS", "messages": formatted_messages}
    except mysql.connector.Error as e:
        print(f"Database error: {e}")
        return {"status": "ERROR", "message": "Failed to retrieve messages"}
    finally:
        cursor.close()
        conn.close()


# Function to fetch profile image path
def get_profile_image(user_id):
    try:
        
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Query to fetch the image path from the database
        query = """
            SELECT COALESCE(image_path, %s) AS image_path
            FROM images
            WHERE user_id = %s AND image_type = 'profile_picture'
        """
        print("query ",query,user_id)
        cursor.execute(query, (DEFAULT_PROFILE_IMAGE, user_id))
        image = cursor.fetchone()
        
        # Extract the filename or full relative path
        if image and image["image_path"]:
            image_path = image["image_path"]
            print(f"[DEBUG] Retrieved image path from database: {image_path}")
        else:
            image_path = DEFAULT_PROFILE_IMAGE
            print(f"[DEBUG] Using default image path: {image_path}")
        
        # Confirm final path sent to the client
        print(f"[DEBUG] Final image path sent to client: {image_path}")
        
        return {"status": "SUCCESS", "image_path": image_path}
    except mysql.connector.Error as e:
        print(f"[ERROR] Database error: {e}")
        return {"status": "ERROR", "message": "Failed to retrieve profile image"}
    finally:
        cursor.close()
        conn.close()

# Function to send a message
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
        print(f"[ERROR] Database error: {e}")
        return {"status": "ERROR", "message": "Failed to send message"}
    finally:
        cursor.close()
        conn.close()

# Function to start the server
def start_server():
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
