import os
import socket
import threading
import socketserver

HOST = "localhost"
PORT = 0
BUFFER_SIZE = 1024
MESSAGE = "Hello echo server!"


class Client:
    def __init__(self, ip: str, port: int) -> None:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((ip, port))

    def execute(self) -> None:
        pid = os.getpid()
        print(f'PID {pid} Sending message to server: "{MESSAGE}"')
        sent_length = self.socket.send(MESSAGE.encode("utf-8"))
        print(f"Sent: {sent_length} characters, so far...")

        response = self.socket.recv(BUFFER_SIZE)
        print(f'PID {pid} received: {response[5:].decode("utf-8")}')

    def close(self) -> None:
        self.socket.close()


class ServerHandler(socketserver.BaseRequestHandler):
    def handle(self) -> None:
        data = self.request.recv(BUFFER_SIZE).decode("utf-8")
        pid = os.getpid()
        response = f"{pid}: {data}"
        print(f"Server sending response [PID: data] = [{response}]")
        self.request.send(response.encode("utf-8"))


class Server(socketserver.ForkingMixIn, socketserver.TCPServer):
    pass


def main() -> None:
    server = Server((HOST, PORT), ServerHandler)
    ip, port = server.server_address
    thread = threading.Thread(target=server.serve_forever)
    thread.setDaemon(True)
    thread.start()
    print(f"Server loop running PID: {os.getpid()}")

    client1 = Client(ip, port)
    client1.execute()
    print("First client running")

    client2 = Client(ip, port)
    client2.execute()
    print("Second client running")

    client1.close()
    client2.close()
    server.shutdown()
    server.server_close()


if __name__ == "__main__":
    main()
