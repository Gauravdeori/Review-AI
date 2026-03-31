import os
import subprocess
import threading
import http.server
import socketserver
import time

directory = r"c:\Users\NISHANKA\Desktop\wrk\New folder\files"
os.chdir(directory)

print("Bootstrapping React without NPM...")
# Run their existing JSX transpiler to build preview_app.html
subprocess.run(["python", "run_preview.py"])

PORT = 8080

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

def serve():
    try:
        with socketserver.TCPServer(("", PORT), QuietHandler) as httpd:
            print(f"Localhost web server actively running on port {PORT}...")
            httpd.serve_forever()
    except OSError:
        print(f"Port {PORT} already in use. Retrying...")

# Start server in background thread
server_thread = threading.Thread(target=serve, daemon=True)
server_thread.start()

# Give server time to bind
time.sleep(1)

# Launch localhost in Chrome!
url = f"http://localhost:{PORT}/preview_app.html"
print(f"Launching Chrome at {url} ...")
subprocess.Popen(["start", "chrome", url], shell=True)

# Keep alive briefly to serve files before script exits
time.sleep(5)
print("Preview broadcast complete!")
