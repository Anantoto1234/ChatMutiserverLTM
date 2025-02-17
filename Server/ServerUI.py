import socket
import threading
import json
import logging
import subprocess
import os

# Configuration for each microservice server port
AUTH_SERVER_PORT = 6001
SEARCH_SERVER_PORT = 6002
UPLOAD_SERVER_PORT = 6003
FRIEND_SERVER_PORT = 6004
CHAT_SERVER_PORT =6005
BUFFER_SIZE = 4096
ENCODING = 'utf-8'
GATEWAY_PORT = 12345

logging.basicConfig(level=logging.INFO)

# Start the microservice processes if they aren’t already running
def start_service(script_name, port):
    """Start a microservice in a new subprocess if it's not already running."""
    try:
        # Start each script as a subprocess
        subprocess.Popen(["python", script_name], close_fds=True)
        logging.info(f"{script_name} started on port {port}.")
    except Exception as e:
        logging.error(f"Failed to start {script_name}: {e}")

# Initialize the microservices
def initialize_microservices():
    """Initialize all required microservices."""
    services = {
        "auth_server.py": AUTH_SERVER_PORT,
        "search_server.py": SEARCH_SERVER_PORT,
        "upload_server.py": UPLOAD_SERVER_PORT,
        "friend_server.py": FRIEND_SERVER_PORT,
        "chat_server.py":CHAT_SERVER_PORT,
    }
    for script, port in services.items():
        start_service(script, port)

def forward_request(data, server_port):
    """Forward the client request to the specified microservice."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.connect(('localhost', server_port))
            server_socket.sendall(data.encode(ENCODING))
            response = server_socket.recv(BUFFER_SIZE).decode(ENCODING)
        return response
    except (ConnectionError, socket.error) as e:
        logging.error(f"Could not connect to server on port {server_port}: {e}")
        return json.dumps({"status": "error", "message": "Service unavailable"})

def handle_client(client_socket):
    """Handle incoming client request and forward to the appropriate service."""
    try:
        request = client_socket.recv(BUFFER_SIZE).decode(ENCODING)
        logging.info(f"Received request: {request}")

        # Parse the request type to determine which service should handle it
        request_type = request.split(',')[0]
        
        if request_type in ["REGISTER", "LOGIN", "FORGOT_PASSWORD"]:
            response = forward_request(request, AUTH_SERVER_PORT)
        elif request_type == "SEARCH":
            response = forward_request(request, SEARCH_SERVER_PORT)
        elif request_type in ["UPLOAD_IMAGE"]:
            response (request, UPLOAD_SERVER_PORT)
        elif request_type in ["GET_FRIEND_LIST", "ACCEPT_FRIEND_REQUEST", "DECLINE_FRIEND_REQUEST","REMOVE_FRIEND"]:
            response = forward_request(request, FRIEND_SERVER_PORT)   
        elif request_type in ["GET_CONTACTS_AND_GROUPS", "GET_MESSAGES","SEND_MESSAGE","GET_PROFILE_IMAGE","GET_OR_CREATE_CONVERSATION","CREATE_GROUP_CONVERSATION","SEND_EMOJI","REGISTERR"]:
            response = forward_request(request, FRIEND_SERVER_PORT)  
        else:
            response = json.dumps({"status": "error", "message": "Unknown request type"})

        client_socket.sendall(response.encode(ENCODING))
    except Exception as e:
        logging.error(f"Error while handling client request: {e}")
        client_socket.sendall(json.dumps({"status": "error", "message": "Failed to process request"}).encode(ENCODING))
    finally:
        client_socket.close()

def start_gateway():
    """Start the gateway server to listen for client connections."""
    gateway_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        gateway_socket.bind(("127.0.0.1", GATEWAY_PORT))
        gateway_socket.listen(5)
        logging.info(f"API Gateway is running on 127.0.0.1 port {GATEWAY_PORT}...")
        
        initialize_microservices()  # Ensure microservices are running

        while True:
            client_socket, addr = gateway_socket.accept()
            logging.info(f"Connected by {addr}")
            threading.Thread(target=handle_client, args=(client_socket,)).start()
    except Exception as e:
        logging.error(f"Error starting the gateway: {e}")
    finally:
        gateway_socket.close()

if __name__ == "__main__":
    start_gateway()
