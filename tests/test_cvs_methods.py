import cvs
import cvs_tree
import unittest


class TestCommitIndex(unittest.TestCase):
    def testDeleteLastComma(self):
        s = 'test,'
        self.assertEqual(s[:-1], cvs._delete_last_comma(s))

    def testNotDeleteLastSymbol(self):
        s = 'test'
        self.assertEqual(s, cvs._delete_last_comma(s))

    def testNotDeleteMiddleComma(self):
        s = 'test,3'
        self.assertEqual(s, cvs._delete_last_comma(s))

    def testParseRightMessage(self):
        result = cvs._parse_message('\'message\'')
        self.assertEqual('message', result)

    def testParseWrongMessageWithTestBefore(self):
        self.assertRaises(ValueError, cvs._parse_message, 'df\'sdf\'')

    def testParseWrongMessageWithTestAfter(self):
        self.assertRaises(ValueError, cvs._parse_message, '\'sdf\'ss')

    def testParseWrongMessageWithManyQuotes(self):
        self.assertRaises(ValueError, cvs._parse_message, '\'sd\'f\'')

    def testGetAllFilesWithoutEnclosure(self):
        result = cvs_tree.get_all_files('test_directories_0')
        expected = {'t0.txt', 't1.txt'}
        self.assertEqual(expected, set(result))

    def testGetAllFilesWithEnclosure(self):
        result = cvs_tree.get_all_files('test_directories_1')
        expected = {'t1.txt', 'a\\t2.txt', 'a\\b\\t3.txt'}
        self.assertEqual(expected, set(result))


if __name__ == '__main__':
    unittest.main()
