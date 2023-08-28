class DetachedHeadError(Exception):
    def __init__(self, commit_name, *args):
        self.commit_name = commit_name

    def __str__(self):
        return f'Не возможно создать коммит {self.commit_name} обособленно.\n' \
               f'Попробуйте сделать новую ветку (команда \'branch\')'
