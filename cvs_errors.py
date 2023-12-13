class DetachedHeadError(Exception):
    def __init__(self, commit_name, *args):
        self.commit_name = commit_name

    def __str__(self):
        return f'Не возможно создать коммит {self.commit_name} обособленно.\n' \
               f'Попробуйте сделать новую ветку (команда \'branch\')'


class CommitNotFoundError(Exception):
    def __init__(self, commit_name):
        self.commit_name = commit_name

    def __str__(self):
        return f'Коммит {self.commit_name} не найден'


class BranchNotFoundError(Exception):
    def __init__(self, branch_name):
        self.branch_name = branch_name

    def __str__(self):
        return f'Ветвь {self.branch_name} не найдена'


class FileDiffError(Exception):
    def __init__(self, message=''):
        self.message = message

    def __str__(self):
        return self.message
