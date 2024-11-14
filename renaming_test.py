from dotenv import load_dotenv
import os
import unittest
from unittest.mock import patch, MagicMock
from file_renamer import FileRenameHandler
load_dotenv()

class TestFileRenameHandler(unittest.TestCase):
    
    @patch('file_renamer.OpenAI')

    def test_valid_rename_on_first_attempt(self, mock_openai):
        # Mock GPT response with filenames that match the regex on the first try
        mock_openai_instance = mock_openai.return_value
        mock_openai_instance.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="REGEX: ^\\d{4}-\\d{2}-\\d{2}_.*\\.ext$\nNAMES:\nfile1.txt -> 2024-11-14_file1.txt\nfile2.txt -> 2024-11-14_file2.txt"))]
        )

        handler = FileRenameHandler()
        name_mappings = handler.process_rename_request(directory=os.getenv("HOST_FOLDER"), naming_request="YYYY-MM-DD_filename.ext")
        
        expected_mappings = {
            "file1.txt": "2024-11-14_file1.txt",
            "file2.txt": "2024-11-14_file2.txt"
        }
        self.assertEqual(name_mappings, expected_mappings)

    @patch('file_renamer.OpenAI')
    def test_retry_until_match(self, mock_openai):
        # Mock GPT responses to require multiple retries
        mock_openai_instance = mock_openai.return_value
        # First response (doesn't match regex)
        mock_openai_instance.chat.completions.create.side_effect = [
            MagicMock(choices=[MagicMock(message=MagicMock(content="REGEX: ^\\d{4}-\\d{2}-\\d{2}_.*\\.ext$\nNAMES:\nfile1.txt -> file1_2024.txt\nfile2.txt -> file2_2024.txt"))]),
            # Second response (matches regex)
            MagicMock(choices=[MagicMock(message=MagicMock(content="REGEX: ^\\d{4}-\\d{2}-\\d{2}_.*\\.ext$\nNAMES:\nfile1.txt -> 2024-11-14_file1.txt\nfile2.txt -> 2024-11-14_file2.txt"))])
        ]
        
        handler = FileRenameHandler()
        name_mappings = handler.process_rename_request(directory=os.getenv("HOST_FOLDER"), naming_request="rename the file to following: YYYY-MM-DD_filename.ext")

        expected_mappings = {
            "file1.txt": "2024-11-14_file1.txt",
            "file2.txt": "2024-11-14_file2.txt"
        }
        self.assertEqual(name_mappings, expected_mappings)

    @patch('file_renamer.OpenAI')
    def test_max_retries_exceeded(self, mock_openai):
        # Mock GPT responses that don't match regex at all
        mock_openai_instance = mock_openai.return_value
        mock_openai_instance.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="REGEX: ^\\d{4}-\\d{2}-\\d{2}_.*\\.ext$\nNAMES:\nfile1.txt -> file1_2024.txt\nfile2.txt -> file2_2024.txt"))]
        )

        handler = FileRenameHandler()

        with self.assertRaises(ValueError) as context:
            handler.process_rename_request(directory=os.getenv("HOST_FOLDER"), naming_request="YYYY-MM-DD_filename.ext", max_retries=2)

        self.assertEqual(str(context.exception), "Could not generate valid file names after 2 attempts.")

