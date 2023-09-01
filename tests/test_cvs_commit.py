import unittest
from cvs_commit import *


ORIGINAL_PATH = 'C:\\orig'
SAVER_PATH = 'C:\\orig\\.cvs\\commits'


class TestCommitIndex(unittest.TestCase):
    def setUp(self) -> None:
        self.old_index = CommitIndex()
        self.old_index.new = ['g\\ed.txt', 'old.txt']

        self.old_commit = CommitCVS('old_com', self.old_index, ORIGINAL_PATH, f'{SAVER_PATH}\\com_0')

        self.new_index = CommitIndex()
        self.new_index.new = ['abc.txt', 'g\\f.txt']
        self.new_index.edited = ['g\\ed.txt']
        self.new_index.deleted = ['old.txt']

        self.new_commit = CommitCVS('new_com', self.new_index, ORIGINAL_PATH, f'{SAVER_PATH}\\com_1', self.old_commit)

    def testSTR(self):
        self.assertEqual('new_com', str(self.new_commit))
        self.assertEqual('old_com', str(self.old_commit))

    def testGetFilesForUpdate(self):
        result = get_files_for_update(self.new_commit.files_and_paths, self.old_commit.files_and_paths)
        expected = {'g\\ed.txt', 'abc.txt', 'g\\f.txt'}
        self.assertEqual(expected, set(result))

    def testSettingWithoutPrevious(self):
        commit = CommitCVS('com', self.old_index, ORIGINAL_PATH, f'{SAVER_PATH}\\com_0')
        expected = {
            'g\\ed.txt': 'C:\\orig\\.cvs\\commits\\com_0\\g\\ed.txt',
            'old.txt': 'C:\\orig\\.cvs\\commits\\com_0\\old.txt'
        }
        self.assertEqual(expected, commit.files_and_paths)

    def testSettingWithPrevious(self):
        commit = CommitCVS('com', self.new_index, ORIGINAL_PATH, f'{SAVER_PATH}\\com_1', self.old_commit)
        expected = {
            'g\\ed.txt': 'C:\\orig\\.cvs\\commits\\com_1\\g\\ed.txt',
            'abc.txt': 'C:\\orig\\.cvs\\commits\\com_1\\abc.txt',
            'g\\f.txt': 'C:\\orig\\.cvs\\commits\\com_1\\g\\f.txt'
        }
        self.assertEqual(expected, commit.files_and_paths)


if __name__ == '__main__':
    unittest.main()
