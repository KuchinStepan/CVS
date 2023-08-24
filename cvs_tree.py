import os


CVS_PATH = '.cvs'


class TreeCVS:
    def __init__(self, path):
        self.path = path
        commit_index = self.create_commit_index_with_all(True)

        initial_commit = CommitCVS('Initial commit', commit_index, 'main')
        self.main = BranchCVS('main', initial_commit)
        self.cur_branch = self.main
        self.commit_number = 0
        self.branches = [self.main]

    @property
    def current_commit(self):
        return self.cur_branch.commits[self.commit_number]

    def find_new_files(self):
        pass

    def get_all_files(self, directory=''):
        """Находит все файлы (в том числе вложенные) в директории (кроме папок)"""
        if directory == '':
            files = os.listdir(self.path)
        else:
            files = list(map(lambda name: f'{directory}\\{name}', os.listdir(f'{self.path}\\{directory}')))
        result_list = list(files)
        for file in files:
            if file == CVS_PATH:
                result_list.remove(CVS_PATH)
                continue
            if os.path.isdir(f'{self.path}\\{file}'):
                result_list += self.get_all_files(file)
                result_list.remove(file)
        return result_list

    def get_all_files1(self, directory=''):
        if directory == '':
            files = os.listdir(self.path)
        else:
            files = os.listdir(f'{self.path}{directory}')
        result_list = list(files)
        for file in files:
            if file == CVS_PATH:
                result_list.remove(CVS_PATH)
                continue
            if (directory == '' and os.path.isdir(f'{self.path}\\{file}')) \
                    or (directory != '' and os.path.isdir(f'{self.path}{directory}\\{file}')):
                result_list += list(map(lambda name: f'{directory}\\{name}',
                                        self.get_all_files(f'{directory}\\{file}')))
                result_list.remove(file)
        return result_list

    def create_commit_index_with_all(self, initial=False):
        com_index = CommitIndex()
        if initial:
            com_index.new = self.get_all_files()
            return com_index

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


class CommitCVS:
    def __init__(self, name, commit_index, branch_name):
        self.name = name
        self.index = commit_index
        self.branch_name = branch_name


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


class CommitIndex:
    def __init__(self):
        self.deleted = []
        self.new = []
        self.edited = []
