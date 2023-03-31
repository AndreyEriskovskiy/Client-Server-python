'''
Программа-клиент представляет собой клиентскую часть приложения для передачи файлов на сервер.

Программа использует модуль socket для обеспечения соединения с сервером, а также модуль os.path

для проверки существования и типа файла, который пользователь хочет отправить на сервер.
'''

from socket import *
import os.path
import sys

'''
Класс Client имеет метод is_valid_filename, который проверяет, существует ли файл, указанный пользователем, 

и является ли этот файл файлом, а не директорией. Если проверка проходит успешно, метод возвращает значение True, 

иначе - False, и пользователю выводится сообщение об ошибке.
'''
class Client:
    def is_valid_filename(self, file_path):
     

        if os.path.exists(file_path) and file_path.find('\\' * 2) == -1:
            if os.path.isfile(file_path):
                return True
            else:
                print('Введенный вами путь не является файлом')

        else:
            print('Заданного вами пути к файлу не существует')

        return False


'''
В основной части программы создается клиентский сокет, после чего происходит его подключение к серверу 

по заданным адресу и порту. Далее программа получает от сервера флаг авторизации и, если этот флаг установлен 

в значение "Auth", запрашивает у пользователя ввод логина и пароля для регистрации или авторизации 

(по выбору пользователя) на сервере. В случае успешной регистрации или авторизации пользователь переходит к основной

части программы. В случае, если пользователь с 3 попытки не проходит авторизацию, его сессия завершается.
'''

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
                login = input('Логин: ').strip()
                password = input('Пароль: ').strip()

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

                    login = input('Логин: ').strip()
                    password = input('Пароль: ').strip()

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

    '''
    После успешной регистрации и авторизации на сервере программа получает информацию о версии сервера и выводит
    
    поддерживаемые режимы работы программы ("/start", "/exit"). При выборе режима работы "/start"
    
    пользователю предлагается ввести полный путь к файлу, который он хочет отправить на сервер. 
    
    Если пользователь выбирает режим работы "/exit", программа завершается.
    '''

    print('''Данная программа обеспечивает:
1) передачу текстовых файлов на сервер, если версия программы-сервера равна 1
2) передачу бинарных файлов на сервер, если версия программы-сервера равна 2''')

    version = int(client_socket.recv(1024).decode())  # версия сервера

    print(f'''Серверная программа работает в версии: {version}
Поддерживаемые режимы работы программы: /start, /exit''')

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
                    file_path = input('Введите полный путь к текстовому файлу, который вы хотите отправить на сервер: ')
                else:
                    file_path = input('Введите полный путь к бинарному файлу, который вы хотите отправить на сервер: ')

                obj = Client()

                '''
                Перед отправкой файла на сервер, программа проверяет его наличие, используя метод 
                
                "is_valid_filename()" класса Client. Если файл проходит проверку, программа отправляет на сервер 
                
                сообщение "Valid" и полный путь к файлу, после чего передает файл на сервер. Если файл не проходит 
                
                проверку, программа выводит соответствующее сообщение об ошибке. Также было реализовано дополнительное
                
                взаимодействие с программой-сервером для пользователя с правами администратора.
                '''

                # введенный путь к файлу действителен
                if obj.is_valid_filename(file_path):
                    client_socket.send('Valid'.encode('utf-8'))  # отправка сообщения о валидности передаваемого файла
                    client_socket.send(file_path.encode('utf-8'))  # отправка пути к файлу
                    pos = file_path.rfind('\\')
                    file_size = os.path.getsize(file_path)

                    with open(file_path, 'rb') as f:
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

                        print(f'Файл {file_path[pos + 1:]} успешно передан на сервер')


                else:
                    client_socket.send('Invalid'.encode('utf-8'))  # отправка сообщения о невалидности передаваемого файла

            else:
                msg = 'Вы ввели несуществующую команду, попробуйте ещё раз'
                print(msg)

client_socket.close()
