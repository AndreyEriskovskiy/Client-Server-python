from socket import *
from threading import Thread
from random import *
import os.path


class Server:
    def is_binary_file(self, filename):
        try:
            with open(filename) as f:
                f.read()
                return False                  
        except:
            return True
       

        


localhost = '127.0.0.1'
port = 1111
try:
    server = socket(AF_INET, SOCK_STREAM)
except error:
    print('Ошибка создания серверного сокета')

try:
    server.bind((localhost, port))
except error:
    print('Ошибка привязки сокета')

try:
    server.listen(5)
except error:
    print('Ошибка прослушивания')

print('Ожидание соединения...')

while True: 
    
    try:
        client_sock, addr = server.accept()
    except error:
        print('Ошибка принятия подключения')
    else:
        print(f'Есть входящий, IP-адрес: {addr[0]} -- Порт: {addr[1]}')

    version = randint(1, 2)
    client_sock.send(str(version).encode('utf-8'))
    if version == 1:
        while True:
            file_name = client_sock.recv(1024).decode()   
            pos = file_name.rfind('\\')
            new_filename = file_name[pos+1:]
            obj = Server()
            if not (obj.is_binary_file(file_name)):
         
                f = open(new_filename, 'w')
                f.close()       
                with open(new_filename, 'ab') as f:
                    file_size = os.path.getsize(file_name)           
                    get_data = client_sock.recv(file_size)
                    f.write(get_data)
                client_sock.send('True'.encode('utf-8'))
                
            else:
                msg = f'Похоже, вы пытаетесь передать на сервер бинарный файл, что не соотвествует версии программы-сервера (версия: {version}), попробуйте еще раз'
                client_sock.send(msg.encode('utf-8'))
                
           
        
       
      
        
    elif version == 2:
        while True:
            file_name = client_sock.recv(1024).decode()
            pos = file_name.rfind('\\')
            new_filename = file_name[pos+1:]
            obj = Server()
            if obj.is_binary_file(file_name):
                f = open(new_filename, 'wb')
                f.close()
                with open(new_filename, 'ab') as f:
                    file_size = os.path.getsize(file_name)
                    get_data = client_sock.recv(file_size)
                    f.write(get_data)
                client_sock.send('True'.encode('utf-8'))
                
            else:
                msg = f'Похоже, вы пытаетесь передать на сервер текстовый файл, что не соотвествует версии программы-сервера (версия: {version}), попробуйте еще раз'
                client_sock.send(msg.encode('utf-8'))
                
            

        
client_sock.close()
server.close()


    