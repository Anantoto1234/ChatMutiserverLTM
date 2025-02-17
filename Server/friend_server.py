import socket
import threading
import json
import mysql.connector
from connectz import create_connection

FRIEND_SERVER_HOST = "127.0.0.1"
FRIEND_SERVER_PORT = 6004
ENCODING = 'utf-8'
BUFFER_SIZE = 4096

def handle_client(client_socket):
    """Handles incoming client requests."""
    try:
        request_data = client_socket.recv(BUFFER_SIZE).decode(ENCODING)
        request = json.loads(request_data)
        response = {}

        if "user_id" not in request:
            response = {"status": "ERROR", "message": "Missing 'user_id' in request"}
        else:
            user_id = request["user_id"]
            
            if request["request_type"] == "GET_FRIEND_LIST":
                response = get_friend_list(user_id)
            elif request["request_type"] == "ACCEPT_FRIEND_REQUEST":
                if "friend_id" in request:
                    response = update_friend_status(user_id, request["friend_id"], "accepted")
                else:
                    response = {"status": "ERROR", "message": "Missing 'friend_id' in request"}
            elif request["request_type"] == "DECLINE_FRIEND_REQUEST":
                if "friend_id" in request:
                    response = update_friend_status(user_id, request["friend_id"], "declined")
                else:
                    response = {"status": "ERROR", "message": "Missing 'friend_id' in request"}
            elif request["request_type"] == "REMOVE_FRIEND":
                if "friend_id" in request:
                    response = remove_friend(user_id, request["friend_id"])
                else:
                    response = {"status": "ERROR", "message": "Missing 'friend_id' in request"}
            else:
                response = {"status": "ERROR", "message": "Invalid request type"}

        client_socket.sendall(json.dumps(response).encode(ENCODING))
    except Exception as e:
        error_response = {"status": "ERROR", "message": str(e)}
        client_socket.sendall(json.dumps(error_response).encode(ENCODING))
    finally:
        client_socket.close()

def get_friend_list(user_id):
    """Fetches the friend list with names for a given user."""
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT f.friend_id, f.status, a.firstname, a.lastname
                FROM friends f
                JOIN account a ON f.friend_id = a.id
                WHERE f.user_id = %s
            """
            cursor.execute(query, (user_id,))
            friends = cursor.fetchall()
            
            # Format the friend's name for display
            for friend in friends:
                friend['name'] = f"{friend['firstname']} {friend['lastname']}"
                del friend['firstname']
                del friend['lastname']
            
            return {"status": "SUCCESS", "friends": friends}
        except Exception as e:
            return {"status": "ERROR", "message": str(e)}
        finally:
            cursor.close()
            connection.close()
    return {"status": "ERROR", "message": "Database connection failed"}

def update_friend_status(user_id, friend_id, status):
    """Updates the friend request status."""
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("UPDATE friends SET status = %s WHERE user_id = %s AND friend_id = %s", (status, user_id, friend_id))
            connection.commit()
            return {"status": "SUCCESS", "message": f"Friend request {status}"}
        except Exception as e:
            return {"status": "ERROR", "message": str(e)}
        finally:
            cursor.close()
            connection.close()
    return {"status": "ERROR", "message": "Database connection failed"}

def remove_friend(user_id, friend_id):
    """Removes a friend relationship."""
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM friends WHERE (user_id = %s AND friend_id = %s) OR (user_id = %s AND friend_id = %s)", (user_id, friend_id, friend_id, user_id))
            connection.commit()
            return {"status": "SUCCESS", "message": "Friend removed"}
        except Exception as e:
            return {"status": "ERROR", "message": str(e)}
        finally:
            cursor.close()
            connection.close()
    return {"status": "ERROR", "message": "Database connection failed"}

def start_server():
    """Starts the Friend Server."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((FRIEND_SERVER_HOST, FRIEND_SERVER_PORT))
    server.listen(5)
    print(f"Friend Server listening on {FRIEND_SERVER_HOST}:{FRIEND_SERVER_PORT}")

    try:
        while True:
            client_socket, _ = server.accept()
            threading.Thread(target=handle_client, args=(client_socket,)).start()
    except KeyboardInterrupt:
        print("Shutting down Friend Server...")
    finally:
        server.close()

if __name__ == "__main__":
    start_server()
