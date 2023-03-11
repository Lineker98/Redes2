import socket

class UDPClient:
    def __init__(self, host: str, port: int, window_size: int, file_path: str) -> None:
        self.host = host
        self.port = port
        self.window_size = window_size
        self.file_path = file_path
        self.client = None

    def init_server(self) -> None:
        """_summary_
        """
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client.sendto("REQUEST".encode(), (self.host, self.port))

    def receive_data(self) -> None:
        """_summary_
        """

        with open(self.file_name, "wb") as file:
            while True:
                data, addr = self.client.recvfrom(1024)
                if data.decode() == "EOF":
                    print("File received!")
                    break
                file.write(data)
                self.client.sendto("ACK".encode(), addr)
                print(f"Chunk {data.decode()} received from {addr[0]}:{addr[1]}")