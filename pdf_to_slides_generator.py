#!/usr/bin/env python3
"""
PDF to Slides Generator
A sample implementation demonstrating the research paper to slides generation prompt.
"""

import os
import sys
import argparse
import json
from typing import Dict, List, Tuple, Optional
import re
from dataclasses import dataclass
from pathlib import Path

try:
    import PyPDF2
    import pdfplumber
except ImportError:
    print("Required packages not installed. Please run:")
    print("pip install PyPDF2 pdfplumber")
    sys.exit(1)

@dataclass
class SlideContent:
    """Represents the content of a single slide."""
    number: int
    title: str
    content: List[str]
    visual_elements: List[str]
    speaker_notes: List[str]

@dataclass
class PaperSection:
    """Represents a section of the research paper."""
    title: str
    content: str
    page_numbers: List[int]

class PDFProcessor:
    """Handles PDF text extraction and preprocessing."""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.text_content = ""
        self.sections = []
        
    def extract_text(self) -> str:
        """Extract text from PDF using pdfplumber for better accuracy."""
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                text_parts = []
                for page_num, page in enumerate(pdf.pages, 1):
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(f"[PAGE {page_num}]\n{page_text}\n")
                
                self.text_content = "\n".join(text_parts)
                return self.text_content
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return ""
    
    def identify_sections(self) -> List[PaperSection]:
        """Identify major sections in the research paper."""
        if not self.text_content:
            self.extract_text()
        
        section_patterns = [
            (r'(?i)^(abstract|summary)\s*$', 'Abstract'),
            (r'(?i)^(introduction|1\.\s*introduction)\s*$', 'Introduction'),
            (r'(?i)^(literature\s+review|related\s+work|background|2\.\s*)', 'Literature Review'),
            (r'(?i)^(methodology|methods|approach|3\.\s*)', 'Methodology'),
            (r'(?i)^(results|findings|4\.\s*)', 'Results'),
            (r'(?i)^(discussion|analysis|5\.\s*)', 'Discussion'),
            (r'(?i)^(conclusion|conclusions|6\.\s*)', 'Conclusion'),
            (r'(?i)^(references|bibliography)', 'References'),
        ]
        
        sections = []
        lines = self.text_content.split('\n')
        current_section = None
        current_content = []
        current_pages = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            page_match = re.match(r'\[PAGE (\d+)\]', line)
            if page_match:
                current_pages.append(int(page_match.group(1)))
                continue
            
            section_found = False
            for pattern, section_name in section_patterns:
                if re.match(pattern, line):
                    if current_section:
                        sections.append(PaperSection(
                            title=current_section,
                            content='\n'.join(current_content),
                            page_numbers=current_pages.copy()
                        ))
                    
                    current_section = section_name
                    current_content = []
                    current_pages = []
                    section_found = True
                    break
            
            if not section_found and current_section:
                current_content.append(line)
        
        if current_section:
            sections.append(PaperSection(
                title=current_section,
                content='\n'.join(current_content),
                page_numbers=current_pages
            ))
        
        self.sections = sections
        return sections

class SlideGenerator:
    """Generates slides based on the extracted paper content."""
    
    def __init__(self, paper_sections: List[PaperSection], target_audience: str = "academic"):
        self.sections = paper_sections
        self.target_audience = target_audience
        self.slides = []
        
    def extract_paper_metadata(self) -> Dict[str, str]:
        """Extract title, authors, and other metadata from the paper."""
        metadata = {
            'title': 'Research Paper Presentation',
            'authors': 'Authors',
            'affiliation': 'Institution',
            'publication': 'Publication Venue'
        }
        
        for section in self.sections[:2]:
            content = section.content
            lines = content.split('\n')
            
            for line in lines[:10]:
                line = line.strip()
                if len(line) > 20 and not line.lower().startswith(('abstract', 'introduction')):
                    metadata['title'] = line
                    break
        
        return metadata
    
    def generate_title_slide(self, metadata: Dict[str, str]) -> SlideContent:
        """Generate the title slide."""
        return SlideContent(
            number=1,
            title="Title Slide",
            content=[
                metadata['title'],
                f"Authors: {metadata['authors']}",
                f"Affiliation: {metadata['affiliation']}",
                f"Publication: {metadata['publication']}"
            ],
            visual_elements=["Professional title slide layout"],
            speaker_notes=["Welcome audience", "Introduce the research topic"]
        )
    
    def extract_key_points(self, text: str, max_points: int = 6) -> List[str]:
        """Extract key points from a text section."""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        scored_sentences = []
        for sentence in sentences:
            score = 0
            if re.search(r'\d+%|\d+\.\d+', sentence):
                score += 2
            if re.search(r'(?i)(significant|important|key|main|primary|novel)', sentence):
                score += 1
            if re.search(r'(?i)(result|finding|conclusion|show|demonstrate)', sentence):
                score += 1
            scored_sentences.append((score, sentence))
        
        scored_sentences.sort(reverse=True, key=lambda x: x[0])
        return [sentence for _, sentence in scored_sentences[:max_points]]
    
    def generate_content_slides(self) -> List[SlideContent]:
        """Generate content slides based on paper sections."""
        slides = []
        slide_number = 2
        
        for section in self.sections:
            if section.title.lower() == 'references':
                continue
                
            if section.title.lower() == 'abstract':
                slides.append(self.generate_abstract_slide(section, slide_number))
            elif 'introduction' in section.title.lower():
                slides.append(self.generate_introduction_slide(section, slide_number))
            elif 'methodology' in section.title.lower() or 'method' in section.title.lower():
                slides.append(self.generate_methodology_slide(section, slide_number))
            elif 'result' in section.title.lower():
                slides.append(self.generate_results_slide(section, slide_number))
            elif 'discussion' in section.title.lower():
                slides.append(self.generate_discussion_slide(section, slide_number))
            elif 'conclusion' in section.title.lower():
                slides.append(self.generate_conclusion_slide(section, slide_number))
            else:
                slides.append(self.generate_generic_slide(section, slide_number))
            
            slide_number += 1
        
        return slides
    
    def generate_abstract_slide(self, section: PaperSection, slide_num: int) -> SlideContent:
        """Generate slide for abstract section."""
        key_points = self.extract_key_points(section.content, 4)
        return SlideContent(
            number=slide_num,
            title="Research Overview",
            content=key_points,
            visual_elements=["Research framework diagram"],
            speaker_notes=["Provide context for the research", "Highlight main contributions"]
        )
    
    def generate_introduction_slide(self, section: PaperSection, slide_num: int) -> SlideContent:
        """Generate slide for introduction section."""
        key_points = self.extract_key_points(section.content, 5)
        return SlideContent(
            number=slide_num,
            title="Research Context & Motivation",
            content=key_points,
            visual_elements=["Problem illustration", "Research gap visualization"],
            speaker_notes=["Explain the problem significance", "Connect to audience interests"]
        )
    
    def generate_methodology_slide(self, section: PaperSection, slide_num: int) -> SlideContent:
        """Generate slide for methodology section."""
        key_points = self.extract_key_points(section.content, 6)
        return SlideContent(
            number=slide_num,
            title="Methodology & Approach",
            content=key_points,
            visual_elements=["Methodology flowchart", "Data collection process"],
            speaker_notes=["Explain research design choices", "Justify methodology selection"]
        )
    
    def generate_results_slide(self, section: PaperSection, slide_num: int) -> SlideContent:
        """Generate slide for results section."""
        key_points = self.extract_key_points(section.content, 6)
        return SlideContent(
            number=slide_num,
            title="Key Findings & Results",
            content=key_points,
            visual_elements=["Charts and graphs", "Statistical visualizations"],
            speaker_notes=["Highlight significant findings", "Explain statistical significance"]
        )
    
    def generate_discussion_slide(self, section: PaperSection, slide_num: int) -> SlideContent:
        """Generate slide for discussion section."""
        key_points = self.extract_key_points(section.content, 5)
        return SlideContent(
            number=slide_num,
            title="Discussion & Implications",
            content=key_points,
            visual_elements=["Implications diagram", "Future work roadmap"],
            speaker_notes=["Interpret results", "Discuss broader implications"]
        )
    
    def generate_conclusion_slide(self, section: PaperSection, slide_num: int) -> SlideContent:
        """Generate slide for conclusion section."""
        key_points = self.extract_key_points(section.content, 4)
        return SlideContent(
            number=slide_num,
            title="Conclusions & Future Work",
            content=key_points,
            visual_elements=["Summary infographic", "Future directions"],
            speaker_notes=["Summarize main contributions", "Suggest next steps"]
        )
    
    def generate_generic_slide(self, section: PaperSection, slide_num: int) -> SlideContent:
        """Generate slide for other sections."""
        key_points = self.extract_key_points(section.content, 5)
        return SlideContent(
            number=slide_num,
            title=section.title,
            content=key_points,
            visual_elements=["Relevant diagrams or charts"],
            speaker_notes=[f"Explain {section.title.lower()} content"]
        )
    
    def generate_slides(self) -> List[SlideContent]:
        """Generate all slides for the presentation."""
        metadata = self.extract_paper_metadata()
        
        slides = [self.generate_title_slide(metadata)]
        
        slides.extend(self.generate_content_slides())
        
        slides.append(SlideContent(
            number=len(slides) + 1,
            title="Questions & Discussion",
            content=[
                "Thank you for your attention!",
                "Questions and Discussion",
                "Contact: [Author Email]",
                "Full paper available at: [Publication Link]"
            ],
            visual_elements=["Contact information", "QR code for paper access"],
            speaker_notes=["Open floor for questions", "Provide contact details"]
        ))
        
        self.slides = slides
        return slides

class SlideFormatter:
    """Formats slides for different output formats."""
    
    @staticmethod
    def format_as_markdown(slides: List[SlideContent]) -> str:
        """Format slides as markdown."""
        markdown_content = []
        
        for slide in slides:
            markdown_content.append(f"# SLIDE {slide.number}: {slide.title}\n")
            
            markdown_content.append("## Content:")
            for point in slide.content:
                markdown_content.append(f"- {point}")
            
            markdown_content.append("\n## Visual Elements:")
            for element in slide.visual_elements:
                markdown_content.append(f"- {element}")
            
            markdown_content.append("\n## Speaker Notes:")
            for note in slide.speaker_notes:
                markdown_content.append(f"- {note}")
            
            markdown_content.append("\n---\n")
        
        return "\n".join(markdown_content)
    
    @staticmethod
    def format_as_json(slides: List[SlideContent]) -> str:
        """Format slides as JSON."""
        slides_data = []
        for slide in slides:
            slides_data.append({
                "number": slide.number,
                "title": slide.title,
                "content": slide.content,
                "visual_elements": slide.visual_elements,
                "speaker_notes": slide.speaker_notes
            })
        
        return json.dumps(slides_data, indent=2)

def main():
    """Main function to run the PDF to slides generator."""
    parser = argparse.ArgumentParser(description="Generate presentation slides from research paper PDF")
    parser.add_argument("pdf_path", help="Path to the research paper PDF")
    parser.add_argument("--output", "-o", default="slides.md", help="Output file path")
    parser.add_argument("--format", "-f", choices=["markdown", "json"], default="markdown", help="Output format")
    parser.add_argument("--audience", "-a", choices=["academic", "general", "educational"], default="academic", help="Target audience")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.pdf_path):
        print(f"Error: PDF file '{args.pdf_path}' not found.")
        sys.exit(1)
    
    print(f"Processing PDF: {args.pdf_path}")
    
    processor = PDFProcessor(args.pdf_path)
    sections = processor.identify_sections()
    
    if not sections:
        print("Warning: No sections identified in the PDF. Using raw text.")
        sections = [PaperSection("Content", processor.text_content, [1])]
    
    print(f"Identified {len(sections)} sections:")
    for section in sections:
        print(f"  - {section.title}")
    
    generator = SlideGenerator(sections, args.audience)
    slides = generator.generate_slides()
    
    print(f"Generated {len(slides)} slides")
    
    if args.format == "markdown":
        output_content = SlideFormatter.format_as_markdown(slides)
    else:
        output_content = SlideFormatter.format_as_json(slides)
    
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(output_content)
    
    print(f"Slides saved to: {args.output}")
    print("\nSlide Overview:")
    for slide in slides:
        print(f"  Slide {slide.number}: {slide.title}")

if __name__ == "__main__":
    main()
