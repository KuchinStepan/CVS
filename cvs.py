from cvs_dialogs import *
from cvs_tree import *
from cvs_errors import *
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


def _parse_message(message):
    parsed_message = message.split('\'')
    if len(parsed_message) != 3 \
            or (len(parsed_message) == 3 and (len(parsed_message[0]) > 0 or len(parsed_message[2]) > 0)):
        raise ValueError
    return parsed_message[1]


class CloneVersionSystem:
    def __init__(self):
        self.running = False
        self.main_folder = None
        self.cvs_tree: TreeCVS = None
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
            self.save_in_saver()

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

    def commit(self, message=None):
        if self.commit_index is None:
            print('Не добавлены изменения. Используйте команду \'add\'')
            return
        if message is None:
            message = self.cvs_tree.next_commit_folder_name
        else:
            try:
                message = _parse_message(message)
            except ValueError:
                print('Неверно указано сообщение к коммиту')
                return
            if message in self.cvs_tree.used_commits_name:
                print('Коммит с таким именем уже существует')
                return
        try:
            self.cvs_tree.create_commit(message, self.commit_index)
            print(f'Коммит {message} создан')
            self.save_in_saver()
            self.commit_index = None
        except DetachedHeadError as e:
            print(e)

    def checkout_commit(self, name):
        try:
            self.cvs_tree.checkout_commit(name)
            self.save_in_saver()
        except CommitNotFoundError as e:
            print(e)

    def create_tag(self, message):
        try:
            message = _parse_message(message)
        except ValueError:
            print('Неверно указано сообщение к тегу')
            return
        if message in self.cvs_tree.tags:
            print('Тег с таким именем уже существует')
            return
        self.cvs_tree.tags[message] = self.cvs_tree.current_commit.name

    def checkout_tag(self, name):
        if name in self.cvs_tree.tags:
            commit = self.cvs_tree.tags[name]
            self.cvs_tree.checkout_commit(commit)
            self.save_in_saver()
        else:
            print(f'Тег {name} не найден')

    def create_branch(self, name):
        if name in self.cvs_tree.used_branch_names:
            print('Ветвь с таким именем уже существует')
            return
        self.cvs_tree.create_branch(name)
        self.save_in_saver()

    def checkout_branch(self, name):
        try:
            self.cvs_tree.checkout_branch(name)
            self.save_in_saver()
        except BranchNotFoundError as e:
            print(e)

    def _find_commit_and_branch(self, name):
        for branch in self.cvs_tree.branches:
            if name in branch:
                for commit in branch.commits:
                    if name == commit.name:
                        return commit, branch.name
        raise CommitNotFoundError(name)

    def log_commit(self, name=None):
        if name is None:
            commit = self.cvs_tree.current_commit
            print(f'Ветка:  {self.cvs_tree.cur_branch}')
        else:
            try:
                commit, branch_name = self._find_commit_and_branch(name)
                print(f'Ветка:  {branch_name}')
            except CommitNotFoundError as e:
                print(e)
                return
        print(f'Коммит: {commit.name}')
        print(f'Создан: {commit.time.date()}  {commit.time.strftime("%H:%M:%S")}')
        print('Изменения:')
        for file in commit.index.new:
            print(colorama.Fore.GREEN + '+ ' + file)
        for file in commit.index.edited:
            print(colorama.Fore.YELLOW + 'Δ ' + file)
        for file in commit.index.deleted:
            print(colorama.Fore.RED + '- ' + file)

    def show_all_commits(self):
        for branch in self.cvs_tree.branches:
            print(f'Коммиты в ветви {branch}:')
            branch.show_commits()

    def show_commits_in_current_branch(self):
        print(f'Коммиты в ветви {self.cvs_tree.cur_branch}:')
        self.cvs_tree.cur_branch.show_commits()

    def show_tags(self):
        if len(self.cvs_tree.tags) == 0:
            print('Теги не добавлены')
        else:
            print('Список тегов:  (тег: коммит)')
            for tag in self.cvs_tree.tags:
                print(f'-- {tag}: {self.cvs_tree.tags[tag]}')

    def show_branches(self):
        print('Список веток:')
        for branch in self.cvs_tree.branches:
            print(f'-- {branch}')

    def do_command(self, command):
        if command != 'init' and not self.cvs_active:
            print('CVS не создан в текущей директории. Используйте команду \'init\'')
            return
        match command.split():
            case [('0' | 'stop')]:
                self.stop()
            case ['init']:
                self.init()

            case ['status']:
                self.status()
            case ['add', '.']:
                self.commit_index = self.cvs_tree.create_commit_index_with_all()
            case ['add', *names]:
                self.add_by_names(names)

            case ['commit']:
                self.commit()
            case ['commit', '-m', message]:
                self.commit(message)
            case ['branch', name]:
                self.create_branch(name)
            case ['tag', message]:
                self.create_tag(message)

            case ['checkout', name]:
                self.checkout_commit(name)
            case ['checkout', '-t', name]:
                self.checkout_tag(name)
            case ['checkout', '-b', name]:
                self.checkout_branch(name)

            case ['log']:
                self.log_commit()
            case ['log', name]:
                self.log_commit(name)

            case ['show']:
                self.show_commits_in_current_branch()
            case ['show', '-all']:
                self.show_all_commits()
            case ['show', '-t']:
                self.show_tags()
            case ['show', '-b']:
                self.show_branches()
            case _:
                print('Неверно введена команда')

    def run(self):
        print('Добро пожаловать в систему контроля версий CVS')
        self.running = True
        self.main_folder = read_recently_used_folder()
        self.reload_saver()
        if os.path.exists(f'{self.main_folder}\\{CVS_PATH}'):
            self.cvs_active = True
            self.cvs_tree = self.saved_cvs

        while self.running:
            command = input('>>> ')
            self.do_command(command)
            # print(f'\nBranch: {self.cvs_tree.cur_branch}\nCommit: {self.cvs_tree.current_commit}')
