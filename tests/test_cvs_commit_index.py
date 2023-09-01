import unittest
from cvs_commit import CommitIndex


class TestCommitIndex(unittest.TestCase):
    def setUp(self) -> None:
        self.index = CommitIndex()
        self.index.new = ['a\\b.txt', 'p.txt', 'a\\v\\m.txt']
        self.index.edited = ['a\\c.txt', 's.txt']
        self.index.deleted = ['a\\v\\p.txt']

    def testAllFiled(self):
        expected = {'a\\b.txt', 'p.txt', 'a\\v\\m.txt',
                    'a\\c.txt', 's.txt', 'a\\v\\p.txt'}
        result = self.index.all_files
        self.assertEqual(expected, set(result))

    def testGetDirs(self):
        expected = {'a', 'a\\v'}
        result = self.index.get_dirs()
        self.assertEqual(expected, result)

    def testContains(self):
        item = 'a\\v\\p.txt'
        self.assertTrue(item in self.index)

    def testNotContains(self):
        item = 'a\\v\\z.txt'
        self.assertFalse(item in self.index)


if __name__ == '__main__':
    unittest.main()
