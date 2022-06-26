import os
import shutil
import tempfile
import unittest
from os import path

from gsArchivPDFDownloader import filename_modification, wait_for_download, move_downloaded, json_config_check


class MyTestCase(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory
        self.test_dir = tempfile.mkdtemp()
        print(self.test_dir)
        self.testfilename = 'Gamestar_Dummy.PDF'
        with open(path.join(self.test_dir, self.testfilename+'.part'), 'w') as f:
            f.write('Only a dummy PDF aka ascii file')
        with open(path.join(self.test_dir, self.testfilename), 'w') as f:
            f.write('Only a dummy PDF aka ascii file')
        # print(path.join(self.test_dir, self.testfilename+'.part'))

    def tearDown(self):
        # Remove the directory after the test
        shutil.rmtree(self.test_dir)

    def test_filename_modification_t1(self):
        # test without a missing optional edition2d arg
        actual_fd, actual_fdwd, actual_ft = filename_modification("GameStar Nr. <ausgabe>_<jahr>.pdf", "GameStar Nr.*<ausgabe>_<jahr>.pdf",
                                                     "GameStar Nr. <ausgabe>_<jahr>.pdf", '4', '2021')
        expected_fd, expected_fdwd, expected_ft = ['GameStar Nr. 4_2021.pdf', 'GameStar Nr.*4_2021.pdf','GameStar Nr. 4_2021.pdf']
        self.assertEqual(expected_fd, actual_fd)
        self.assertEqual(expected_fdwd, actual_fdwd)
        self.assertEqual(expected_ft, actual_ft)

    def test_filename_modification_t2(self):
        # test with optional edition2d arg YES
        actual_fd, actual_fdwd, actual_ft = filename_modification("GameStar Nr. <ausgabe>_<jahr>.pdf", "GameStar Nr.*<ausgabe>_<jahr>.pdf",
                                                     "GameStar Nr. <ausgabe>_<jahr>.pdf", '4', '2021', 'YES')
        expected_fd, expected_fdwd, expected_ft = ['GameStar Nr. 4_2021.pdf','GameStar Nr.*4_2021.pdf', 'GameStar Nr. 04_2021.pdf']
        self.assertEqual(expected_fd, actual_fd)
        self.assertEqual(expected_fdwd, actual_fdwd)
        self.assertEqual(expected_ft, actual_ft)

    def test_filename_modification_t3(self):
        # test with optional edition2d arg NO
        actual_fd, actual_fdwd, actual_ft = filename_modification("GameStar Nr. <ausgabe>_<jahr>.pdf", "GameStar Nr.*<ausgabe>_<jahr>.pdf",
                                                     "GameStar Nr. <ausgabe>_<jahr>.pdf", '4', '2021', 'NO')
        expected_fd, expected_fdwd, expected_ft = ['GameStar Nr. 4_2021.pdf','GameStar Nr.*4_2021.pdf', 'GameStar Nr. 4_2021.pdf']
        self.assertEqual(expected_fd, actual_fd)
        self.assertEqual(expected_fdwd, actual_fdwd)
        self.assertEqual(expected_ft, actual_ft)

    def test_filename_modification_t4(self):
        # test with int not string
        with self.assertRaises(SystemExit) as cm:
            filename_modification("GameStar Nr. <ausgabe>_<jahr>.pdf", "GameStar Nr.*<ausgabe>_<jahr>.pdf",
                                  "GameStar Nr. <ausgabe>_<jahr>.pdf", 4, 2021, 'NO')
        self.assertEqual(cm.exception.code, 99)

    def test_filename_modification_t5(self):
        # test with int not string
        actual_fd, actual_fdwd, actual_ft = filename_modification("GameStar Nr. <ausgabe>_<jahr>.pdf", "GameStar Nr.*<ausgabe>_<jahr>.pdf",
                                                     "GameStar Nr. <ausgabe>_<jahr>.pdf", "04", "2021", 'yes')
        expected_fd, expected_fdwd, expected_ft = ['GameStar Nr. 4_2021.pdf','GameStar Nr.*4_2021.pdf', 'GameStar Nr. 04_2021.pdf']
        self.assertEqual(expected_fd, actual_fd)
        self.assertEqual(expected_fdwd, actual_fdwd)
        self.assertEqual(expected_ft, actual_ft)

    def test_wait_for_download_t1(self):
        # check if partial is not seen
        filedownloadfullpath = str(path.join(self.test_dir, self.testfilename))
        self.assertEqual(False, wait_for_download(filedownloadfullpath, timeout=3))

    def test_wait_for_download_t2(self):
        # check if partial is not seen anymore
        os.remove(path.join(self.test_dir, self.testfilename+'.part'))
        filedownloadfullpath = str(path.join(self.test_dir, self.testfilename))
        self.assertEqual(True, wait_for_download(filedownloadfullpath, timeout=3))

    def test_move_downloaded_t1(self):
        # check in case no source file is existing
        self.assertEqual(False, move_downloaded(self.test_dir, 1999, "DateiA", self.testfilename, 3))

    def test_move_downloaded_t2(self):
        # check in case source file is existing
        self.assertEqual(True, move_downloaded(self.test_dir, 1999, self.testfilename, self.testfilename, 3))

    def test_json_config_check_t1(self):
        # check if exist is not called if all keys are found
        self.json_test_dict = {'log_level': 'INFO', 'downloadtarget': 'c:\\download\\Gamestar-archive', 'edition2d': 'Yes',
         'downloadtimeout': 240, 'abortlimit': 2, 'filenamepattern_intarget': 'GameStar Nr. <ausgabe>_<jahr>.pdf',
         'filenamepattern_fromserver': 'GameStar Nr. <ausgabe>_<jahr>.pdf',
         'latestdownload': [{'year': '2021', 'edition': '5'}], 'browser_display_on_latest': 'no',
         'skip_editions': [{'2017': '10'}]}
        self.json_test_key_list = ['log_level', 'downloadtarget', 'edition2d', 'downloadtimeout', 'abortlimit', 'filenamepattern_intarget',
             'filenamepattern_fromserver', 'latestdownload', 'browser_display_on_latest', 'skip_editions']
        self.assertEqual(True, json_config_check(self.json_test_dict, self.json_test_key_list))


    def test_json_config_check_t2(self):
        # check if exist is called if one key is not found
        self.json_test_dict = {'log_level': 'INFO', 'downloadtarget': 'c:\\download\\Gamestar-archive', 'edition2d': 'Yes',
         'downloadtimeout': 240, 'abortlimit': 2, 'filenamepattern_intarget': 'GameStar Nr. <ausgabe>_<jahr>.pdf',
         'filenamepattern_fromserver': 'GameStar Nr. <ausgabe>_<jahr>.pdf',
         'latestdownload': [{'year': '2021', 'edition': '5'}], 'browser_display_on_latest': 'no',
         'skip_editions': [{'2017': '10'}]}
        self.json_test_key_list = ['log_level', 'new_key']
        with self.assertRaises(SystemExit) as cm:
            json_config_check(self.json_test_dict, self.json_test_key_list)
        self.assertEqual(cm.exception.code, 99)


if __name__ == '__main__':
    unittest.main()
