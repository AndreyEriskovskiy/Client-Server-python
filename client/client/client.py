'''
Необходимые модули для работы с сокетами, файловой системой и системными функциями
'''

from socket import *
import os.path
import sys

'''
Класс Client для работы с клиентскими операциями
'''
class Client:


    # Метод is_valid_filename() проверяет валидность введенного пользователем пути к файлу
    def is_valid_filename(self, filename):
      
        if os.path.exists(filename) and filename.find('\\' * 2) == -1:
            if os.path.isfile(filename):
                return True
            else:
                print('Введенный вами путь не является файлом')

        else:
            print('Заданного вами пути к файлу не существует')

        return False


host = '127.0.0.1'
port = 1111

# Создание клиентского сокета
try:
    client_socket = socket(AF_INET, SOCK_STREAM)
except error:
    print('Ошибка создания клиентского сокета')

# Подключение к серверу
try:
    client_socket.connect((host, port))
except error:
    print('Ошибка подключения к серверу')

else:

    # Реакция сервера на подключение клиента
    flag_in_to_the_server = client_socket.recv(1024).decode()

    if flag_in_to_the_server == 'Auth':  # Успешное подключение
        print('На начальном этапе вам необходимо авторизоваться, либо зарегистрироваться')
        while True:
            print('Для регистрации используется команда /reg, для авторизации - /auth')
            command = input('Введите команду: ')
            client_socket.send(command.encode('utf-8'))  # отправка команды, введенной пользователем, на сервер

            # выбрана регистрация
            if command == '/reg':
                login = input('Логин: ')
                password = input('Пароль: ')

                # данные были введены пользователем
                if login != '' and password != '':
                    data = login + "_" + password
                    client_socket.send(data.encode('utf-8'))  # отправка логина и пароля на сервер
                    reaction_on_the_reg = client_socket.recv(1024).decode() # реакция сервера на введенные данные пользователя

                    # Успешная регистрация
                    if reaction_on_the_reg == 'Successful':
                        print('Вы успешно зарегистрированы')
                        break

                    # Ошибка регистрации
                    elif reaction_on_the_reg == 'Failed':
                        print('Вы уже были зарегистрированы, пройдите авторизацию')
                else:
                    # данные не были введены пользователем
                    login, password = '?', '?'
                    data = login + "_" + password
                    client_socket.send(data.encode('utf-8'))
                    reaction_on_the_empty_data = client_socket.recv(1024).decode()
                    print(reaction_on_the_empty_data)

            # выбрана авторизация
            elif command == '/auth':
                counter = 0               # счетчик попыток авторизации пользователя
                SuccessFlag = False       # флаг успешной авторизации
                EmptyFlag = False         # флаг о невведенных пользователем логине или пароле

                for i in range(3):        # 3 попытки на авторизацию пользователя, в противном случае закрывается соединение с сервером
                    login = input('Логин: ')
                    password = input('Пароль: ')

                    if login != '' and password != '':
                        data = login + "_" + password
                        client_socket.send(data.encode('utf-8'))
                        reaction_on_the_auth = client_socket.recv(1024).decode()

                        if reaction_on_the_auth == 'Successful':
                            print('Вы успешно авторизованы')
                            SuccessFlag = True
                            break

                        elif reaction_on_the_auth == 'Failed':
                            if counter != 2:
                                print('Ошибка авторизации: убедитесь в правильности введённых данных, либо вашей регистрации')

                            counter += 1
                    else:
                        login, password = '?', '?'
                        data = login + "_" + password
                        client_socket.send(data.encode('utf-8'))
                        EmptyFlag = True
                        reaction_on_the_empty_data = client_socket.recv(1024).decode()
                        print(reaction_on_the_empty_data)
                        break

                if EmptyFlag:
                    continue

                if SuccessFlag:
                    break

                if counter == 3:
                    print('Вы потратили все попытки для прохождения авторизации на сервере')
                    sys.exit(0)

            else:
                print('Введена несуществующая команда, повторите еще раз')
    else:
        # Превышено количество подключений к серверу
        print(flag_in_to_the_server)
        sys.exit(0)

    print('''Данная программа обеспечивает:
1) передачу текстовых файлов на сервер, если версия программы-сервера равна 1
2) передачу бинарных файлов на сервер, если версия программы-сервера равна 2''')
    version = int(client_socket.recv(1024).decode())  # версия сервера
    print('Серверная программа работает в версии:', version)
    print('Поддерживаемые режимы работы программы: /start, /exit')
    start = '/start'
    exit = '/exit'

    if version:
        while True:
            choice = input('Введите режим работы: ')
            client_socket.send(choice.encode('utf-8'))  # отправка команды (/start, /exit) на сервер

            if choice == exit:
                print('Программа успешно завершена')
                break

            elif choice == start:
                if version == 1:
                    file_name = input('Введите полный путь к текстовому файлу, который вы хотите отправить на сервер: ')
                else:
                    file_name = input('Введите полный путь к бинарному файлу, который вы хотите отправить на сервер: ')

                obj = Client()

                # введенный путь к файлу действителен
                if obj.is_valid_filename(file_name):
                    client_socket.send('Valid'.encode('utf-8'))  # отправка сообщения о валидности передаваемого файла
                    client_socket.send(file_name.encode('utf-8'))  # отправка пути к файлу
                    pos = file_name.rfind('\\')
                    file_size = os.path.getsize(file_name)

                    with open(file_name, 'rb') as f:
                        send_data = f.read(file_size)
                        client_socket.send(send_data)    # отправка содержимого файла на сервер

                    msg = client_socket.recv(1024).decode()  # сообщение о состоянии файла, переданного на сервер

                    # Файл не соответствует версии программы-сервера
                    if msg != 'True':
                        print(msg)

                    else:

                        status = client_socket.recv(1024).decode()  # сообщение о статусе пользователя

                        if status == 'Admin':
                            while True:
                                users = client_socket.recv(1024).decode()
                                print(f'Возможные каталоги для сохранения: {users}')
                                user_catalog = input('Введите имя каталога пользователя, в который хотите сохранить файл: ')

                                if user_catalog != '':
                                    client_socket.send(user_catalog.encode('utf-8'))  # отправка выбранного каталога на сервер
                                    existing_catalog_flag = client_socket.recv(1024).decode()  # сообщение о наличии (отсутствии) пользовательского каталога на сервере

                                    if existing_catalog_flag == 'NotExist':
                                        print('Введенного вами каталога не существует, попробуйте еще раз')
                                        continue

                                    else:
                                        break
                                else:
                                    print('Вы не ввели имя каталога пользователя')

                        print(f'Файл {file_name[pos + 1:]} успешно передан на сервер')



                else:
                    client_socket.send('Invalid'.encode('utf-8')) # отправка сообщения о невалидности передаваемого файла

            else:
                msg = 'Вы ввели несуществующую команду, попробуйте ещё раз'
                print(msg)

client_socket.close()
