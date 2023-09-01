import datetime
import shutil
import os


class CommitIndex:
    def __init__(self):
        self.deleted = []
        self.new = []
        self.edited = []

    @property
    def all_files(self):
        return self.new + self.edited + self.deleted

    def get_dirs(self) -> set:
        dirs = set()
        for file in self.all_files:
            split_name = list(file.split('\\'))
            if len(split_name) > 1:
                path = '\\'.join(split_name[:-1])
                dirs.add(path)
        return dirs

    def __contains__(self, item):
        return item in self.deleted or item in self.new or item in self.edited


def create_folders_from_dir(directory: str, path):
    split_name = directory.split('\\')
    for i in range(len(split_name)):
        new_folder = '\\'.join(split_name[:i+1])
        folder = f'{path}\\{new_folder}'
        if os.path.exists(folder):
            continue
        else:
            os.mkdir(folder)


def get_files_for_update(new_file_paths, old_file_paths):
    result = []
    for key in new_file_paths:
        if key in old_file_paths and new_file_paths[key] == old_file_paths[key]:
            continue
        result.append(key)
    return result


def remove_files(files, path):
    for file in files:
        full_path = f'{path}\\{file}'
        os.remove(full_path)


class CommitCVS:
    def __init__(self, name, commit_index: CommitIndex, original_path, saver_folder, previous_commit=None):
        self.name = name
        self.time = datetime.datetime.now()
        self.directory = original_path
        self.index = commit_index
        self.files_and_paths = dict()
        if previous_commit is None:
            self.set_files_dict_without_previous(saver_folder)
        else:
            self.set_files_dict_with_previous(previous_commit, saver_folder)

    def __str__(self):
        return f'{self.name}'

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

    def _create_folders(self, folder):
        dirs = self.index.get_dirs()
        for path in dirs:
            create_folders_from_dir(path, folder)

    def _load_files_in_folder(self):
        for file in self.index.new + self.index.edited:
            old_path = f'{self.directory}\\{file}'
            shutil.copy2(old_path, self.files_and_paths[file])

    def save_files_in_folders(self, folder):
        self._create_folders(folder)
        self._load_files_in_folder()

    def checkout(self, old_commit):
        if self.name == old_commit.name:
            return
        current_all_files = set(self.files_and_paths.keys())
        old_all_files = set(old_commit.files_and_paths.keys())

        files_to_remove = old_all_files.difference(current_all_files)
        remove_files(files_to_remove, self.directory)

        files_to_update = get_files_for_update(self.files_and_paths, old_commit.files_and_paths)
        for file in files_to_update:
            shutil.copy2(self.files_and_paths[file], f'{self.directory}\\{file}')
