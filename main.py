from app import create_server


# Create a new instance of the SmartFeeder server
# This initializes the Flask application, registers routes,
# sets up socket events, and initializes the database
server = create_server()


# Export the Flask application instance for use with WSGI servers
app = server.app


if __name__ == "__main__":
    # Only run the server directly when this file is executed as a script
    # Flask-SocketIO will use host and port settings from the config
    server.run()
