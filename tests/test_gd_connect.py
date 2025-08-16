# tests/test_gd_connect.py

import unittest
from unittest.mock import MagicMock, patch
from gd_connect.drive import GoogleDrive
from gd_connect.utils import guess_mime_type, format_file_info


class TestUtils(unittest.TestCase):
    def test_guess_mime_type_txt(self):
        self.assertEqual(guess_mime_type("file.txt"), "text/plain")

    def test_guess_mime_type_unknown(self):
        self.assertEqual(guess_mime_type("file.unknownext"), "application/octet-stream")

    def test_format_file_info(self):
        file_data = {"id": "12345", "name": "test.txt"}
        self.assertEqual(format_file_info(file_data), "test.txt (12345)")


class TestGoogleDrive(unittest.TestCase):
    @patch("gd_connect.drive.build")
    def setUp(self, mock_build):
        """Mock Google Drive API service"""
        self.mock_service = MagicMock()
        mock_build.return_value = self.mock_service
        creds = MagicMock()
        self.drive = GoogleDrive(creds)

    def test_list_files(self):
        # Mock API response
        self.mock_service.files().list().execute.return_value = {
            "files": [{"id": "1", "name": "test.txt"}]
        }
        files = self.drive.list_files(page_size=1)
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0]["name"], "test.txt")

    def test_upload_file(self):
        # Mock upload
        mock_request = MagicMock()
        mock_request.next_chunk.side_effect = [(MagicMock(progress=lambda: 1.0), {"id": "123"})]
        self.mock_service.files().create.return_value = mock_request

        file_id = self.drive.upload_file("dummy.txt", "uploaded.txt")
        self.assertEqual(file_id, "123")

    def test_download_file(self):
        # Mock download
        mock_request = MagicMock()
        self.mock_service.files().get_media.return_value = mock_request
        mock_downloader = MagicMock()
        mock_downloader.next_chunk.side_effect = [(MagicMock(progress=lambda: 1.0), True)]

        with patch("gd_connect.drive.MediaIoBaseDownload", return_value=mock_downloader):
            self.drive.download_file("file123", "local.txt")
            self.mock_service.files().get_media.assert_called_with(fileId="file123")

    def test_delete_file(self):
        # Mock delete success
        self.mock_service.files().delete.return_value.execute.return_value = {}
        result = self.drive.delete_file("file123")
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
