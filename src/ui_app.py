import tkinter as tk
from tkinter import messagebox, font
from helpers.server import *
from threading import Thread, Event

stop_event = Event()


# Function to run the TCP Echo client in a separate thread
def start_tcp_client(ip, port, message):
    Thread(target=tcp_echo_client, args=(ip, port, message)).start()


# Function to run the TCP Echo server in a separate thread
def start_tcp_server(ip, port):
    global tcp_thread
    tcp_thread = Thread(target=tcp_echo_server, args=(ip, port, stop_event))
    tcp_thread.start()


# Function to run the UDP Echo client in a separate thread
def start_udp_client(ip, port, message):
    Thread(target=udp_echo_client, args=(ip, port, message)).start()


# Function to run the UDP Echo server in a separate thread
def start_udp_server(ip, port):
    global udp_thread
    udp_thread = Thread(target=udp_echo_server, args=(ip, port, stop_event))
    udp_thread.start()


def on_exit():
    print("Stopping servers...")
    stop_event.set()  # Signal servers to stop
    if "tcp_thread" in globals() and tcp_thread.is_alive():
        tcp_thread.join()  # Wait for TCP server to stop
    if "udp_thread" in globals() and udp_thread.is_alive():
        udp_thread.join()  # Wait for UDP server to stop
    print("Servers stopped.")
    root.quit()


# Main App Window
class EchoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Echo Server/Client")
        self.root.geometry("500x400")
        self.root.configure(bg="#f0f0f0")  # Light gray background

        # Custom Font
        self.default_font = font.Font(family="Segoe UI", size=10)

        # Default values
        self.default_ip = "127.0.0.1"
        self.default_port = 9000
        self.default_message = "Hello, world!"

        # Style Configuration
        style = {
            "bg": "#ffffff",  # White background for inputs
            "relief": "flat",
            "bd": 2,
        }

        # Frame for user input
        self.frame = tk.Frame(self.root, bg="#f0f0f0")
        self.frame.pack(pady=20)

        # Labels and inputs for IP Address, Port, and Message
        tk.Label(
            self.frame, text="IP Address:", font=self.default_font, bg="#f0f0f0"
        ).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.ip_entry = tk.Entry(self.frame, **style)
        self.ip_entry.insert(0, self.default_ip)
        self.ip_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(self.frame, text="Port:", font=self.default_font, bg="#f0f0f0").grid(
            row=1, column=0, padx=10, pady=5, sticky="w"
        )
        self.port_entry = tk.Entry(self.frame, **style)
        self.port_entry.insert(0, str(self.default_port))
        self.port_entry.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(
            self.frame,
            text="Message (for clients):",
            font=self.default_font,
            bg="#f0f0f0",
        ).grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.message_entry = tk.Entry(self.frame, **style)
        self.message_entry.insert(0, self.default_message)
        self.message_entry.grid(row=2, column=1, padx=10, pady=5)

        # Buttons for starting clients/servers with modern styling
        button_style = {
            "bg": "#0078d4",
            "fg": "white",
            "font": self.default_font,
            "relief": "flat",
        }

        tk.Button(
            self.frame,
            text="Start TCP Echo Client",
            command=self.run_tcp_client,
            **button_style,
        ).grid(row=3, column=0, padx=10, pady=5, sticky="ew")

        tk.Button(
            self.frame,
            text="Start TCP Echo Server",
            command=self.run_tcp_server,
            **button_style,
        ).grid(row=3, column=1, padx=10, pady=5, sticky="ew")

        tk.Button(
            self.frame,
            text="Start UDP Echo Client",
            command=self.run_udp_client,
            **button_style,
        ).grid(row=4, column=0, padx=10, pady=5, sticky="ew")

        tk.Button(
            self.frame,
            text="Start UDP Echo Server",
            command=self.run_udp_server,
            **button_style,
        ).grid(row=4, column=1, padx=10, pady=5, sticky="ew")

        # Exit Button
        tk.Button(self.frame, text="Exit", command=on_exit, **button_style).grid(
            row=5, column=0, columnspan=2, pady=10, sticky="ew"
        )

    def get_ip_and_port(self, type=None):
        """Get the IP address and port entered by the user."""
        ip = self.ip_entry.get()
        port = self.port_entry.get()

        if not is_valid_ip(ip):
            messagebox.showerror("Invalid Input", "Please enter a valid IP address.")
            return None, None
        try:
            port = int(port)
            if not is_valid_port(port):
                raise ValueError
            if type is None:
                return ip, port
            self.port_entry.delete(0, tk.END)
            self.port_entry.insert(0, str(port + 1))
            return ip, port
        except ValueError:
            messagebox.showerror(
                "Invalid Input", "Please enter a valid port number (1-65535)."
            )
            return None, None

    def run_tcp_client(self):
        """Start the TCP Echo Client."""
        ip, port = self.get_ip_and_port()
        if ip and port:
            message = self.message_entry.get() or self.default_message
            start_tcp_client(ip, port, message)

    def run_tcp_server(self):
        """Start the TCP Echo Server."""
        ip, port = self.get_ip_and_port("tcp")
        if ip and port:
            start_tcp_server(ip, port)

    def run_udp_client(self):
        """Start the UDP Echo Client."""
        ip, port = self.get_ip_and_port()
        if ip and port:
            message = self.message_entry.get() or self.default_message
            start_udp_client(ip, port, message)

    def run_udp_server(self):
        """Start the UDP Echo Server."""
        ip, port = self.get_ip_and_port("udp")
        if ip and port:
            start_udp_server(ip, port)


# Run the Tkinter application
if __name__ == "__main__":
    root = tk.Tk()
    root.protocol("WM_DELETE_WINDOW", on_exit)
    app = EchoApp(root)
    root.mainloop()
