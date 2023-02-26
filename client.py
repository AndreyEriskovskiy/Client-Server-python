from socket import *
from random import *
from threading import *
import os.path

class Client(Thread):
    def is_valid_filename(self, filename):
        
        if not os.path.exists(filename):
            print('Заданного вами пути к файлу не существует')
            return False
        else:       
            fpath = os.path.abspath(filename)
            if filename[filename.rfind('\\')+1:] == '' or filename.rfind('.') == -1:
                print('Не указано имя файла')
                return False
           
            elif fpath != filename:
                print('Вы ввели неполный путь к файлу')
                return False
            
            else:
                return True
    
    
        
            
host = '127.0.0.1'
port = 1111

try:
    client_socket = socket(AF_INET, SOCK_STREAM)
except error:
    print('Ошибка создания клиентского сокета')

try:
    client_socket.connect((host, port))
except error:
    print('Ошибка подключения к серверу')
else:

    print("Данная программа обечпечивает:\n""1) передачу текстовых файлов на сервер, если версия программы-сервера равна 1\n""2) передачу бинарных файлов на сервер, если версия программы-сервера равна 2")
    version = client_socket.recv(1024).decode()
    print('В данном случае версия сервера:', version)
    version = int(version)
    print('Поддерживаемые режимы работы программы: /start, /exit')
    start = '/start'
    exit = '/exit' 
    if version == 1:
        while True:
            choice = input('Введите режим работы: ')
            client_socket.send(choice.encode('utf-8'))
            if choice == start:
                file_name = input('Введите полный путь к текстовому файлу, который вы хотите отправить на сервер: ')              
                obj = Client()
                if obj.is_valid_filename(file_name):
                    client_socket.send(file_name.encode('utf-8'))
                    pos = file_name.rfind('\\')            
                    file_size = os.path.getsize(file_name)
                    send_data = ''
    
                    with open(file_name, 'rb') as f:    
                        send_data = f.read(file_size)
                        client_socket.send(send_data)
               
                    msg = client_socket.recv(1024).decode()
                    if msg != 'True':
                        print(msg)
                    else:
                        print(f'Файл {file_name[pos+1:]} успешно передан на сервер')
                   
        
                else:
                   
                    continue

            elif choice == exit:
                print('Программа успешно завершена')
                break
            

            else:
                msg = 'Вы ввели несуществующую команду, попробуйте ещё раз'
                print(msg)
                continue
       
        
     
       

    elif version == 2:
        while True:
            choice = input('Введите режим работы: ')
            client_socket.send(choice.encode('utf-8'))
            if choice == start:
                file_name = input('Введите полный путь к бинарному файлу, который вы хотите отправить на сервер: ')
                obj = Client()
                if obj.is_valid_filename(file_name):
                    client_socket.send(file_name.encode('utf-8'))
                    pos = file_name.rfind('\\')
                    file_size = os.path.getsize(file_name)
                    send_data = ''
    
                    with open(file_name, 'rb') as f:    
                        send_data = f.read(file_size)
                        client_socket.send(send_data)
               
                    msg = client_socket.recv(1024).decode()
                    if msg != 'True':
                        print(msg)
                    else:
                        print(f'Файл {file_name[pos+1:]} успешно передан на сервер')


                else:
                    
                    continue

            elif choice == exit:
                print('Программа успешно завершена')
                break

            else:
                msg = 'Вы ввели несуществующую команду, попробуйте ещё раз'
                print(msg)           
                continue

client_socket.close()
