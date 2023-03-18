import socket

class UDPClient:
   def __init__(self, host: str, port: int, window_size: int, file_path: str) -> None:
      self.host = host
      self.port = port
      self.window_size = window_size
      self.file_path = file_path
      self.client = None

   def init_server(self) -> None:
      """
      Method to start the UDP client server and send the first request to the server
      """
      self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

   def list_file(self):
      message = 'LIST'
      self.client.sendto(message.encode(), (self.host, self.port))
      while True:
         data, addr = self.client.recvfrom(1024)
         if data.decode() == "ACK":
            print("List received!")
            break
         print(data.decode())
         self.client.sendto("ACK".encode(), addr)

   def receive_data(self) -> None:
      """
      Main method to receive the server response and write the file
      """
      
      file_name = input()
      with open(self.file_path, "wb") as file:
         while True:
               self.client.sendto(f"REQUEST:{file_name}".encode(), (self.host, self.port))
               data, addr = self.client.recvfrom(1024)
               if data.decode() == "EOF":
                  print("File received!")
                  break
               file.write(data)
               self.client.sendto("ACK".encode(), addr)
               print(f"Chunk {data.decode()} received from {addr[0]}:{addr[1]}")

if __name__ == "__main__":
   udp_client = UDPClient("127.0.0.1", 8080, window_size=16, file_path="receive.txt")
   udp_client.init_server()
   udp_client.receive_data()
   # udp_client.list_file()