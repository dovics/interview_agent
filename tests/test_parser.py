import unittest
import os
import tempfile
from unittest.mock import patch, MagicMock
from parser import parse_resume, _parse_pdf, _parse_docx, _parse_markdown


class TestParser(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_pdf_content = "This is a test PDF content"
        self.test_docx_content = "This is a test DOCX content"
        self.test_md_content = "# This is a test Markdown content"
        
    def test_parse_resume_with_pdf(self):
        """Test parsing a PDF resume file"""
        with patch('parser._parse_pdf') as mock_parse_pdf:
            mock_parse_pdf.return_value = self.test_pdf_content
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                tmp_file_path = tmp_file.name
            
            try:
                result = parse_resume(tmp_file_path)
                self.assertEqual(result, self.test_pdf_content)
                mock_parse_pdf.assert_called_once_with(tmp_file_path)
            finally:
                os.unlink(tmp_file_path)
    
    def test_parse_resume_with_docx(self):
        """Test parsing a DOCX resume file"""
        with patch('parser._parse_docx') as mock_parse_docx:
            mock_parse_docx.return_value = self.test_docx_content
            with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as tmp_file:
                tmp_file_path = tmp_file.name
            
            try:
                result = parse_resume(tmp_file_path)
                self.assertEqual(result, self.test_docx_content)
                mock_parse_docx.assert_called_once_with(tmp_file_path)
            finally:
                os.unlink(tmp_file_path)
    
    def test_parse_resume_with_markdown(self):
        """Test parsing a Markdown resume file"""
        with patch('parser._parse_markdown') as mock_parse_markdown:
            mock_parse_markdown.return_value = self.test_md_content
            with tempfile.NamedTemporaryFile(suffix='.md', delete=False) as tmp_file:
                tmp_file_path = tmp_file.name
            
            try:
                result = parse_resume(tmp_file_path)
                self.assertEqual(result, self.test_md_content)
                mock_parse_markdown.assert_called_once_with(tmp_file_path)
            finally:
                os.unlink(tmp_file_path)
    
    def test_parse_resume_with_unsupported_format(self):
        """Test parsing an unsupported file format"""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp_file:
            tmp_file_path = tmp_file.name
        
        try:
            with self.assertRaises(ValueError) as context:
                parse_resume(tmp_file_path)
            
            self.assertIn("Unsupported file format: .txt", str(context.exception))
        finally:
            os.unlink(tmp_file_path)
    
    @patch('parser.PyPDF2.PdfReader')
    def test_parse_pdf_success(self, mock_pdf_reader):
        """Test successful PDF parsing"""
        # Setup mock
        mock_page1 = MagicMock()
        mock_page1.extract_text.return_value = "Page 1 content"
        mock_page2 = MagicMock()
        mock_page2.extract_text.return_value = "Page 2 content"
        
        mock_reader_instance = MagicMock()
        mock_reader_instance.pages = [mock_page1, mock_page2]
        mock_pdf_reader.return_value = mock_reader_instance
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            tmp_file_path = tmp_file.name
        
        try:
            result = _parse_pdf(tmp_file_path)
            expected = "Page 1 content\nPage 2 content\n"
            self.assertEqual(result, expected)
        finally:
            os.unlink(tmp_file_path)
    
    @patch('parser.PyPDF2.PdfReader')
    def test_parse_pdf_exception(self, mock_pdf_reader):
        """Test PDF parsing with exception"""
        mock_pdf_reader.side_effect = Exception("PDF error")
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            tmp_file_path = tmp_file.name
        
        try:
            with self.assertRaises(Exception) as context:
                _parse_pdf(tmp_file_path)
            
            self.assertIn("Error parsing PDF: PDF error", str(context.exception))
        finally:
            os.unlink(tmp_file_path)
    
    @patch('parser.docx.Document')
    def test_parse_docx_success(self, mock_document):
        """Test successful DOCX parsing"""
        # Setup mock
        mock_paragraph1 = MagicMock()
        mock_paragraph1.text = "Paragraph 1 content"
        mock_paragraph2 = MagicMock()
        mock_paragraph2.text = "Paragraph 2 content"
        
        mock_doc_instance = MagicMock()
        mock_doc_instance.paragraphs = [mock_paragraph1, mock_paragraph2]
        mock_document.return_value = mock_doc_instance
        
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as tmp_file:
            tmp_file_path = tmp_file.name
        
        try:
            result = _parse_docx(tmp_file_path)
            expected = "Paragraph 1 content\nParagraph 2 content\n"
            self.assertEqual(result, expected)
        finally:
            os.unlink(tmp_file_path)
    
    @patch('parser.docx.Document')
    def test_parse_docx_exception(self, mock_document):
        """Test DOCX parsing with exception"""
        mock_document.side_effect = Exception("DOCX error")
        
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as tmp_file:
            tmp_file_path = tmp_file.name
        
        try:
            with self.assertRaises(Exception) as context:
                _parse_docx(tmp_file_path)
            
            self.assertIn("Error parsing DOCX: DOCX error", str(context.exception))
        finally:
            os.unlink(tmp_file_path)
    
    def test_parse_markdown_success(self):
        """Test successful Markdown parsing"""
        test_content = "# Test Resume\n\nThis is a test resume content."
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as tmp_file:
            tmp_file.write(test_content)
            tmp_file_path = tmp_file.name
        
        try:
            result = _parse_markdown(tmp_file_path)
            self.assertEqual(result, test_content)
        finally:
            os.unlink(tmp_file_path)
    
    def test_parse_markdown_exception(self):
        """Test Markdown parsing with exception"""
        # Try to read a non-existent file to trigger exception
        non_existent_file = "/tmp/non_existent_file.md"
        
        with self.assertRaises(Exception) as context:
            _parse_markdown(non_existent_file)
        
        self.assertIn("Error parsing markdown:", str(context.exception))


if __name__ == '__main__':
    unittest.main()