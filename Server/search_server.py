import socket
import mysql.connector
import json
import logging
import threading
from connectz import create_connection

SEARCH_SERVER_PORT = 6002
BUFFER_SIZE = 4096
ENCODING = 'utf-8'

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def search_friends_in_db(friend_name):
    """Search for friends in the database by name."""
    try:
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        query = '''
        SELECT id, firstname, lastname
        FROM account
        WHERE firstname LIKE %s OR lastname LIKE %s
        '''
        cursor.execute(query, (f'%{friend_name}%', f'%{friend_name}%'))
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        logging.info(f"Search results for '{friend_name}': {results}")
        return results
    except Exception as e:
        logging.error(f"Database query error: {e}")
        return []

def handle_client(client_socket):
    """Handle incoming requests from clients."""
    logging.info("Handling request from client")
    try:
        request_data = client_socket.recv(BUFFER_SIZE).decode(ENCODING)
        logging.info(f"Received request data: {request_data}")

        # Parse the request type
        request_type, *data = request_data.split(',')

        if request_type == "SEARCH":
            logging.info("<=== Handling SEARCH ===>")
            friend_name = data[0].strip()

            # Search in database
            results = search_friends_in_db(friend_name)
            response = json.dumps(results if results else {"error": "No friends found."})
            client_socket.sendall(response.encode(ENCODING))
            logging.info("Sent search results to client")
        else:
            # Send error for unknown request types
            response = json.dumps({"status": "error", "message": "Invalid request type"})
            client_socket.sendall(response.encode(ENCODING))
    except Exception as e:
        error_response = json.dumps({"status": "error", "message": f"An error occurred: {str(e)}"})
        logging.error(f"Error handling request: {error_response}")
        client_socket.sendall(error_response.encode(ENCODING))
    finally:
        client_socket.close()

def start_search_server():
    """Start the search server."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', SEARCH_SERVER_PORT))
    server_socket.listen(5)
    logging.info(f"Search Server is running on port {SEARCH_SERVER_PORT}...")

    try:
        while True:
            client_socket, addr = server_socket.accept()
            logging.info(f"Connection from {addr}")
            threading.Thread(target=handle_client, args=(client_socket,)).start()
    except KeyboardInterrupt:
        logging.info("Search Server is shutting down...")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_search_server()
