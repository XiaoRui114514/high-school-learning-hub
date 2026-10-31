"""用最小 DOCX 验证阅读时不会静默丢失文本；不读取教材或学习记录。"""
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "extract_word_text.py"
SPEC = importlib.util.spec_from_file_location("extract_word_text", SCRIPT)
word = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(word)
NS = word.NS["w"]


def paragraph(text):
    return "<w:p><w:r><w:t>%s</w:t></w:r></w:p>" % text


def table(text):
    return "<w:tbl><w:tr><w:tc>%s</w:tc></w:tr></w:tbl>" % paragraph(text)


class WordExtractionTests(unittest.TestCase):
    def cli(self, body, *args):
        with tempfile.TemporaryDirectory() as tmp:
            docx = Path(tmp) / "sample.docx"
            with zipfile.ZipFile(docx, "w") as archive:
                archive.writestr("word/document.xml", (
                    '<w:document xmlns:w="%s"><w:body>%s</w:body></w:document>'
                    % (NS, body)
                ))
            return subprocess.run(
                [sys.executable, str(SCRIPT), str(docx), *args],
                capture_output=True, text=True, encoding="utf-8", check=False,
            )

    def test_tabs_and_breaks_keep_words_separate(self):
        element = ET.fromstring(
            '<w:p xmlns:w="%s"><w:r><w:t>first</w:t><w:tab/>'
            '<w:t>second</w:t><w:br/><w:t>third</w:t><w:cr/>'
            '<w:t>fourth</w:t></w:r></w:p>' % NS
        )
        self.assertEqual(word.text_of(element), "first\tsecond\nthird\nfourth")

    def test_cell_paragraphs_keep_numbers_separate(self):
        element = ET.fromstring(
            '<w:tc xmlns:w="%s">%s%s</w:tc>' % (NS, paragraph("12"), paragraph("34"))
        )
        self.assertEqual(word.text_of(element), "12\n34")

    def test_run_boundaries_do_not_insert_spaces_into_words(self):
        element = ET.fromstring(
            '<w:p xmlns:w="%s"><w:r><w:t>hel</w:t></w:r>'
            '<w:r><w:t>lo</w:t></w:r></w:p>' % NS
        )
        self.assertEqual(word.text_of(element), "hello")

    def test_range_keeps_following_table_and_excludes_other_paragraphs(self):
        body = paragraph("first") + table("kept") + paragraph("second") + table("excluded")
        result = self.cli(body, "--start", "1", "--end", "1")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("[P1] first", result.stdout)
        self.assertIn("[表] kept", result.stdout)
        self.assertNotIn("second", result.stdout)
        self.assertNotIn("excluded", result.stdout)

    def test_range_keeps_leading_table(self):
        result = self.cli(table("leading") + paragraph("first"), "--end", "1")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("[表] leading", result.stdout)

    def test_table_only_document_keeps_table_in_open_ended_range(self):
        result = self.cli(table("only"), "--start", "1")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("[表] only", result.stdout)

    def test_later_range_does_not_include_previous_table(self):
        result = self.cli(paragraph("first") + table("previous") + paragraph("second"),
                          "--start", "2")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("[P2] second", result.stdout)
        self.assertNotIn("previous", result.stdout)

    def test_invalid_ranges_fail_clearly(self):
        for args in (("--start", "0"), ("--end", "-1"), ("--start", "2", "--end", "1")):
            with self.subTest(args=args):
                result = self.cli(paragraph("first"), *args)
                self.assertEqual(result.returncode, 2)
                self.assertNotIn("Traceback", result.stderr)

    def test_tab_separated_toc_entry_is_not_reported_as_heading(self):
        body = ('<w:p><w:pPr><w:pStyle w:val="Heading1"/></w:pPr>'
                '<w:r><w:t>Chapter 1</w:t><w:tab/><w:t>9</w:t></w:r></w:p>')
        result = self.cli(body + paragraph("Chapter 1"), "--outline")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("[P2]", result.stdout)
        self.assertNotIn("[P1]", result.stdout)


if __name__ == "__main__":
    unittest.main()
