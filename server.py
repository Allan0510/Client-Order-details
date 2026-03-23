import http.server
import socketserver
import json
import os
import socket

# Force server to run in the folder where server.py and Index.html actually live
os.chdir(os.path.dirname(os.path.abspath(__file__)))

PORT = 8000
DATABASE_FILE = 'database.json'

class CRMRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

    def do_GET(self):
        if self.path == '/api/load':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            if os.path.exists(DATABASE_FILE):
                with open(DATABASE_FILE, 'r', encoding='utf-8') as f:
                    self.wfile.write(f.read().encode('utf-8'))
            else:
                self.wfile.write(b'[]')
        else:
            # Serve Index.html explicitly for the root
            if self.path == '/':
                self.path = '/Index.html'
            super().do_GET()

    def do_POST(self):
        if self.path == '/api/save':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                # Validate JSON before writing
                data = json.loads(post_data.decode('utf-8'))
                with open(DATABASE_FILE, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
                    
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"status": "success"}')
            except Exception as e:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(f'{{"error": "{str(e)}" }}'.encode())
        else:
            self.send_response(404)
            self.end_headers()

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

with socketserver.TCPServer(("0.0.0.0", PORT), CRMRequestHandler) as httpd:
    local_ip = get_local_ip()
    print("=" * 60)
    print(" 🚀 CLIENT VAULT SERVER IS RUNNING! 🚀 ")
    print("=" * 60)
    print(f"On THIS laptop, you can view the CRM at:")
    print(f"    http://localhost:{PORT}/")
    print(f"")
    print(f"On your PHONE or TABLET, make sure you are connected")
    print(f"to the same Wi-Fi, then open your browser to:")
    print(f"    http://{local_ip}:{PORT}/")
    print("=" * 60)
    print("(Press Ctrl+C inside this window to shut down the server)")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer shutting down. Goodbye!")
        httpd.server_close()
