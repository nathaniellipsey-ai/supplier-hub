import socket
import os

PORT = 9999
HOST = '127.0.0.1'

# Read the HTML file once
with open('index.html', 'rb') as f:
    html_content = f.read()

print(f'\n{"="*60}')
print(f'Simple Web Server')
print(f'{"="*60}')
print(f'Listening on http://{HOST}:{PORT}/index.html')
print(f'File size: {len(html_content)} bytes')
print(f'Press Ctrl+C to stop')
print(f'{"="*60}\n')

# Create socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((HOST, PORT))
sock.listen(1)

print(f'Server is listening on {HOST}:{PORT}...')

try:
    while True:
        client, addr = sock.accept()
        request = client.recv(4096).decode('utf-8', errors='ignore')
        
        # Parse the request
        if 'GET' in request:
            # Send HTTP response
            response = b'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: ' + str(len(html_content)).encode() + b'\r\nCache-Control: no-store\r\nAccess-Control-Allow-Origin: *\r\n\r\n' + html_content
            client.sendall(response)
        
        client.close()
except KeyboardInterrupt:
    print('\n\nServer stopped.')
finally:
    sock.close()
