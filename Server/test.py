import socket
import json
import bcrypt
import logging
import threading
from connectz import create_connection
import mysql.connector

AUTH_SERVER_PORT = 6001
BUFFER_SIZE = 4096
ENCODING = 'utf-8'

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def signup(client_socket, data):
    """Process user registration from the client."""
    _, firstname, lastname, email, password, confirm_password = data.split(',')

    if not all([firstname, lastname, email, password, confirm_password]):
        response = "error,All fields are required"
        client_socket.sendall(response.encode(ENCODING))
        return

    if password != confirm_password:
        response = "error,Passwords do not match"
        client_socket.sendall(response.encode(ENCODING))
        return

    hashed_password = bcrypt.hashpw(password.encode(ENCODING), bcrypt.gensalt()).decode(ENCODING)

    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO account (firstname, lastname, email, password) VALUES (%s, %s, %s, %s)", 
                           (firstname, lastname, email, hashed_password))
            connection.commit()
            response = "success,New account created successfully"
            client_socket.sendall(response.encode(ENCODING))
        except mysql.connector.IntegrityError:
            response = "error,Email already exists"
            client_socket.sendall(response.encode(ENCODING))
        except Exception as e:
            response = f"error,Database error: {str(e)}"
            client_socket.sendall(response.encode(ENCODING))
        finally:
            cursor.close()
            connection.close()
    else:
        response = "error,Could not connect to database"
        client_socket.sendall(response.encode(ENCODING))

def login(client_socket, email, password):
    """Process user login."""
    if not email or not password:
        response = {"error": "All fields are required"}
        client_socket.sendall(json.dumps(response).encode(ENCODING))
        return

    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT id, password FROM account WHERE email=%s", (email,))
            result = cursor.fetchone()

            if result:
                user_id, stored_password = result
                if bcrypt.checkpw(password.encode(ENCODING), stored_password.encode(ENCODING)):
                    response = {"status": "SUCCESS", "user_id": user_id}
                else:
                    response = {"error": "Invalid Email or Password"}
            else:
                response = {"error": "No account found with that email"}

            client_socket.sendall(json.dumps(response).encode(ENCODING))
        except Exception as e:
            response = {"error": f"Database error: {str(e)}"}
            client_socket.sendall(json.dumps(response).encode(ENCODING))
        finally:
            cursor.close()
            connection.close()
    else:
        response = {"error": "Could not connect to the database"}
        client_socket.sendall(json.dumps(response).encode(ENCODING))

def change_password(client_socket, request_data):
    """Process password change requests."""
    try:
        _, email, new_password = request_data.split(',')

        if not email or not new_password:
            response = {"error": "All fields are required"}
            client_socket.sendall(json.dumps(response).encode(ENCODING))
            return

        db = create_connection()
        if db:
            try:
                cursor = db.cursor()
                cursor.execute("SELECT * FROM account WHERE email=%s", (email,))
                row = cursor.fetchone()

                if row is None:
                    response = {"error": "Email does not exist"}
                    client_socket.sendall(json.dumps(response).encode(ENCODING))
                else:
                    hashed_password = bcrypt.hashpw(new_password.encode(ENCODING), bcrypt.gensalt()).decode(ENCODING)
                    cursor.execute('UPDATE account SET password=%s WHERE email=%s', (hashed_password, email))
                    db.commit()
                    response = {"status": "success", "message": "Password changed successfully"}
                    client_socket.sendall(json.dumps(response).encode(ENCODING))
            except Exception as es:
                response = {"error": f"Database error: {str(es)}"}
                client_socket.sendall(json.dumps(response).encode(ENCODING))
            finally:
                cursor.close()
                db.close()
        else:
            response = {"error": "Could not connect to the database"}
            client_socket.sendall(json.dumps(response).encode(ENCODING))
    except Exception as es:
        response = {"error": f"Request processing error: {str(es)}"}
        client_socket.sendall(json.dumps(response).encode(ENCODING))

def handle_client(client_socket):
    """Handle incoming requests from clients."""
    logging.info("Handling request from client")
    try:
        request_data = client_socket.recv(BUFFER_SIZE).decode(ENCODING)
        logging.info(f"Request data: {request_data}")

        request_type, *data = request_data.split(',')

        if request_type == 'REGISTER':
            logging.info("Handling REGISTER")
            signup(client_socket, request_data)
        elif request_type == 'LOGIN':
            logging.info("Handling LOGIN")
            login(client_socket, data[0], data[1])
        elif request_type == 'FORGOT_PASSWORD':
            logging.info("Handling FORGOT_PASSWORD")
            change_password(client_socket, request_data)
        else:
            response = {"status": "error", "message": "Invalid request type"}
            client_socket.sendall(json.dumps(response).encode(ENCODING))
    except Exception as e:
        response = {"status": "error", "message": f"An error occurred: {str(e)}"}
        logging.error(f"Error handling request: {response}")
        client_socket.sendall(json.dumps(response).encode(ENCODING))
    finally:
        client_socket.close()

def start_auth_server():
    """Start the authentication server."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', AUTH_SERVER_PORT))
    server_socket.listen(5)
    logging.info(f"Auth Server is running on port {AUTH_SERVER_PORT}...")

    try:
        while True:
            client_socket, addr = server_socket.accept()
            logging.info(f"Connection from {addr}")
            threading.Thread(target=handle_client, args=(client_socket,)).start()
    except KeyboardInterrupt:
        logging.info("Auth Server is shutting down...")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_auth_server()
