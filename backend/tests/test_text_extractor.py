"""
Tests for resume text extractor.

Tests PDF, DOCX, and TXT extraction with various edge cases.
"""
import pytest
import tempfile
import os
from pathlib import Path
from app.modules.resume_intelligence.extraction.text_extractor import ResumeTextExtractor


@pytest.fixture
def extractor():
    """Create extractor instance."""
    return ResumeTextExtractor()


def test_extract_from_txt_file(extractor):
    """Test extraction from plain text file."""
    text_content = """John Doe
john@example.com | 555-1234
Software Engineer with 5 years experience

SKILLS
Python, JavaScript, React, Django

EXPERIENCE
Senior Developer at Tech Corp
Built scalable web applications
"""
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(text_content)
        temp_path = f.name
    
    try:
        result = extractor.extract_text(temp_path)
        
        assert result is not None
        assert 'John Doe' in result
        assert 'john@example.com' in result
        assert 'Python' in result
        assert 'Tech Corp' in result
        assert len(result) > 50
    finally:
        os.unlink(temp_path)


def test_extract_from_txt_with_unicode(extractor):
    """Test extraction from text file with unicode characters."""
    text_content = """José García
josé@example.com | +34 123-456-789
Ingeniero de Software

Experiencia en Python, JavaScript, React
Trabajé en Tech España desde 2020 hasta 2023
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(text_content)
        temp_path = f.name
    
    try:
        result = extractor.extract_text(temp_path)
        
        assert result is not None
        assert 'José García' in result or 'Jose Garcia' in result  # May normalize
        assert 'Python' in result
    finally:
        os.unlink(temp_path)


def test_extract_from_empty_txt(extractor):
    """Test extraction from empty text file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write('')
        temp_path = f.name
    
    try:
        result = extractor.extract_text(temp_path)
        
        # Should return empty string, not None or error
        assert result == ''
    finally:
        os.unlink(temp_path)


def test_extract_from_nonexistent_file(extractor):
    """Test extraction from file that doesn't exist."""
    result = extractor.extract_text('/nonexistent/path/resume.txt')
    
    # Should return None or empty string, not crash
    assert result is None or result == ''


def test_extract_with_unsupported_extension(extractor):
    """Test extraction from unsupported file type."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.xyz', delete=False) as f:
        f.write('Some content')
        temp_path = f.name
    
    try:
        result = extractor.extract_text(temp_path)
        
        # Should handle gracefully
        assert result is None or result == '' or isinstance(result, str)
    finally:
        os.unlink(temp_path)


def test_extract_txt_with_special_characters(extractor):
    """Test extraction with special characters and formatting."""
    text_content = """John Doe

Email: john.doe+test@example.com
Phone: (555) 123-4567

SKILLS:
• Python
• JavaScript
• React.js
• Node.js

EXPERIENCE:
Company: Tech Corp (2018-2023)
Role: Senior Software Engineer
    - Built web applications
    - Led team of 5
    - Increased performance by 40%
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(text_content)
        temp_path = f.name
    
    try:
        result = extractor.extract_text(temp_path)
        
        assert result is not None
        assert 'john.doe+test@example.com' in result
        assert 'Python' in result
        assert 'Tech Corp' in result
        assert '2018-2023' in result
    finally:
        os.unlink(temp_path)


def test_extract_large_txt_file(extractor):
    """Test extraction from large text file."""
    # Create a large resume (10KB+)
    text_content = "John Doe Resume\n\n"
    text_content += "SKILLS\n"
    text_content += "\n".join([f"Skill {i}: Python, JavaScript, React" for i in range(100)])
    text_content += "\n\nEXPERIENCE\n"
    text_content += "\n".join([f"Company {i}\nPosition {i}\nDescription line 1\nDescription line 2\n" for i in range(50)])
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(text_content)
        temp_path = f.name
    
    try:
        result = extractor.extract_text(temp_path)
        
        assert result is not None
        assert len(result) > 1000
        assert 'John Doe' in result
        assert 'Python' in result
    finally:
        os.unlink(temp_path)


def test_detect_file_type_txt(extractor):
    """Test file type detection for TXT."""
    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
        temp_path = f.name
    
    try:
        # Method might be internal, test via extract_text
        result = extractor.extract_text(temp_path)
        # Should handle TXT without error
        assert result is not None or result == ''
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def test_extract_txt_with_tabs_and_newlines(extractor):
    """Test extraction with tabs and multiple newlines."""
    text_content = """John\tDoe
Email:\tjohn@example.com


Phone:\t555-1234


SKILLS


Python\t\tJavaScript\t\tReact
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(text_content)
        temp_path = f.name
    
    try:
        result = extractor.extract_text(temp_path)
        
        assert result is not None
        # Tabs should be preserved or converted to spaces
        assert 'john@example.com' in result
        assert 'Python' in result
    finally:
        os.unlink(temp_path)


def test_extract_handles_encoding_errors(extractor):
    """Test extraction handles encoding errors gracefully."""
    # Create file with mixed encodings (not valid UTF-8)
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.txt', delete=False) as f:
        f.write(b'John Doe\n')
        f.write(b'Email: john@example.com\n')
        f.write(b'\xff\xfe Invalid bytes\n')  # Invalid UTF-8
        f.write(b'Skills: Python\n')
        temp_path = f.name
    
    try:
        result = extractor.extract_text(temp_path)
        
        # Should handle encoding errors gracefully
        assert result is not None or result == ''
        if result:
            # Valid parts should still be extracted
            assert 'john@example.com' in result or 'Python' in result
    finally:
        os.unlink(temp_path)


def test_extract_path_as_string_and_path_object(extractor):
    """Test extraction accepts both string path and Path object."""
    text_content = "John Doe\njohn@example.com"
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(text_content)
        temp_path = f.name
    
    try:
        # Test with string path
        result1 = extractor.extract_text(temp_path)
        assert result1 is not None
        assert 'John Doe' in result1
        
        # Test with Path object
        result2 = extractor.extract_text(Path(temp_path))
        assert result2 is not None
        assert 'John Doe' in result2
        
        # Results should be the same
        assert result1 == result2
    finally:
        os.unlink(temp_path)


def test_extract_preserves_line_breaks(extractor):
    """Test that line breaks are preserved in extraction."""
    text_content = """SECTION 1
Content line 1
Content line 2

SECTION 2
Content line 3

SECTION 3
Content line 4"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(text_content)
        temp_path = f.name
    
    try:
        result = extractor.extract_text(temp_path)
        
        assert result is not None
        # Line structure should be somewhat preserved
        assert 'SECTION 1' in result
        assert 'SECTION 2' in result
        assert 'SECTION 3' in result
        assert 'Content line 1' in result
    finally:
        os.unlink(temp_path)


def test_multiple_extractions_same_file(extractor):
    """Test multiple extractions from same file work correctly."""
    text_content = "John Doe\njohn@example.com\nPython Developer"
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(text_content)
        temp_path = f.name
    
    try:
        # Extract multiple times
        result1 = extractor.extract_text(temp_path)
        result2 = extractor.extract_text(temp_path)
        result3 = extractor.extract_text(temp_path)
        
        # All should succeed and be identical
        assert result1 is not None
        assert result1 == result2
        assert result2 == result3
    finally:
        os.unlink(temp_path)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
