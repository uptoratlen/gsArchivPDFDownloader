import os
import shutil
import tempfile
import unittest
from os import path

from gsArchivPDFDownloader import filename_modification, wait_for_download

class MyTestCase(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory
        self.test_dir = tempfile.mkdtemp()
        self.testfilename='Gamestar_Dummy.PDF'
        with open(path.join(self.test_dir, self.testfilename+'.part'), 'w') as f:
            f.write('Only a dummy PDF aka ascii file')
        with open(path.join(self.test_dir, self.testfilename), 'w') as f:
            f.write('Only a dummy PDF aka ascii file')
        # print(path.join(self.test_dir, self.testfilename+'.part'))

    def tearDown(self):
        # Remove the directory after the test
        # shutil.rmtree(self.test_dir)
        pass

    def test_filename_modification_t1(self):
        # test without a missing optional edition2d arg
        actual_fd, actual_ft = filename_modification("GameStar Nr. <ausgabe>_<jahr>.pdf", "GameStar Nr. <ausgabe>_<jahr>.pdf", '4', '2021')
        expected_fd, expected_ft = ['GameStar Nr. 4_2021.pdf', 'GameStar Nr. 4_2021.pdf']
        self.assertEqual(expected_fd, actual_fd)
        self.assertEqual(expected_ft, actual_ft)

    def test_filename_modification_t2(self):
        # test with optional edition2d arg YES
        actual_fd, actual_ft = filename_modification("GameStar Nr. <ausgabe>_<jahr>.pdf", "GameStar Nr. <ausgabe>_<jahr>.pdf", '4', '2021', 'YES')
        expected_fd, expected_ft = ['GameStar Nr. 4_2021.pdf', 'GameStar Nr. 04_2021.pdf']
        self.assertEqual(expected_fd, actual_fd)
        self.assertEqual(expected_ft, actual_ft)

    def test_filename_modification_t3(self):
        # test with optional edition2d arg NO
        actual_fd, actual_ft = filename_modification("GameStar Nr. <ausgabe>_<jahr>.pdf", "GameStar Nr. <ausgabe>_<jahr>.pdf", '4', '2021', 'NO')
        expected_fd, expected_ft = ['GameStar Nr. 4_2021.pdf', 'GameStar Nr. 4_2021.pdf']
        self.assertEqual(expected_fd, actual_fd)
        self.assertEqual(expected_ft, actual_ft)

    def test_filename_modification_t4(self):
        # test with int not string
        with self.assertRaises(SystemExit) as cm:
            filename_modification("GameStar Nr. <ausgabe>_<jahr>.pdf", "GameStar Nr. <ausgabe>_<jahr>.pdf", 4, 2021, 'NO')
        self.assertEqual(cm.exception.code, 99)

    def test_filename_modification_t5(self):
        # test with int not string
        actual_fd, actual_ft = filename_modification("GameStar Nr. <ausgabe>_<jahr>.pdf", "GameStar Nr. <ausgabe>_<jahr>.pdf", "04", "2021", 'yes')
        expected_fd, expected_ft = ['GameStar Nr. 4_2021.pdf', 'GameStar Nr. 04_2021.pdf']
        self.assertEqual(expected_fd, actual_fd)
        self.assertEqual(expected_ft, actual_ft)

    def test_wait_for_download_t1(self):
        # check if partial is not seen
        filedownloadfullpath =str(path.join(self.test_dir, self.testfilename))
        self.assertEqual(False, wait_for_download(filedownloadfullpath, timeout=3))

    def test_wait_for_download_t2(self):
        # check if partial is not seen anymore
        os.remove(path.join(self.test_dir, self.testfilename+'.part'))
        filedownloadfullpath =str(path.join(self.test_dir, self.testfilename))
        self.assertEqual(True, wait_for_download(filedownloadfullpath, timeout=3))

if __name__ == '__main__':
    unittest.main()
