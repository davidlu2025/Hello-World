# PDF to Slides Generator

A comprehensive tool for generating presentation slides from research paper PDFs, implementing the research paper to slides generation prompt framework.

## Overview

This tool demonstrates how to use the PDF to slides generation prompt by providing a complete implementation that:

1. **Extracts text** from research paper PDFs
2. **Identifies paper sections** (Abstract, Introduction, Methodology, Results, etc.)
3. **Generates structured slides** following academic presentation best practices
4. **Formats output** in multiple formats (Markdown, JSON)
5. **Adapts content** for different target audiences

## Features

- **Intelligent Section Detection**: Automatically identifies common academic paper sections
- **Content Extraction**: Extracts key points using heuristic scoring
- **Multiple Output Formats**: Supports Markdown and JSON output
- **Audience Adaptation**: Adjusts content complexity for academic, general, or educational audiences
- **Comprehensive Slide Structure**: Includes title, content, visual elements, and speaker notes
- **Extensible Framework**: Easy to customize for specific research domains

## Installation

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

2. Make the script executable:
```bash
chmod +x pdf_to_slides_generator.py
```

## Usage

### Basic Usage

```bash
python pdf_to_slides_generator.py research_paper.pdf
```

This will generate `slides.md` with presentation slides in Markdown format.

### Advanced Usage

```bash
# Generate JSON format for academic audience
python pdf_to_slides_generator.py paper.pdf --format json --audience academic --output presentation.json

# Generate slides for general audience
python pdf_to_slides_generator.py paper.pdf --audience general --output general_slides.md

# Generate educational slides
python pdf_to_slides_generator.py paper.pdf --audience educational --output lecture_slides.md
```

### Command Line Options

- `pdf_path`: Path to the research paper PDF (required)
- `--output, -o`: Output file path (default: slides.md)
- `--format, -f`: Output format - markdown or json (default: markdown)
- `--audience, -a`: Target audience - academic, general, or educational (default: academic)

## Output Structure

The generated slides follow this structure:

### Markdown Format
```markdown
# SLIDE 1: Title Slide

## Content:
- Research Paper Title
- Authors: Author Names
- Affiliation: Institution
- Publication: Venue

## Visual Elements:
- Professional title slide layout

## Speaker Notes:
- Welcome audience
- Introduce the research topic

---
```

### JSON Format
```json
[
  {
    "number": 1,
    "title": "Title Slide",
    "content": ["Research Paper Title", "Authors: Author Names"],
    "visual_elements": ["Professional title slide layout"],
    "speaker_notes": ["Welcome audience", "Introduce the research topic"]
  }
]
```

## Slide Types Generated

1. **Title Slide**: Paper title, authors, affiliation, publication
2. **Research Overview**: Abstract and key contributions
3. **Research Context & Motivation**: Problem statement and research gap
4. **Literature Review**: Related work and background (if present)
5. **Methodology & Approach**: Research methods and experimental design
6. **Key Findings & Results**: Main results and statistical findings
7. **Discussion & Implications**: Interpretation and broader impact
8. **Conclusions & Future Work**: Summary and next steps
9. **Questions & Discussion**: Contact information and Q&A

## Customization

### Adding New Section Types

To add support for new paper sections, modify the `section_patterns` in `PDFProcessor.identify_sections()`:

```python
section_patterns = [
    (r'(?i)^(your_section_pattern)\s*$', 'Your Section Name'),
    # ... existing patterns
]
```

### Customizing Content Extraction

Modify the `extract_key_points()` method in `SlideGenerator` to adjust how key points are identified and scored.

### Adding New Output Formats

Extend the `SlideFormatter` class to support additional output formats:

```python
@staticmethod
def format_as_powerpoint(slides: List[SlideContent]) -> str:
    # Implementation for PowerPoint format
    pass
```

## Example Workflow

1. **Input**: Research paper PDF
2. **Processing**: 
   - Extract text using pdfplumber
   - Identify sections using regex patterns
   - Extract key points using heuristic scoring
   - Generate slides following academic presentation structure
3. **Output**: Structured slides with content, visual elements, and speaker notes

## Prompt Framework Integration

This implementation demonstrates the practical application of the comprehensive prompt framework defined in `pdf_to_slides_prompt.md`. The prompt provides:

- **Analysis Framework**: How to structure paper analysis
- **Content Extraction Guidelines**: What information to extract from each section
- **Slide Generation Framework**: Template for slide structure
- **Formatting Guidelines**: How to present content effectively
- **Quality Assurance**: Checklist for ensuring output quality

## Limitations and Future Improvements

### Current Limitations
- Section detection relies on common academic patterns
- Key point extraction uses simple heuristics
- No actual visual element generation (only descriptions)
- Limited support for complex mathematical notation

### Potential Improvements
- Machine learning-based section detection
- Advanced NLP for better content summarization
- Integration with presentation software APIs
- Support for figure and table extraction
- Multi-language support

## Contributing

To contribute to this project:

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For questions or issues:
- Check the documentation in `pdf_to_slides_prompt.md`
- Review the example outputs
- Submit issues for bugs or feature requests

---

This tool demonstrates how a well-structured prompt can be implemented as a practical solution for automating the creation of academic presentations from research papers.
