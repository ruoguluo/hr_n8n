#!/usr/bin/env python3
import http.server
import socketserver
import os
import sys

# Configuration
PORT = 8001
DIRECTORY = "html"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

def main():
    # Change to the project directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Check if html directory exists
    if not os.path.exists(DIRECTORY):
        print(f"Error: Directory '{DIRECTORY}' not found!")
        sys.exit(1)
    
    # Start the server
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Serving HTML files from '{DIRECTORY}' directory")
        print(f"Server running at http://localhost:{PORT}/")
        print("Press Ctrl+C to stop the server")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")

if __name__ == "__main__":
    main()