from socket import *
from threading import Thread
from random import *
import os.path
import os
import pickle
import mimetypes


class Server:
    def __init__(self, max_clients):
        if not os.path.exists('user_data.pickle'):
            f = open('user_data.pickle', 'wb')
            f.close()

        self.admin_logins = ['root', 'admin']
        self.filename_auth = 'user_data.pickle'
        self.max_clients = max_clients
        self.counter_client_connections = 0
        file_size = os.path.getsize(self.filename_auth)

        if file_size == 0:
            self.user_data = {}

        else:
            with open(self.filename_auth, 'rb') as f:
                self.user_data = pickle.load(f)

    def is_text_file(self, filename):
        mimetype, _ = mimetypes.guess_type(filename)

        if mimetype is not None:
            if mimetype.startswith('text/'):
                return True
        return False

    def save_file(self, new_filename, file_data, user_login, client_sock):
        status = self.user_data[user_login][1]
        if status == 'admin':
            client_sock.send('Введите имя каталога пользователя, в который хотите сохранить файл: '.encode('utf-8'))
            while True:
                os.makedirs(f'users/{user_login}', exist_ok=True)
                users = os.listdir('users')
                client_sock.send(", ".join(users).encode('utf-8'))
                user_catalog = client_sock.recv(1024).decode()

                if user_catalog in self.user_data:
                    client_sock.send('Exist'.encode('utf-8'))
                    user_path = os.path.join(f'users/{user_catalog}', new_filename)

                    f = open(user_path, 'wb')
                    f.close()

                    with open(user_path, 'ab') as f:
                        f.write(file_data)

                    break

                else:
                    client_sock.send('NotExist'.encode('utf-8'))
        else:
            client_sock.send('NoAdmin'.encode('utf-8'))
            os.makedirs(f'users/{user_login}', exist_ok=True)
            user_path = os.path.join(f'users/{user_login}', new_filename)

            f = open(user_path, 'wb')
            f.close()

            with open(user_path, 'ab') as f:
                f.write(file_data)

    def Check_Registration(self, login):
        if login in self.user_data:
            return True
        return False

    def Registration(self, login, password):
        status = 'user'

        if not self.Check_Registration(login):
            if login in self.admin_logins:
                status = 'admin'
                self.user_data[login] = [password, status]
            else:
                self.user_data[login] = [password, status]

            with open(self.filename_auth, 'wb') as f:
                pickle.dump(self.user_data, f)
                print(f'Регистрация пользователя {login} завершена успешно')
                return True
        else:
            print(f'Пользователь {login} уже зарегистрирован')
            return False

    def Authorization(self, login, password):

        if self.Check_Registration(login):
            existing_password = self.user_data[login][0]

            if existing_password == password:
                print(f'Пользователь {login} успешно авторизован')
                return True
            else:
                print(f'Неверный пароль для пользователя {login}')
        else:
            print(f'Пользователь {login} не зарегистрирован')

        return False

   
def main(client_sock, addr, obj):
    if obj.counter_client_connections == obj.max_clients:
        client_sock.send('Превышено количество подключений'.encode('utf-8'))
    else:
        obj.counter_client_connections += 1
        print(f'Есть входящий, IP-адрес: {addr[0]} -- Порт: {addr[1]}')
        client_sock.send('Auth'.encode('utf-8'))

        while True:
            backflag = False
            command = client_sock.recv(1024).decode()

            if command == '/reg':
                data = client_sock.recv(1024).decode().split('_')
                login, password = data[0], data[1]

                if login == '?' and password == '?':
                    client_sock.send('Вы ввели пустые данные, попробуйте еще раз'.encode('utf-8'))
                    continue

                if obj.Registration(login, password):
                    user_login = login
                    client_sock.send('Successful'.encode('utf-8'))
                    break
                else:
                    client_sock.send('Failed'.encode('utf-8'))

            elif command == '/auth':
                counter = 0
                SuccessFlag = False
                EmptyFlag = False

                for i in range(3):
                    data = client_sock.recv(1024).decode().split("_")
                    login, password = data[0], data[1]
                    if login == '?' and password == '?':
                        client_sock.send('Вы ввели пустые данные, попробуйте еще раз'.encode('utf-8'))
                        EmptyFlag = True
                        break

                    if obj.Authorization(login, password):
                        user_login = login
                        client_sock.send('Successful'.encode('utf-8'))
                        SuccessFlag = True
                        break

                    else:
                        client_sock.send('Failed'.encode('utf-8'))
                        counter += 1

                if EmptyFlag:
                    continue

                if SuccessFlag:
                    break

                if counter == 3:
                    print(f'Клиент (IP-адрес: {addr[0]} -- Порт: {addr[1]}) отключен')
                    backflag = True
                    obj.counter_client_connections -= 1
                    break

        if backflag:
            return

        version = randint(1, 2)
        client_sock.send(str(version).encode('utf-8'))

        if version == 1:
            while True:
                flag = client_sock.recv(1024)

                if flag.startswith(b'/'):

                    if flag == b'/exit':
                        print(f'Клиент (IP-адрес: {addr[0]} -- Порт: {addr[1]}) отключен')
                        obj.counter_client_connections -= 1
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
                            new_filename = file_name[pos + 1:]
                            file_size = os.path.getsize(file_name)
                            file_data = client_sock.recv(file_size)

                            if obj.is_text_file(file_name):
                                client_sock.send('True'.encode('utf-8'))
                                obj.save_file(new_filename, file_data, user_login, client_sock)
                                print(f'Файл {new_filename} был успешно принят')

                            else:
                                msg = f'Похоже, вы пытаетесь передать на сервер бинарный файл, что не соотвествует версии программы-сервера (версия: {version}), попробуйте еще раз'
                                client_sock.send(msg.encode('utf-8'))



        elif version == 2:
            while True:
                flag = client_sock.recv(1024)

                if flag.startswith(b'/'):

                    if flag == b'/exit':
                        print(f'Клиент с IP-адресом: {addr[0]} -- Портом: {addr[1]} отключен')
                        obj.counter_client_connections -= 1
                        break

                    elif flag == b'/start':
                        ValidFileFlag = client_sock.recv(1024)

                        if ValidFileFlag == b'Valid':
                            try:
                                file_name = client_sock.recv(1024).decode('utf-8')
                            except UnicodeDecodeError:
                                print(f'Ошибка декодирования, IP-адрес: {addr[0]} -- Порт: {addr[1]}')
                                break

                            pos = file_name.rfind('\\')
                            new_filename = file_name[pos + 1:]
                            file_size = os.path.getsize(file_name)
                            file_data = client_sock.recv(file_size)

                            if not obj.is_text_file(file_name):
                                client_sock.send('True'.encode('utf-8'))
                                obj.save_file(new_filename, file_data, user_login, client_sock)
                                print(f'Файл {new_filename} был успешно принят')

                            else:
                                msg = f'Похоже, вы пытаетесь передать на сервер текстовый файл, что не соотвествует версии программы-сервера (версия: {version}), попробуйте еще раз'
                                client_sock.send(msg.encode('utf-8'))
        client_sock.close()

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
    server.listen(3)
except error:
    print('Ошибка прослушивания')

print('Ожидание соединения...')
max_clients = 3
obj = Server(max_clients)

while True:
    try:
        client_sock, addr = server.accept()
    except error:
        print('Ошибка принятия подключения')
    else:
        client_thread = Thread(target=main, args=(client_sock, addr, obj))
        client_thread.start()

            
server.close()       
