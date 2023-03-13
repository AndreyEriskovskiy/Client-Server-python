from socket import *
import os.path
import sys


class Client:
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
        print('На начальном этапе вам необходимо авторизоваться, либо зарегистрироваться')
        auth = client_socket.recv(1024).decode()

        if auth:
            while True:
                print('Для регистрации используется команда /reg, для авторизации - /auth')
                command = input('Введите команду: ')
                client_socket.send(command.encode('utf-8'))

                if command == '/reg':
                    login = input('Логин: ')
                    password = input('Пароль: ')

                    if login != '' and password != '':
                        data = login + "_" + password
                        client_socket.send(data.encode('utf-8'))
                        reaction_on_the_reg = client_socket.recv(1024).decode()

                        if reaction_on_the_reg == 'Successful':
                            print('Вы успешно зарегистрированы')
                            break

                        elif reaction_on_the_reg == 'Failed':
                            print('Вы уже были зарегистрированы, пройдите авторизацию')
                    else:
                        login, password = '?', '?'
                        data = login + "_" + password
                        client_socket.send(data.encode('utf-8'))
                        reaction_on_the_empty_data = client_socket.recv(1024).decode()
                        print(reaction_on_the_empty_data)

                elif command == '/auth':
                    counter = 0
                    SuccessFlag = False
                    EmptyFlag = False

                    for i in range(3):
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
                        print('Вы потратили все попытки для прохождения авторизации на сервере :(')
                        sys.exit(0)


                else:
                    print('Введена несуществующая команда, повторите еще раз')

        print("Данная программа обеспечивает:\n""1) передачу текстовых файлов на сервер, если версия программы-сервера равна 1\n""2) передачу бинарных файлов на сервер, если версия программы-сервера равна 2")
        version = client_socket.recv(1024).decode()
        print('Серверная программа работает в версии:', version)
        version = int(version)
        print('Поддерживаемые режимы работы программы: /start, /exit')
        start = '/start'
        exit = '/exit' 

        if version:
            while True:
                choice = input('Введите режим работы: ')
                client_socket.send(choice.encode('utf-8'))

                if choice == exit:
                    print('Программа успешно завершена')
                    break

                elif choice == start:
                    if version == 1:
                        file_name = input('Введите полный путь к текстовому файлу, который вы хотите отправить на сервер: ')
                    else:
                        file_name = input('Введите полный путь к бинарному файлу, который вы хотите отправить на сервер: ')

                    obj = Client()

                    if obj.is_valid_filename(file_name):
                        client_socket.send('Valid'.encode('utf-8'))
                        client_socket.send(file_name.encode('utf-8'))
                        pos = file_name.rfind('\\')            
                        file_size = os.path.getsize(file_name)
                        
                        with open(file_name, 'rb') as f:    
                            send_data = f.read(file_size)
                            client_socket.send(send_data)

                        catalog_msg = client_socket.recv(1024).decode()

                        if catalog_msg != 'NoAdmin':
                            while True:
                                user_catalog = input(catalog_msg)
                                
                                if user_catalog != '':
                                    client_socket.send(user_catalog.encode('utf-8'))
                                    existing_catalog_flag = client_socket.recv(1024).decode()
                                    
                                    if existing_catalog_flag == 'NotExist':
                                        print('Введенного вами каталога не существует, попробуйте еще раз')
                                        continue
                                    else:
                                        break
                                else:
                                    print('Вы не ввели имя каталога пользователя')

                        msg = client_socket.recv(1024).decode()
                        
                        if msg != 'True':
                            print(msg)
                        else:
                            print(f'Файл {file_name[pos+1:]} успешно передан на сервер')
                   
        
                    else:
                        client_socket.send('Invalid'.encode('utf-8'))

                else:
                    msg = 'Вы ввели несуществующую команду, попробуйте ещё раз'
                    print(msg)
                      

client_socket.close()
