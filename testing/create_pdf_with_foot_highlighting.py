"""
Create PDF in the style of digbib with foot highlighting.
Every second, fourth and sixth foot of a verse is grey.
"""

import csv
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT


def register_fonts():
    """Register fonts for PDF generation."""
    # Try to register Arial if available, otherwise use Helvetica (built-in sans-serif)
    try:
        # Try to register Arial from Windows fonts
        arial_path = "C:/Windows/Fonts/arial.ttf"
        if Path(arial_path).exists():
            pdfmetrics.registerFont(TTFont('Arial', arial_path))
            return 'Arial'
    except:
        pass
    # Fallback to Helvetica (built-in sans-serif)
    return 'Helvetica'


def get_german_ordinal(n: int) -> str:
    """
    Convert a number to German ordinal.
    
    Args:
        n: Integer number
        
    Returns:
        German ordinal string (e.g., 1 -> "erster", 13 -> "dreizehnter")
    """
    # German ordinals for numbers 1-24 (Iliad has 24 books)
    ordinals = {
        1: "erster", 2: "zweiter", 3: "dritter", 4: "vierter",
        5: "fünfter", 6: "sechster", 7: "siebter", 8: "achter",
        9: "neunter", 10: "zehnter", 11: "elfter", 12: "zwölfter",
        13: "dreizehnter", 14: "vierzehnter", 15: "fünfzehnter", 16: "sechzehnter",
        17: "siebzehnter", 18: "achtzehnter", 19: "neunzehnter", 20: "zwanzigster",
        21: "einundzwanzigster", 22: "zweiundzwanzigster", 23: "dreiundzwanzigster", 24: "vierundzwanzigster"
    }
    return ordinals.get(n, str(n))


def parse_feet_from_pattern(pattern: str) -> list[tuple[int, int]]:
    """
    Parse hexameter pattern and return start/end indices for each foot.
    
    Args:
        pattern: Pattern string like "TSSTLTSSTLTSSTL"
        
    Returns:
        List of (start, end) tuples for each foot (0-indexed, inclusive start, exclusive end)
    """
    
    feet_starts = [i for i, char in enumerate(pattern) if char == 'T']
    feet_starts.append(len(pattern))  # Add end of pattern as last boundary
    feet = list(zip(feet_starts[:-1], feet_starts[1:]))
    
    return feet


def get_foot_indices_to_highlight(feet: list[tuple[int, int]]) -> set[int]:
    """
    Get syllable indices that should be highlighted (feet 2, 4, 6).
    
    Args:
        feet: List of (start, end) tuples for each foot
        
    Returns:
        Set of syllable indices to highlight (0-indexed)
    """
    highlight_indices = set()
    
    # Feet are 0-indexed, so foot 1 is index 0, foot 2 is index 1, etc.
    # We want feet 2, 4, 6 which are indices 1, 3, 5
    for foot_idx in [1, 3, 5]:
        if foot_idx < len(feet):
            start, end = feet[foot_idx]
            highlight_indices.update(range(start, end))
    
    return highlight_indices


def create_highlighted_text(original_text: str, verse_syllabified: str, highlight_indices: set[int]) -> str:
    """
    Create HTML-like text with highlighting for specified syllables.
    Maps original_text characters to scansion_display syllables for coloring.
    
    Args:
        original_text: Original verse text with punctuation and capitalization
        verse_syllabified: Syllabified verse text with | separators
        highlight_indices: Set of syllable indices to highlight
        
    Returns:
        String with HTML-like markup for highlighting
    """
    # Build a flat string from syllables (removing | separators)
    verse_flat = ''.join(verse_syllabified.split('|')).lower()
    
    # Map each character position in original_text to a syllable index
    char_to_syllable = []
    syl_pos = 0
    
    for orig_char in original_text:
        if orig_char.isalpha():
            # Find matching character in verse_flat
            orig_char_lower = orig_char.lower()
            
            while syl_pos < len(verse_flat) and verse_flat[syl_pos].lower() != orig_char_lower:
                syl_pos += 1
            
            if syl_pos < len(verse_flat):
                # Find which syllable this position belongs to
                char_count = 0
                syllable_idx = 0
                for i, syl in enumerate(verse_syllabified.split('|')):
                    if char_count <= syl_pos < char_count + len(syl):
                        syllable_idx = i
                        break
                    char_count += len(syl)
                
                char_to_syllable.append(syllable_idx)
                syl_pos += 1
            else:
                # No match, use last known syllable index
                char_to_syllable.append(char_to_syllable[-1] if char_to_syllable else 0)
        else:
            # Non-letter character, will use last letter's color
            char_to_syllable.append(None)
    
    # Build highlighted text character by character
    result = []
    last_color = None
    
    for i, (orig_char, syl_idx) in enumerate(zip(original_text, char_to_syllable)):
        if orig_char.isalpha() and syl_idx is not None:
            # Determine if this syllable should be highlighted
            if syl_idx in highlight_indices:
                current_color = "#808080"
            else:
                current_color = "black"
            
            # If color changed, close previous font tag and open new one
            if last_color != current_color:
                if last_color is not None:
                    result.append('</font>')
                result.append(f'<font color="{current_color}">')
                last_color = current_color
            
            result.append(orig_char)
        else:
            # Non-letter character, use last color
            result.append(orig_char)
    
    # Close final font tag if open
    if last_color is not None:
        result.append('</font>')
    
    return ''.join(result)


def create_pdf(input_csv: str, output_pdf: str):
    """
    Create PDF from CSV with foot highlighting.
    
    Args:
        input_csv: Path to verses_with_patterns.csv
        output_pdf: Path to output PDF file
    """
    # Register fonts
    font_name = register_fonts()
    print(f"Using font: {font_name}")
    
    # Load verses
    print(f"Loading verses from {input_csv}...")
    verses = []
    with open(input_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            verses.append(row)
    
    print(f"Loaded {len(verses)} verses")
    
    # Create PDF
    print(f"Creating PDF: {output_pdf}...")
    
    # Page number callback
    def add_page_number(canvas, doc):
        """Add page number to top right of each page."""
        canvas.saveState()
        canvas.setFont(font_name, 9)
        canvas.drawRightString(A4[0] - 2*cm, A4[1] - 1*cm, str(doc.page))
        canvas.restoreState()
    
    doc = SimpleDocTemplate(
        output_pdf,
        pagesize=A4,
        leftMargin=2.77*cm,
        rightMargin=2*cm,
        topMargin=1.5*cm,
        bottomMargin=2*cm,
        title="Ilias skandiert",
    )
    
    # Create styles
    styles = getSampleStyleSheet()
    
    # Custom style for verses - close spacing
    verse_style = ParagraphStyle(
        'Verse',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=12,
        leading=14,  # Reduced further for closer spacing
        spaceAfter=0,  # No space after for closer spacing
        alignment=TA_LEFT,
    )
    
    # Style for line numbers (every 5th verse) - same size as text
    line_number_style = ParagraphStyle(
        'LineNumber',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=12,  # Same size as verse text
        leading=14,
        spaceAfter=0,
        alignment=TA_LEFT,
    )
    
    # Style for book headers
    book_style = ParagraphStyle(
        'Book',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=14,
        leading=18,
        spaceAfter=8,
        spaceBefore=12,
        alignment=TA_LEFT,
    )
    
    # Build story
    story = []
    current_book = None
    verse_count_in_book = 0
    first_book = True
    
    for verse in verses:
        book_number = verse.get('book_number', '')
        original_text = verse.get('original_text', '')
        pattern = verse.get('assigned_pattern', '')
        verse_syllabified = verse.get('verse_syllabified', '')
        
        # Add book header if book changed
        if book_number != current_book:
            current_book = book_number
            verse_count_in_book = 0  # Reset verse count for new book
            
            # Add page break before new book (except first book)
            if not first_book and book_number:
                story.append(PageBreak())
            first_book = False
            
            if book_number:
                # Convert to German ordinal
                book_num_int = int(book_number)
                german_ordinal = get_german_ordinal(book_num_int)
                story.append(Paragraph(f"{german_ordinal.capitalize()} Gesang", book_style))
        
        verse_count_in_book += 1
        
        # Add line number every 5 verses on a separate line
        if verse_count_in_book % 5 == 0:
            story.append(Paragraph(str(verse_count_in_book), line_number_style))
        
        # Parse pattern to get feet
        if pattern and verse_syllabified:
            feet = parse_feet_from_pattern(pattern)
            highlight_indices = get_foot_indices_to_highlight(feet)
            
            # Create highlighted text using original_text
            highlighted_text = create_highlighted_text(original_text, verse_syllabified, highlight_indices)
            
            # Add highlighted verse (no line number on this line)
            story.append(Paragraph(highlighted_text, verse_style))
        else:
            # No pattern, just show original text
            story.append(Paragraph(original_text, verse_style))
    
    # Build PDF with page number callback
    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    print(f"PDF created successfully: {output_pdf}")


def main():
    """Main execution function."""
    root = Path(__file__).resolve().parent
    input_csv = root / "../scansion/digbib_ilias_verses_with_scansion.csv"
    output_pdf = root / "Ilias_Hexameter_Highlighted.pdf"
    
    create_pdf(str(input_csv), str(output_pdf))


if __name__ == "__main__":
    main()
