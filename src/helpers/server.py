from helpers.checkers import *


def tcp_echo_client(ip, port, message):  # -> Any:
    """TCP Echo Client with protocol mismatch detection"""

    tcp_open = scan_tcp_port(ip, port)  # Scan for TCP server
    udp_open = scan_udp_port(ip, port)  # Scan for UDP server

    if not tcp_open and udp_open:
        print(
            f"Error: A UDP server is running on {ip}:{port}. Please use a UDP client."
        )
        return
    elif not tcp_open:
        print(f"Error: No TCP server is running on {ip}:{port}.")
        return

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (ip, port)
        print(f"Connecting to {ip} port {port}")
        sock.connect(server_address)

        try:
            print(f"Sending: {message}")
            sock.sendall(message.encode("utf-8"))

            amount_received = 0
            amount_expected = len(message)

            while amount_received < amount_expected:
                data = sock.recv(16)
                amount_received += len(data)
                print(f"Received: {data.decode('utf-8')}")
        except socket.error as e:
            print(f"Socket error during communication: {str(e)}")
        finally:
            print("Closing connection to the server")
            sock.close()

    except ConnectionRefusedError:
        print(f"Connection to {ip}:{port} refused. Is the TCP server running?")
    except socket.timeout:
        print(f"Connection to {ip}:{port} timed out.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


def tcp_echo_server(ip, port, stop_event=None) -> None:
    """TCP Echo Server"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.settimeout(1)  # Set a timeout of 1 second for non-blocking accept
    server_address = (ip, port)
    print(f"Starting up TCP echo server on {ip} port {port}")

    try:
        sock.bind(server_address)
        sock.listen(5)

        while stop_event is None or not stop_event.is_set():
            try:
                client, address = sock.accept()  # Accept connections
                client.settimeout(1)  # Non-blocking client communication
                try:
                    data = client.recv(2048)
                    if data:
                        print(f"Data: {data.decode('utf-8')}")
                        client.sendall(data)
                        print(f"Sent {len(data)} bytes back to {address}")
                except socket.timeout:
                    continue  # Handle client timeout and keep waiting
                except Exception as e:
                    print(f"Error during communication: {str(e)}")
                finally:
                    client.close()
            except socket.timeout:
                continue  # Continue loop if accept() times out
            except Exception as e:
                print(f"Server error: {str(e)}")
    except OSError as e:
        print(f"Error: Unable to bind to {ip}:{port}. It may already be in use.")
    finally:
        sock.close()
        print("TCP server closed.")


def udp_echo_client(ip, port, message):  # -> Any:
    """UDP Echo Client with protocol mismatch detection"""

    udp_open = scan_udp_port(ip, port)  # Scan for UDP server
    tcp_open = scan_tcp_port(ip, port)  # Scan for TCP server

    if not udp_open and tcp_open:
        print(
            f"Error: A TCP server is running on {ip}:{port}. Please use a TCP client."
        )
        return
    elif not udp_open:
        print(f"Error: No UDP server is running on {ip}:{port}.")
        return

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(5)  # Set a timeout of 5 seconds (adjustable)

        server_address = (ip, port)
        print(f"Sending to {ip} port {port}: {message}")

        try:
            sent = sock.sendto(message.encode("utf-8"), server_address)
            data, server = sock.recvfrom(2048)  # Waiting for the echo response
            print(f"Received: {data.decode('utf-8')}")
        except socket.timeout:
            print(f"UDP connection timed out. No response from {ip}:{port}.")
        except socket.error as e:
            if e.errno == 10054:  # Handle connection reset by peer (WinError)
                print(
                    f"UDP connection failed. The server might not be running, or a protocol mismatch occurred."
                )
            else:
                print(f"Socket error during communication: {str(e)}")
        finally:
            print("Closing connection to the server")
            sock.close()

    except ConnectionRefusedError:
        print(f"Connection to {ip}:{port} refused. Is the UDP server running?")
    except socket.timeout:
        print(f"Connection to {ip}:{port} timed out.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


def udp_echo_server(ip, port, stop_event=None) -> None:
    """UDP Echo Server"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = (ip, port)
    print(f"Starting up UDP echo server on {ip} port {port}")

    try:
        sock.bind(server_address)

        while stop_event is None or not stop_event.is_set():
            try:
                sock.settimeout(1)
                data, address = sock.recvfrom(2048)
                print(f"Received {len(data)} bytes from {address}")
                message = data.decode("utf-8")
                print(f"Data: {message}")

                # Respond to "ping" messages to help with UDP detection
                if message == "ping":
                    response = "pong"
                else:
                    response = message  # Echo back the received message

                sent = sock.sendto(response.encode("utf-8"), address)
                print(f"Sent {sent} bytes back to {address}")
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Error during communication: {str(e)}")
    except OSError as e:
        print(f"Error: Unable to bind to {ip}:{port}. It may already be in use.")
    finally:
        sock.close()
        print("UDP server closed.")
