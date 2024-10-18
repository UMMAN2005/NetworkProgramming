import socket


def scan_tcp_port(ip, port) -> bool:
    """Check if a TCP server is running by attempting to connect."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_sock:
            tcp_sock.settimeout(1)
            tcp_sock.connect((ip, port))
            return True
    except (socket.timeout, ConnectionRefusedError):
        return False
    except socket.error:
        return False


def scan_udp_port(ip, port) -> bool:
    """Check if a UDP server is running by sending a ping message."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(1)  # Set timeout for response
        server_address = (ip, port)

        # Send a "ping" message
        sock.sendto(b"ping", server_address)

        # Expect a "pong" response
        data, server = sock.recvfrom(1024)
        if data.decode("utf-8") == "pong":
            return True
        return False
    except socket.timeout:
        return False
    except socket.error as e:
        return False
    finally:
        sock.close()


def is_valid_ip(ip) -> bool:
    """Validate the IP address format (IPv4)."""
    try:
        socket.inet_aton(ip)
        return True
    except socket.error:
        return False


def is_valid_port(port):  # -> Any:
    """Check if the port is a valid integer and within the range of 1-65535."""
    return 1 <= port <= 65535


def find_available_port(ip, port, protocol="tcp"):  # Added protocol argument
    """Find the next available port if the default one is in use."""
    while True:
        try:
            if protocol == "tcp":
                # Check for TCP availability
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            elif protocol == "udp":
                # Check for UDP availability
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            else:
                raise ValueError("Invalid protocol specified. Use 'tcp' or 'udp'.")

            sock.bind((ip, port))
            sock.close()
            return port
        except OSError:
            # Increment port number if it's in use and try again
            port += 1
            continue
