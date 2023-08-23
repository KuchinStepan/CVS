from cvs_dialogs import *
from cvs_tree import *
import os


PATH_NAME = '.cvs'


class CloneVersionSystem:
    def __init__(self):
        self.running = False
        self.main_folder = None
        self.cvs_tree = None
        self.cvs_active = False
        self.commands = {
            'stop': self.stop,
            '0': self.stop
        }

    def stop(self):
        self.running = False

    def init(self):
        if self.cvs_active:
            print('В текущей директории уже создана система контроля версий')
            return
        else:
            path = f'{self.main_folder}\\{PATH_NAME}'
            os.mkdir(path)
            self.cvs_tree = TreeCVS(self.main_folder)
            print('CVS создан')

    def commit(self, message=None):
        if message is None:
            print('Коммит беб создан')
        else:
            parsed_message = message.split('\'')
            if len(parsed_message) != 3 \
                    or (len(parsed_message) == 3 and (len(parsed_message[0]) > 0 or len(parsed_message[2]) > 0)):
                print('Неверно указано сообщение к коммиту')
                return
            else:
                message = parsed_message[1]
                print(f'Коммит {message} создан')

    def do_command(self, command):
        if command != 'init' and not self.cvs_active:
            print('CVS не создан в текущей директории. Используйте команду \'init\'')
            return
        match command.split():
            case[('0' | 'stop')]:
                self.stop()
            case['init']:
                self.init()
            case['commit']:
                self.commit()
            case['commit', '-m', message]:
                self.commit(message)
            case _:
                print('Неверно введена команда')

    def run(self):
        print('Добро пожаловать в систему контроля версий CVS')
        self.running = True
        self.main_folder = read_main_folder()
        if os.path.exists(f'{self.main_folder}\\{PATH_NAME}'):
            self.cvs_active = True
        while self.running:
            command = input()
            self.do_command(command)
