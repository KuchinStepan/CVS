from cvs_errors import *
from cvs_commit import *
import os
import hashlib


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


def get_file_hash(file_path):
    with open(file_path, 'rb') as f:
        content = f.read()
        return hashlib.md5(content)


class TreeCVS:
    def __init__(self, path):
        self.used_commits_name = set()
        self.tags = dict()
        self.path = path
        self.commits_count = 0
        commit_index = self.create_commit_index_with_all(True)
        initial_commit = self.create_commit('Initial_commit', commit_index, True)
        self.main = BranchCVS('main', initial_commit)
        self.cur_branch = self.main
        self.branches = [self.main]

        self.used_branch_names = set()
        self.used_branch_names.add('main')

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

    def find_edited_files(self, all_files: set):
        current_commit = self.current_commit
        last_files = set(current_commit.files_and_paths.keys())
        files_for_checking = set(all_files.intersection(last_files))
        result = []
        for file in files_for_checking:
            previous_hash = get_file_hash(current_commit.files_and_paths[file]).digest()
            current_hash = get_file_hash(f'{self.path}\\{file}').digest()
            if previous_hash != current_hash:
                result.append(file)
        return result

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
        com_index.edited = self.find_edited_files(all_files)
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
        commit.save_files_in_folders(com_path)
        if not initial:
            self.cur_branch.add_commit(commit)

        self.commits_count += 1
        self.used_commits_name.add(name)
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

    def create_branch(self, name):
        branch = BranchCVS(name, self.current_commit)
        self.branches.append(branch)
        self.cur_branch = branch
        self.used_branch_names.add(name)

    def checkout_branch(self, branch_name):
        """Делает переход на ветку, при этом так же переходит на последний коммит в этой ветке"""
        old_commit = self.current_commit
        if self.cur_branch.name == branch_name:
            return
        for i in range(len(self.branches)):
            if self.branches[i].name == branch_name:
                self.cur_branch = self.branches[i]
                self.cur_branch.checkout_last(old_commit)
                return
        raise BranchNotFoundError(branch_name)


class BranchCVS:
    def __init__(self, name, root: CommitCVS):
        self.name = name
        self.root = root
        self.commits = [root]
        self.current_number = 0

    def __str__(self):
        return f'{self.name}'

    @property
    def current_commit(self):
        return self.commits[self.current_number]

    @property
    def last_commit_taken(self):
        return self.current_number == len(self.commits) - 1

    def show_commits(self):
        for commit in reversed(self.commits):
            print(f'-- {commit}')

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
        for i in range(len(self.commits)):
            if self.commits[i].name == commit_name:
                self.current_number = i
                self.current_commit.checkout(old_commit)
                return
        raise CommitNotFoundError(commit_name)

    def checkout_last(self, previous_commit):
        self.current_number = len(self.commits) - 1
        self.current_commit.checkout(previous_commit)
