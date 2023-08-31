import os


def read_main_folder():
    print('Введите директорию, в которой хотите работать с ситемой контроля версий')
    while True:
        path = input()
        if os.path.exists(path):
            return path
        else:
            print(f'Директория {path} не найдена!')
