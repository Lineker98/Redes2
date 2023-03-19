import socket
import os

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
   
   def read_file(self, file_name) -> list:
      """
      Method to read the file requested by the client.

      Returns:
         List: A list with the chunks of 1024 size.
      """
      file_chunks = []
      file_size = os.stat(file_name).st_size

      with open(file_name, "rb") as file:
         while True:
               chunk = file.read(1024)
               if not chunk:
                  break
               file_chunks.append(chunk)

      print(f"File '{file_name}' of size {file_size} bytes loaded into memory in {len(file_chunks)} chunks")
      return file_chunks

   def receive_data(self) -> None:
      """
      Main method to receive the server response and write the file
      """
      
      file_name = input("Entre com o nome do arquivo")
      self.client.sendto(f"REQUEST:{file_name}".encode(), (self.host, self.port))
      with open(self.file_path, "wb") as file:
         while True:
               data, addr = self.client.recvfrom(1024)
               if data.decode() == "EOF":
                  print("File received!")
                  break
               file.write(data)
               self.client.sendto("ACK".encode(), addr)
               print(f"Chunk {data.decode()} received from {addr[0]}:{addr[1]}")

   def send_file(self):
      file_path = input("Entre com o nome do arquivo")
      file_name = file_path.split('/')[-1]

      chunks = self.read_file(file_path)
      self.client.sendto(f"STORE:{file_name}".encode(), (self.host, self.port))

      for i in range(0, len(chunks), self.window_size):
         chunk_window = chunks[i:i+self.window_size]
         for chunk in chunk_window:
            self.client.sendto(chunk, (self.host, self.port))

         if i+self.window_size >= len(chunks):
            self.client.sendto("EOF".encode(), (self.host, self.port))
            print("File transferred")
            break

if __name__ == "__main__":
   udp_client = UDPClient("127.0.0.1", 8080, window_size=16, file_path="receive.txt")
   udp_client.init_server()

   while True:
      print("Escolha uma das opções")
      print("1 - Listar os arquivos")
      print("2 - Receber os arquivos")
      print("3 - Enviar arquivo")
      choice = input()

      if choice == '1':
         udp_client.list_file()
      elif choice == '2':
         udp_client.receive_data()
      elif choice == '3':
         udp_client.send_file()
      else:
         print("opção inválida, tente novamente")

      print("\n\nClique enter para continuar")
      input()
      os.system("clear")