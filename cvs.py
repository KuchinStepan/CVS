from cvs_dialogs import *
from cvs_tree import *
import os
import pickle
import colorama


colorama.init(autoreset=True)


SAVER_FILE_PATH = f'{CVS_PATH}\\saver.pickle'


def _delete_last_comma(x):
    if len(x) > 0 and x[-1] == ',':
        return x[:-1]
    else:
        return x


class CloneVersionSystem:
    def __init__(self):
        self.running = False
        self.main_folder = None
        self.cvs_tree = None
        self.saved_cvs = None
        self.cvs_active = False
        self.commit_index = None

    @property
    def saver_directory(self):
        return f'{self.main_folder}\\{SAVER_FILE_PATH}'

    def reload_saver(self):
        if not os.path.exists(self.saver_directory):
            return
        with open(self.saver_directory, 'rb') as f:
            self.saved_cvs = pickle.load(f)

    def save_in_saver(self):
        self.saved_cvs = self.cvs_tree
        with open(self.saver_directory, 'wb') as f:
            pickle.dump(self.saved_cvs, f)

    def stop(self):
        self.save_in_saver()
        self.running = False

    def _create_folders(self):
        path = f'{self.main_folder}\\{CVS_PATH}'
        os.mkdir(path)
        path = f'{self.main_folder}\\{COMMITS_PATH}'
        os.mkdir(path)

    def init(self):
        if self.cvs_active:
            print('В текущей директории уже создана система контроля версий')
            return
        else:
            self._create_folders()
            self.cvs_tree = TreeCVS(self.main_folder)
            print('CVS создан')
            self.cvs_active = True

    def commit(self, message=None):
        if self.commit_index is None:
            print('Не добавлены изменения. Используйте команду \'add\'')
            return
        if message is None:
            name = self.cvs_tree.next_commit_folder_name
            self.cvs_tree.create_commit(name, self.commit_index)
            print(f'Коммит {name} создан')
        else:
            parsed_message = message.split('\'')
            if len(parsed_message) != 3 \
                    or (len(parsed_message) == 3 and (len(parsed_message[0]) > 0 or len(parsed_message[2]) > 0)):
                print('Неверно указано сообщение к коммиту')
                return
            else:
                message = parsed_message[1]
                self.cvs_tree.create_commit(message, self.commit_index)
                print(f'Коммит {message} создан')
        self.commit_index = None

    def status(self):
        all_changes = set(self.cvs_tree.create_commit_index_with_all().all_files)
        if len(all_changes) == 0:
            print('Нет новых изменений')
        if self.commit_index is None:
            added_changes = set()
        else:
            added_changes = set(self.commit_index.all_files)
        for file in all_changes.difference(added_changes):
            print(colorama.Fore.RED + file)
        for file in added_changes:
            print(colorama.Fore.GREEN + file)

    def add_by_names(self, names):
        names = list(map(_delete_last_comma, names))
        try:
            if self.commit_index is None:
                self.commit_index = CommitIndex()
            self.commit_index = self.cvs_tree.update_commit_index_by_names(self.commit_index, names)
        except FileNotFoundError as e:
            print(f'{e.filename} не найден')

    def do_command(self, command):
        if command != 'init' and not self.cvs_active:
            print('CVS не создан в текущей директории. Используйте команду \'init\'')
            return
        match command.split():
            case[('0' | 'stop')]:
                self.stop()
            case['init']:
                self.init()
            case['status']:
                self.status()
            case['add', '.']:
                self.commit_index = self.cvs_tree.create_commit_index_with_all()
            case['add', *names]:
                self.add_by_names(names)
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
        self.reload_saver()
        if os.path.exists(f'{self.main_folder}\\{CVS_PATH}'):
            self.cvs_active = True
            self.cvs_tree = self.saved_cvs

        while self.running:
            command = input('>>> ')
            self.do_command(command)
