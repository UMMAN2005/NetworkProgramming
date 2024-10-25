import os
import socket
import threading
import socketserver

HOST = "localhost"
PORT = 0
BUFFER_SIZE = 1024


def client(ip: str, port: int, message: str) -> None:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    try:
        sock.sendall(message.encode("utf-8"))
        response = sock.recv(BUFFER_SIZE)
        print(f"Client received: {response.decode('utf-8')}")
    finally:
        sock.close()


class RequestHandler(socketserver.BaseRequestHandler):
    def handle(self) -> None:
        data = self.request.recv(BUFFER_SIZE)
        current_thread = threading.current_thread()
        response = f"{current_thread.name}: {data.decode('utf-8')}"
        self.request.sendall(response.encode("utf-8"))


class ThreadedServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


if __name__ == "__main__":
    server = ThreadedServer((HOST, PORT), RequestHandler)
    ip, port = server.server_address

    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    print(f"Server loop running on thread: {server_thread.name}")

    client(ip, port, "Hello from client 1")
    client(ip, port, "Hello from client 2")
    client(ip, port, "Hello from client 3")

    server.shutdown()
