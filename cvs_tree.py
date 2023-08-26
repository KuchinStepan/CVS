import os


CVS_PATH = '.cvs'


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


class TreeCVS:
    def __init__(self, path):
        self.path = path
        commit_index = self.create_commit_index_with_all(True)
        initial_commit = CommitCVS('Initial commit', commit_index)
        self.main = BranchCVS('main', initial_commit)
        self.cur_branch = self.main
        self.commit_number = 0
        self.branches = [self.main]

    @property
    def current_commit(self):
        return self.cur_branch.commits[self.commit_number]

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

    def checkout_branch(self, branch_name):
        """Делает переход на ветку, при этом так же переходит на последний коммит в этой ветке"""
        i = -1
        for j in range(len(self.branches)):
            if self.branches[j] == branch_name:
                i = j
                self.cur_branch = self.branches[i]
                self.cur_branch.checkout_last()
                self.commit_number = self.cur_branch.current_number
                break
        if i == -1:
            return None
        return self.current_commit

    def checkout_commit(self, name):
        for branch in self.branches:
            if branch.contains(name):
                commit = branch.checkout_commit(name)
                self.cur_branch = branch
                self.commit_number = branch.current_number
                return commit
        return None


class CommitIndex:
    def __init__(self):
        self.deleted = []
        self.new = []
        self.edited = []

    def __contains__(self, item):
        return item in self.deleted or item in self.new or item in self.edited


class CommitCVS:
    def __init__(self, name, commit_index: CommitIndex, previous_commit=None):
        self.name = name
        self.index = commit_index
        self.files_and_paths = dict()
        if previous_commit is None:
            self.set_files_dict_without_previous()
        else:
            self.set_files_dict_with_previous(previous_commit)

    def set_files_dict_without_previous(self):
        for file in self.index.new:
            self.files_and_paths[file] = file

    def set_files_dict_with_previous(self, previous_commit):
        for file in previous_commit.files_and_paths:
            self.files_and_paths[file] = file
        #     ПРОПИСАТЬ СОЗДАНИЕ ПАПКИ И СОХРАНЯТЬ ССЫЛКУ НА ПУТЬ В НЕЕ
        for file in self.index.new:
            self.files_and_paths[file] = file
        for file in self.index.edited:
            self.files_and_paths[file] = file
        for file in self.index.deleted:
            if file in self.files_and_paths:
                self.files_and_paths.pop(file)


class BranchCVS:
    def __init__(self, name, root: CommitCVS):
        self.name = name
        self.root = root
        self.commits = [root]
        self.current = root
        self.current_number = 0

    def add_commit(self, commit, checkout=False):
        self.commits.append(commit)
        if checkout:
            self.current = commit

    def contains(self, commit_name):
        for c in self.commits:
            if c.name == commit_name:
                return True
        return False

    def checkout_commit(self, commit_name):
        i = -1
        for j in range(len(self.commits)):
            if self.commits[j] == commit_name:
                i = j
                self.current_number = i
                self.current = self.commits[i]
                break
        if i != -1:
            return self.current
        return None

    def checkout_last(self):
        self.current_number = len(self.commits) - 1
        self.current = self.commits[self.current_number]
        return self.current
