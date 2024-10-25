import select
import socket
import sys
import signal
import pickle
import struct
import argparse

SERVER_HOST = "localhost"
CHAT_SERVER_NAME = "server"


def send(channel: socket.socket, *args: str) -> None:
    buffer_data = pickle.dumps(args)
    value = socket.htonl(len(buffer_data))
    size = struct.pack("L", value)
    channel.send(size)
    channel.send(buffer_data)


def receive(channel: socket.socket) -> str:
    size = struct.calcsize("L")
    size_data = channel.recv(size)
    try:
        size = socket.ntohl(struct.unpack("L", size_data)[0])
    except struct.error:
        return ""

    buf = b""
    while len(buf) < size:
        buf += channel.recv(size - len(buf))
    return pickle.loads(buf)[0]


class ChatServer:
    """An example chat server using select."""

    def __init__(self, port: int, backlog: int = 5) -> None:
        self.clients = 0
        self.clientmap = {}
        self.outputs = []  # List of output sockets
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((SERVER_HOST, port))
        print(f"Server listening to port: {port} ...")
        self.server.listen(backlog)
        # Catch keyboard interrupts
        signal.signal(signal.SIGINT, self.sighandler)

    def sighandler(self, signum, frame) -> None:
        """Clean up client outputs."""
        print("Shutting down server...")
        for output in self.outputs:
            output.close()
        self.server.close()

    def get_client_name(self, client: socket.socket) -> str:
        """Return the name of the client."""
        info = self.clientmap[client]
        host, name = info[0][0], info[1]
        return f"@{name}@{host}"

    def run(self) -> None:
        inputs = [self.server, sys.stdin]
        self.outputs = []
        running = True
        while running:
            try:
                readable, writeable, exceptional = select.select(
                    inputs, self.outputs, []
                )
            except select.error:
                break

            for sock in readable:
                if sock == self.server:
                    client, address = self.server.accept()
                    print(
                        f"Chat server: got connection {client.fileno()} from {address}"
                    )
                    cname = receive(client).split("NAME: ")[1]

                    self.clients += 1
                    send(client, f"CLIENT: {address[0]}")
                    inputs.append(client)
                    self.clientmap[client] = (address, cname)

                    msg = f"\n(Connected: New client ({self.clients}) from {self.get_client_name(client)})"
                    for output in self.outputs:
                        send(output, msg)
                    self.outputs.append(client)

                elif sock == sys.stdin:
                    sys.stdin.readline()
                    running = False
                else:
                    try:
                        data = receive(sock)
                        if data:
                            msg = f"\n#[{self.get_client_name(sock)}]>> {data}"
                            for output in self.outputs:
                                if output != sock:
                                    send(output, msg)
                        else:
                            print(f"Chat server: {sock.fileno()} hung up")
                            self.clients -= 1
                            sock.close()
                            inputs.remove(sock)
                            self.outputs.remove(sock)

                            msg = f"\n(Now hung up: Client from {self.get_client_name(sock)})"
                            for output in self.outputs:
                                send(output, msg)
                    except socket.error:
                        inputs.remove(sock)
                        self.outputs.remove(sock)
        self.server.close()


class ChatClient:
    """A command line chat client using select."""

    def __init__(self, name: str, port: int, host: str = SERVER_HOST) -> None:
        self.name = name
        self.connected = False
        self.host = host
        self.port = port
        self.prompt = f"[{self.name}@{socket.gethostname().split('.')[0]}> "

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((host, self.port))
            print(f"Now connected to chat server@ port {self.port}")
            self.connected = True
            send(self.sock, f"NAME: {self.name}")
            data = receive(self.sock)
            addr = data.split("CLIENT: ")[1]
            self.prompt = f"[{self.name}@{addr}]> "
        except socket.error:
            print(f"Failed to connect to chat server @ port {self.port}")
            sys.exit(1)

    def run(self) -> None:
        """Chat client main loop."""
        while self.connected:
            try:
                sys.stdout.write(self.prompt)
                sys.stdout.flush()
                readable, _, _ = select.select([0, self.sock], [], [])
                for sock in readable:
                    if sock == 0:
                        data = sys.stdin.readline().strip()
                        if data:
                            send(self.sock, data)
                    elif sock == self.sock:
                        data = receive(self.sock)
                        if not data:
                            print("Client shutting down.")
                            self.connected = False
                            break
                        else:
                            sys.stdout.write(data + "\n")
                            sys.stdout.flush()
            except KeyboardInterrupt:
                print("Client interrupted.")
                self.sock.close()
                break


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Socket Server Example with Select")
    parser.add_argument("--name", required=True, help="Name of the client or server.")
    parser.add_argument(
        "--port", type=int, required=True, help="Port number to connect to."
    )
    args = parser.parse_args()

    if args.name == CHAT_SERVER_NAME:
        server = ChatServer(args.port)
        server.run()
    else:
        client = ChatClient(name=args.name, port=args.port)
        client.run()
