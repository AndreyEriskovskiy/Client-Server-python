'''
Программа-сервер  обрабатывает  подключения от клиентов, их регистрацию и авторизацию,

а также прием и сохранение файлов на сервере. Для работы сервера используются сокеты,

многопоточность (threading), библиотеки для работы с файловой системой (os, os.path),

со случайными числами (random), сериализацией объектов Python в поток байтов (pickle),

MIME-типами файлов (mimetypes).
'''

from socket import *
from threading import Thread
from random import *
import os.path
import os
import pickle
import mimetypes

'''
Класс "Server" реализует основные функции сервера: регистрацию, авторизацию клиента,
    
сохранение файла на сервере и проверку типа файла.
'''

class Server:

    '''
    Конструктор класса "__init__" инициализирует необходимые параметры,

    такие как список администраторских логинов, файл для хранения информации о пользователях, максимальное количество

    подключений, счетчик подключенных клиентов и словарь, содержащий информацию о пользователях.
    '''
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

    '''
    Метод is_text_file() проверяет, является ли переданный ему файл текстовым.
    '''
    def is_text_file(self, filename):
        mimetype, _ = mimetypes.guess_type(filename)

        if mimetype is not None:
            if mimetype.startswith('text/'):
                return True
        return False

    '''
    Метод save_file() сохраняет файлы, отправленные клиентом на сервер. Если пользователь с правами администратора, 
    
    ему необходимо указать имя каталога, в который следует сохранить файл, иначе файл сохраняется в каталоге 
    
    с логином пользователя.
    '''
    def save_file(self, new_filename, file_data, user_login, client_sock):
        status = self.user_data[user_login][1]  # статус пользователя
        if status == 'admin':
            client_sock.send('Admin'.encode('utf-8'))  # пользователь - администратор
            while True:
                os.makedirs(f'users/{user_login}', exist_ok=True)                    # cоздание каталога пользователя в случае его отсутствия
                users = os.listdir('users')                                          # список каталогов пользователей
                client_sock.send(", ".join(users).encode('utf-8'))                   # отправка списка каталогов пользователю для сохранения файла
                user_catalog = client_sock.recv(1024).decode()                       # полученный от пользователя каталог

                if user_catalog in self.user_data:
                    client_sock.send('Exist'.encode('utf-8'))                        # отправка сообщения о существовании каталога
                    user_path = os.path.join(f'users/{user_catalog}', new_filename)  # путь для сохранения файла

                    f = open(user_path, 'wb')                                        # создание файла в полученной директории
                    f.close()

                    with open(user_path, 'ab') as f:                                 # запись информации в файл
                        f.write(file_data)

                    break

                else:
                    client_sock.send('NotExist'.encode('utf-8'))                     # отправка сообщения об отсутствии каталога
        else:
            client_sock.send('NoAdmin'.encode('utf-8'))                              # пользователь - не администратор
            os.makedirs(f'users/{user_login}', exist_ok=True)
            user_path = os.path.join(f'users/{user_login}', new_filename)

            f = open(user_path, 'wb')
            f.close()

            with open(user_path, 'ab') as f:
                f.write(file_data)
    '''
    Метод Check_Registration() проверяет, зарегистрирован ли пользователь с указанным логином.
    '''
    def Check_Registration(self, login):
        if login in self.user_data:
            return True
        return False

    '''
    Метод Registration() регистрирует новых пользователей на сервере, если таких пользователей еще не существует.
    
    Также при регистрации происходит назначение ролей клиентам, в зависимости от введенного логина.
    
    В случае успешной регистрации данные о пользователе записываются в словарь, после чего словарь записывается в файл.
    '''
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

    '''
    Метод Authorization() авторизует пользователей на сервере, если они уже были зарегистрированы.
    '''
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

'''
Функция main() выполняет основную работу сервера. В цикле while сервер принимает команды от клиента и выполняет соответствующие операции. 

Если клиент выбирает команду /reg, он должен предоставить логин и пароль для регистрации. Если клиент выбирает команду /auth, он должен 

предоставить логин и пароль для авторизации. Если клиент выбирает команду /exit, он завершает соединение. Если клиент отправляет файл, 

сервер сохраняет его с помощью метода save_file().

Если количество подключившихся клиентов достигает значения "max_clients", то следующему клиенту будет отправлено сообщение об ошибке подключения.
'''
def main(client_sock, addr, obj):
    user_login = ''

    if obj.counter_client_connections == obj.max_clients:                       # превышено количество пользователей
        client_sock.send('Превышено количество подключений'.encode('utf-8'))
    else:
        obj.counter_client_connections += 1                                     # подключен новый клиент
        print(f'Есть входящий, IP-адрес: {addr[0]} -- Порт: {addr[1]}')         # информация о подключившемся клиенте
        client_sock.send('Auth'.encode('utf-8'))                                # отправка сообщения о прохождении процедуры аутентификации

        while True:
            ExitFlag = False
            command = client_sock.recv(1024).decode()                           # команда, введенная пользователем (/reg, /auth)

            if command == '/reg':
                data = client_sock.recv(1024).decode().split('_')               # введенные пользователем логин и пароль
                login, password = data[0], data[1]

                if login == '?' and password == '?':
                    client_sock.send('Данные не были введены, попробуйте еще раз'.encode('utf-8'))
                    continue

                if obj.Registration(login, password):
                    user_login = login
                    client_sock.send('Successful'.encode('utf-8'))              # отправка сообщения об успешной регистрации
                    break

                else:
                    client_sock.send('Failed'.encode('utf-8'))                  # отправка сообщения об ошибке регистрации

            elif command == '/auth':
                counter = 0
                SuccessFlag = False                                             # флаг об успешной авторизации
                EmptyFlag = False                                               # флаг о невведенных пользователем логине или пароле

                for i in range(3):                                              # 3 попытки на авторизацию пользователя, в противном случае закрывается соединение с сервером
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
                    ExitFlag = True
                    obj.counter_client_connections -= 1
                    break

        if ExitFlag:
            return                                                              # возврат сервера к состоянию принятия подключений

        version = randint(1, 2)                                                 # генерация версии сервера
        client_sock.send(str(version).encode('utf-8'))                          # отправка версии сервера клиенту

        if version == 1:
            while True:
                command = client_sock.recv(1024)                                # команда, введенная пользователем (/start, /exit)

                if command.startswith(b'/'):

                    if command == b'/exit':
                        print(f'Клиент (IP-адрес: {addr[0]} -- Порт: {addr[1]}) отключен')
                        obj.counter_client_connections -= 1
                        break

                    elif command == b'/start':
                        ValidFileFlag = client_sock.recv(1024)                  # сообщение о валидности указанного пользователем пути к файлу

                        if ValidFileFlag == b'Valid':                           # путь к передаваемому файлу действителен
                            try:
                                file_path = client_sock.recv(1024).decode('utf-8')   # полученный путь к файлу
                            except UnicodeDecodeError:
                                print(f'Ошибка декодирования (IP-адрес: {addr[0]} -- Порт: {addr[1]})')
                                break

                            pos = file_path.rfind('\\')
                            file_name = file_path[pos + 1:]                     # имя файла
                            file_size = os.path.getsize(file_path)              # размер передаваемого файла
                            file_data = client_sock.recv(file_size)             # полученное содержимое файла

                            if obj.is_text_file(file_path):                     # файл является текстовым
                                client_sock.send('True'.encode('utf-8'))        # отправка сообщения о соответствии передаваемого файла версии сервера

                                obj.save_file(file_name, file_data, user_login, client_sock)
                                print(f'Файл {file_name} был успешно принят')

                            else:
                                msg = f'Похоже, вы пытаетесь передать на сервер бинарный файл, что не соотвествует версии программы-сервера (версия: {version}), попробуйте еще раз'

                                client_sock.send(msg.encode('utf-8'))           # отправка сообщения о несоответствии передаваемого файла версии сервера




        elif version == 2:
            while True:
                command = client_sock.recv(1024)

                if command.startswith(b'/'):

                    if command == b'/exit':
                        print(f'Клиент с IP-адресом: {addr[0]} -- Портом: {addr[1]} отключен')
                        obj.counter_client_connections -= 1
                        break

                    elif command == b'/start':
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

                            if not obj.is_text_file(file_name):                 # файл является бинарным
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
    server = socket(AF_INET, SOCK_STREAM)           # создание серверного сокета
except error:
    print('Ошибка создания серверного сокета')

try:
    server.bind((localhost, port))                  # привязка сокета к заданному адресу
except error:
    print('Ошибка привязки сокета')

try:
    server.listen()                                 # прослушивание входящих соединений
except error:
    print('Ошибка прослушивания')

print('Ожидание соединения...')
max_clients = 3
obj = Server(max_clients)

while True:
    try:
        client_sock, addr = server.accept()         # принятие подключения
    except error:
        print('Ошибка принятия подключения')
    else:
        client_thread = Thread(target=main, args=(client_sock, addr, obj))
        client_thread.start()


server.close()


