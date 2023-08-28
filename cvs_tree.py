from detached_head_error import DetachedHeadError, CommitNotFoundError
import os
import shutil


CVS_PATH = '.cvs'
COMMITS_PATH = f'{CVS_PATH}\\commits'


def get_all_files(path, directory=''):
    """Находит все файлы (в том числе вложенные) в директории (кроме папок)"""
    if directory == '':
        files = os.listdir(path)
    else:
        files = list(map(lambda name: f'{directory}\\{name}', os.listdir(f'{path}\\{directory}')))
    result_list = list(files)
    for file in files:
        if file == CVS_PATH:
            result_list.remove(CVS_PATH)
            continue
        if os.path.isdir(f'{path}\\{file}'):
            result_list += get_all_files(path, file)
            result_list.remove(file)
    return result_list


def create_folders_from_dir(directory: str, path):
    split_name = directory.split('\\')
    for i in range(len(split_name)):
        new_folder = '\\'.join(split_name[:i+1])
        folder = f'{path}\\{new_folder}'
        if os.path.exists(folder):
            continue
        else:
            os.mkdir(folder)


class TreeCVS:
    def __init__(self, path):
        self.path = path
        self.commits_count = 0
        commit_index = self.create_commit_index_with_all(True)
        initial_commit = self.create_commit('Initial_commit', commit_index, True)
        self.main = BranchCVS('main', initial_commit)
        self.cur_branch = self.main
        self.branches = [self.main]

    @property
    def commit_number(self):
        return self.cur_branch.current_number

    @property
    def current_commit(self):
        return self.cur_branch.commits[self.commit_number]

    @property
    def next_commit_folder_name(self):
        return f'com_{self.commits_count}'

    def find_new_files(self, all_files):
        last_files = set(self.current_commit.files_and_paths.keys())
        return list(all_files.difference(last_files))

    def find_deleted_files(self, all_files):
        last_files = set(self.current_commit.files_and_paths.keys())
        return list(last_files.difference(all_files))

    def create_commit_index_with_all(self, initial=False):
        com_index = CommitIndex()
        if initial:
            com_index.new = get_all_files(self.path)
            return com_index
        all_files = set(get_all_files(self.path))
        com_index.new = self.find_new_files(all_files)
        com_index.deleted = self.find_deleted_files(all_files)
        return com_index

    def update_commit_index_by_names(self, commit_index, names):
        full_index = self.create_commit_index_with_all()
        for name in names:
            if name not in commit_index:
                if name in full_index.new:
                    commit_index.new.append(name)
                elif name in full_index.deleted:
                    commit_index.deleted.append(name)
                elif name in full_index.edited:
                    commit_index.edited.append(name)
                else:
                    raise FileNotFoundError(name, name, name)
        return commit_index

    def create_commit(self, name, commit_index, initial=False):
        if not initial:
            if not self.cur_branch.last_commit_taken:
                raise DetachedHeadError(name)
            previous = self.current_commit
        else:
            previous = None
        com_path = f'{self.path}\\{COMMITS_PATH}\\{self.next_commit_folder_name}'
        os.mkdir(com_path)
        commit = CommitCVS(name, commit_index, self.path, com_path, previous)
        if not initial:
            self.cur_branch.add_commit(commit)

        self.commits_count += 1
        return commit

    def checkout_commit(self, name):
        if name in self.cur_branch:
            self.cur_branch.checkout_commit(name, self.current_commit)
            return
        for branch in self.branches:
            if name in branch:
                branch.checkout_commit(name, self.current_commit)
                self.cur_branch = branch
                return
        raise CommitNotFoundError(name)

    def checkout_branch(self, branch_name):
        """Делает переход на ветку, при этом так же переходит на последний коммит в этой ветке"""
        i = -1
        for j in range(len(self.branches)):
            if self.branches[j] == branch_name:
                i = j
                self.cur_branch = self.branches[i]
                self.cur_branch.checkout_last()
                break
        if i == -1:
            return None
        return self.current_commit


class CommitIndex:
    def __init__(self):
        self.deleted = []
        self.new = []
        self.edited = []

    @property
    def all_files(self):
        return self.new + self.edited + self.deleted

    def get_dirs(self):
        dirs = set()
        for file in self.all_files:
            split_name = list(file.split('\\'))
            if len(split_name) > 1:
                path = '\\'.join(split_name[:-1])
                dirs.add(path)
        return dirs

    def __contains__(self, item):
        return item in self.deleted or item in self.new or item in self.edited


def remove_files(files, path):
    for file in files:
        full_path = f'{path}\\{file}'
        os.remove(full_path)


def get_files_for_update(new_file_paths, old_file_paths):
    result = []
    for key in new_file_paths:
        if key in old_file_paths and new_file_paths[key] == old_file_paths[key]:
            continue
        result.append(key)
    return result


class CommitCVS:
    def __init__(self, name, commit_index: CommitIndex, original_path, saver_folder, previous_commit=None):
        self.name = name
        self.directory = original_path
        self.index = commit_index
        self.files_and_paths = dict()
        if previous_commit is None:
            self.set_files_dict_without_previous(saver_folder)
        else:
            self.set_files_dict_with_previous(previous_commit, saver_folder)
        self.create_folders(saver_folder)
        self.load_files_in_folder()

    def set_files_dict_without_previous(self, folder):
        for file in self.index.new:
            self.files_and_paths[file] = f'{folder}\\{file}'

    def set_files_dict_with_previous(self, previous_commit, folder):
        for file in previous_commit.files_and_paths:
            self.files_and_paths[file] = previous_commit.files_and_paths[file]
        for file in self.index.new:
            self.files_and_paths[file] = f'{folder}\\{file}'
        for file in self.index.edited:
            self.files_and_paths[file] = f'{folder}\\{file}'
        for file in self.index.deleted:
            if file in self.files_and_paths:
                self.files_and_paths.pop(file)

    def create_folders(self, folder):
        dirs = self.index.get_dirs()
        for path in dirs:
            create_folders_from_dir(path, folder)

    def load_files_in_folder(self):
        for file in self.index.new + self.index.edited:
            old_path = f'{self.directory}\\{file}'
            shutil.copy2(old_path, self.files_and_paths[file])

    def checkout(self, old_commit):
        current_all_files = set(self.files_and_paths.keys())
        old_all_files = set(old_commit.files_and_paths.keys())

        files_to_remove = old_all_files.difference(current_all_files)
        remove_files(files_to_remove, self.directory)

        files_to_update = get_files_for_update(self.files_and_paths, old_commit.files_and_paths)
        for file in files_to_update:
            shutil.copy2(self.files_and_paths[file], f'{self.directory}\\{file}')


class BranchCVS:
    def __init__(self, name, root: CommitCVS):
        self.name = name
        self.root = root
        self.commits = [root]
        self.current_number = 0

    @property
    def current_commit(self):
        return self.commits[self.current_number]

    @property
    def last_commit_taken(self):
        return self.current_number == len(self.commits) - 1

    def add_commit(self, commit, checkout=True):
        self.commits.append(commit)
        if checkout:
            self.current_number += 1

    def __contains__(self, item):
        for c in self.commits:
            if c.name == item:
                return True
        return False

    def checkout_commit(self, commit_name, old_commit):
        if commit_name == self.current_commit.name:
            return
        for i in range(len(self.commits)):
            if self.commits[i].name == commit_name:
                self.current_number = i
                self.current_commit.checkout(old_commit)
                return
        raise CommitNotFoundError(commit_name)

    def checkout_last(self):
        self.current_number = len(self.commits) - 1
        return self.current
