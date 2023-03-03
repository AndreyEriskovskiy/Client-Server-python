from socket import *
from threading import Thread
from random import *
import os.path
import pickle


class Server:
    def is_text_file(self, filename):
        try:
            with open(filename) as f:
                f.read(1)
                return True
        except:
            return False

    def __init__(self, filename_auth):

        self.filename_auth = filename_auth
        file_size = os.path.getsize(self.filename_auth)

        if file_size == 0:
            self.user_data = {}

        else:
            with open(self.filename_auth, 'rb') as f:
                self.user_data = pickle.load(f)


    def Check_Registration(self, login):

        if login in self.user_data:
            return True
        return False
       
    def Registration(self, login, password):

        if not self.Check_Registration(login):
            self.user_data[login] = password

            with open(self.filename_auth, 'wb') as f:
                pickle.dump(self.user_data, f)
                print(f'Регистрация пользователя {login} завершена успешно')
                return True
        else:
            print(f'Пользователь {login} уже зарегистрирован')
            return False

    def Authorization(self, login, password):

        if self.Check_Registration(login):
            if self.user_data[login] == password:
                print(f'Пользователь {login} успешно авторизован')
                return True
            else:
                print(f'Неверный пароль для пользователя {login}')
        else:
            print(f'Пользователь {login} не зарегистрирован')

        return False

        


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
    server.listen(1)
except error:
    print('Ошибка прослушивания')

print('Ожидание соединения...')
filename_auth = 'user_data.pickle'
obj = Server(filename_auth)
while True: 
    
    try:
        client_sock, addr = server.accept()
    except error:
        print('Ошибка принятия подключения')
    else:
        print(f'Есть входящий, IP-адрес: {addr[0]} -- Порт: {addr[1]}')
        client_sock.send('Auth'.encode('utf-8'))

        while True:
            backflag = False
            command = client_sock.recv(1024).decode()

            if command == '/reg':
                data = client_sock.recv(1024).decode().split('_')
                login, password = data[0], data[1]

                if obj.Registration(login, password):
                    client_sock.send('Successful'.encode('utf-8'))
                    break
                else:
                    client_sock.send('Failed'.encode('utf-8'))

            elif command == '/auth':
                counter = 0
                SuccessFlag = False
                for i in range(3):
                    data = client_sock.recv(1024).decode().split("_")
                    login, password = data[0], data[1]

                    if obj.Authorization(login, password):
                        client_sock.send('Successful'.encode('utf-8'))
                        SuccessFlag = True
                        break

                    else:
                        client_sock.send('Failed'.encode('utf-8'))
                        counter += 1

                if SuccessFlag:
                    break

                if counter == 3:
                    print(f'Клиент (IP-адрес: {addr[0]} -- Порт: {addr[1]}) отключен')
                    backflag = True

        if backflag:
            continue


        version = randint(1, 2)
        client_sock.send(str(version).encode('utf-8'))

        if version == 1:
            while True:
                flag = client_sock.recv(1024)

                if flag.startswith(b'/'):
                    

                    if flag == b'/exit':
                        print(f'Клиент (IP-адрес: {addr[0]} -- Порт: {addr[1]}) отключен')
                        break

                    elif flag == b'/start':
                        ValidFileFlag = client_sock.recv(1024)

                        if ValidFileFlag == b'Valid':
                            try:
                                file_name = client_sock.recv(1024).decode('utf-8')
                            except UnicodeDecodeError:
                                print(f'Ошибка декодирования (IP-адрес: {addr[0]} -- Порт: {addr[1]})')
                                break

                            pos = file_name.rfind('\\')
                            new_filename = file_name[pos+1:]
   
                            if obj.is_text_file(file_name):

                                f = open(new_filename, 'w')
                                f.close()       

                                with open(new_filename, 'ab') as f:
                                    file_size = os.path.getsize(file_name)           
                                    get_data = client_sock.recv(file_size)
                                    f.write(get_data)

                                client_sock.send('True'.encode('utf-8'))
                                print(f'Файл {new_filename} был успешно принят')
                
                            else:
                                msg = f'Похоже, вы пытаетесь передать на сервер бинарный файл, что не соотвествует версии программы-сервера (версия: {version}), попробуйте еще раз'
                                client_sock.send(msg.encode('utf-8'))
                    
      
        
        elif version == 2:
            while True:          
                flag = client_sock.recv(1024).decode('cp1251')

                if flag.startswith('/'):

                    if flag == '/exit': 
                        print(f'Клиент с IP-адресом: {addr[0]} -- Портом: {addr[1]} отключен')
                        break

                    elif flag == '/start':
                        ValidFileFlag = client_sock.recv(1024).decode('cp1251')

                        if ValidFileFlag == 'Valid':
                            try:
                                file_name = client_sock.recv(1024).decode('cp1251')
                            except UnicodeDecodeError:
                                print(f'Ошибка декодирования, IP-адрес: {addr[0]} -- Порт: {addr[1]}')
                                break

                            pos = file_name.rfind('\\')
                            new_filename = file_name[pos+1:]
                        
                            if not obj.is_text_file(file_name):
                                f = open(new_filename, 'wb')
                                f.close()

                                with open(new_filename, 'ab') as f:
                                    file_size = os.path.getsize(file_name)
                                    get_data = client_sock.recv(file_size)
                                    f.write(get_data)

                                client_sock.send('True'.encode('cp1251'))
                                print(f'Файл {new_filename} был успешно принят')
                
                            else:
                                msg = f'Похоже, вы пытаетесь передать на сервер текстовый файл, что не соотвествует версии программы-сервера (версия: {version}), попробуйте еще раз'
                                client_sock.send(msg.encode('cp1251'))
                   
client_sock.close()
server.close()
