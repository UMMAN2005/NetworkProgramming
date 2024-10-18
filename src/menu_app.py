from helpers.server import *


def main() -> None:
    default_ip = "127.0.0.1"
    default_port = 9000
    default_message = "Hello, world!"

    while True:
        print("\n--- Echo Program Menu ---")
        print("1. TCP Echo Client")
        print("2. TCP Echo Server")
        print("3. UDP Echo Client")
        print("4. UDP Echo Server")
        print("5. Exit")

        choice = input("Enter your choice (1-5): ")

        if choice in ["1", "2", "3", "4"]:
            # Input IP address and validate, use default if Enter is pressed
            while True:
                ip = input(f"Enter IP address (default {default_ip}): ") or default_ip
                if is_valid_ip(ip):
                    break
                else:
                    print("Invalid IP address. Please enter a valid IPv4 address.")

            # Input port number and validate, use default if Enter is pressed
            while True:
                port_input = input(f"Enter port number (default {default_port}): ")
                if not port_input:
                    port = default_port  # use default port
                    if choice == "2" or choice == "4":
                        # Increment the port if it is already in use
                        port = find_available_port(ip, default_port)
                    break
                try:
                    port = int(port_input)
                    if is_valid_port(port):
                        break
                    else:
                        print(
                            "Invalid port. Please enter a port number between 1 and 65535."
                        )
                except ValueError:
                    print("Port must be an integer.")

            # For clients, ask for the message, use default if Enter is pressed
            if choice in ["1", "3"]:
                message = (
                    input(f"Enter message (default '{default_message}'): ")
                    or default_message
                )

            if choice == "1":
                tcp_echo_client(ip, port, message)
            elif choice == "2":
                tcp_echo_server(ip, port)
            elif choice == "3":
                udp_echo_client(ip, port, message)
            elif choice == "4":
                udp_echo_server(ip, port)

        elif choice == "5":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please select again.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
        pass
