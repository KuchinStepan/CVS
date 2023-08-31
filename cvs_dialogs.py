import os
import pickle


FOLDERS_SAVER = 'recently_used_folders.pickle'


def read_number(limit: int):
    while True:
        try:
            number = int(input())
            if 0 <= number <= limit:
                return number
            else:
                print('Неверно введена команда')
        except ValueError:
            print('Неверно введена команда')


def read_recently_used_folder():
    print('Введите директорию, в которой хотите работать с ситемой контроля версий')
    if os.path.exists(FOLDERS_SAVER):
        print('0 - Выбрать директорию самостоятельно')
        with open(FOLDERS_SAVER, 'rb') as f:
            folders: list = pickle.load(f)
        for i in range(len(folders)):
            print(f'{i+1} - {folders[i]}')
        command = read_number(len(folders))
        if command == 0:
            return read_main_folder()
        else:
            return folders[command - 1]
    else:
        with open(FOLDERS_SAVER, 'wb') as f:
            folders = []
            pickle.dump(folders, f)
        return read_main_folder()


def read_main_folder():
    while True:
        path = input()
        if os.path.exists(path):
            with open(FOLDERS_SAVER, 'rb') as f:
                folders: list = pickle.load(f)
            folders.append(path)
            with open(FOLDERS_SAVER, 'wb') as f:
                pickle.dump(folders, f)
            return path
        else:
            print(f'Директория {path} не найдена!')
