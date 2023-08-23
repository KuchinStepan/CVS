import os


class TreeCVS:
    def __init__(self, path):
        self.path = path
        commit_index = CommitIndex()
        commit_index.new = os.listdir(path)
        initial_commit = CommitCVS('Initial commit', commit_index)
        self.main = BranchCVS('main', initial_commit)


class BranchCVS:
    def __init__(self, name, root):
        self.name = name
        self.root = root
        self.commits = [root]
        self.current = root

    def add_commit(self, commit, checkout=False):
        self.commits.append(commit)
        if checkout:
            self.current = commit


class CommitCVS:
    def __init__(self, name, commit_index):
        self.name = name
        self.index = commit_index


class CommitIndex:
    def __init__(self):
        self.deleted = []
        self.new = []
        self.edited = []
