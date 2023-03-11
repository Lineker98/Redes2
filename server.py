import socket
import os
from typing import List

class UDPServer(object):

    def __init__(self, host: str, port: int, window_size: int, file_name: str) -> None:
        self.host = host
        self.port = port
        self.window_size = window_size
        self.file_name = file_name
        self.file_size = os.stat(file_name).st_size
        self.server = None

    def read_file(self) -> List:
        """_summary_

        Returns:
            List: _description_
        """
        file_chunks = []
        with open(self.file_name, "rb") as file:
            while True:
                chunk = file.read(1024)
                if not chunk:
                    break
                file_chunks.append(chunk)

        print(f"File '{self.file_name}' of size {self.file_size} bytes loaded into memory in {len(self.file_chunks)} chunks")
        return file_chunks
    
    def init_server(self) -> None:
        """_summary_
        """
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server.bind((self.host, self.port))
        print(f"Server started on {self.host}:{self.port}")

    def process_requisition(self):
        """_summary_
        """

        chunks = self.read_file()
        while True:
            data, addr = self.server.recvfrom(1024)
            if data.decode() == "REQUEST":
                for i in range(0, len(self.file_chunks), self.window_size):
                    chunk_window = chunks[i:i+self.window_size]
                    for chunk in chunk_window:
                        self.server.sendto(chunk, addr)
                        ack, addr = self.server.recvfrom(1024)

                    if i+self.window_size >= len(chunks):
                        self.server.sendto("EOF".encode(), addr)
                        print("File transferred")
                        break
