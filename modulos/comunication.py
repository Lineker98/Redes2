import socket
import os
from typing import List
import zlib
import struct

import random
import string

class UDPServer(object):

   def __init__(self, host: str, port: int, window_size: int) -> None:
      self.host = host
      self.port = port
      self.window_size = window_size

      self.max_payload_size = 1024
      self.server = None

   def check_sum_calculator(self, data: bytes) -> int:
      """_summary_

      Args:
          data (bytes): _description_

      Returns:
          int: _description_
      """
      checksum = zlib.crc32(data)
      return checksum
   
   def make_udp_header(self, data: bytes, dest_addr: str) -> bytes:
      """_summary_

      Args:
          data (_type_): _description_

      Returns:
          bytes: _description_
      """
      data_length = len(data)
      checksum = self.check_sum_calculator(data=data)
      udp_header = struct.pack("!IIII", self.port, dest_addr, data_length, checksum)
      return udp_header
   
   def init_server(self, bind = False) -> None:
      """
      Method to init the UDP server and bind in the port and host
      """
      self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      if bind:
         self.server.bind((self.host, self.port))
      print(f"Server started on {self.host}:{self.port}")
   
   def read_file(self, file_name) -> List:
      """
      Method to read the file requested by the client.

      Returns:
         List: A list with the chunks of 1024 size.
      """
      file_chunks = []

      with open(file_name, "rb") as file:
         while True:
               chunk = file.read(self.max_payload_size)
               if not chunk:
                  break
               file_chunks.append(chunk)
      return file_chunks
   
   def send_file(self, file_path, addr):
      chunks = self.read_file(file_path)
      print(chunks)

      for i in range(0, len(chunks), self.window_size):
         chunk_window = chunks[i:i+self.window_size]
         for chunk in chunk_window:
            # udp_header = self.make_udp_header(data=chunk, dest_addr=addr[1])
            full_packet = chunk
            self.server.sendto(full_packet, addr)

         if i+self.window_size >= len(chunks):
            end_of_file = "EOF"
            # udp_header = self.make_udp_header(data=end_of_file.encode(), dest_addr=addr[1])
            full_packet = end_of_file.encode()
            self.server.sendto(full_packet, addr)
            print("File transferred")
            break

   def store_file(self, file_path, addr):    
      with open(file_path, "wb") as file:
         while True:
            self.server.sendto(f"REQUEST:{file_path}".encode(), addr)
            data, addr = self.server.recvfrom(1024)
            if data.decode() == "EOF":
               print("File received!")
               break
            file.write(data)
            self.server.sendto("ACK".encode(), addr)
            print(f"Chunk {data.decode()} received from {addr[0]}:{addr[1]}")

   def list_files(self, addr):
      files = os.listdir('files')
      message = '\n'.join(files)
      self.server.sendto(message.encode(), addr)
      self.wait_ack()
      print("List transferred")
   
   def wait_ack(self):
      data = ''.encode()
      while data.decode() != 'ACK':
         data, addr = self.server.recvfrom(1024)
      self.server.sendto(data, addr)
            
if __name__ == "__main__":
    udp_server = UDPServer("127.0.0.1", 8080, window_size=2)
    udp_server.init_server(True)
    udp_server.process_requisition()