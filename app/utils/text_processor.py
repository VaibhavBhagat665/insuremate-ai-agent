import re
from typing import List, Dict, Optional
from app.core.config import settings

class TextProcessor:
    """Advanced text processing and chunking with multiple strategies"""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)\[\]\{\}\/\\\@\#\$\%\&\*\+\=\'\"\`\~]', '', text)
        
        # Normalize quotes
        text = text.replace('\u201c', '"').replace('\u201d', '"')
        text = text.replace('\u2018', "'").replace('\u2019', "'")
        
        return text.strip()
    
    @staticmethod
    def smart_chunk(text: str) -> List[Dict]:
        """Intelligent text chunking with semantic boundaries"""
        
        # Clean text first
        text = TextProcessor.clean_text(text)
        
        # Split by sentences first
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        chunks = []
        current_chunk = []
        current_length = 0
        
        for i, sentence in enumerate(sentences):
            words = sentence.split()
            sentence_length = len(words)
            
            # Check if adding sentence exceeds chunk size
            if current_length + sentence_length > settings.chunk_size and current_chunk:
                # Create chunk
                chunk_text = ' '.join(current_chunk)
                chunks.append({
                    'text': chunk_text,
                    'chunk_id': f"chunk_{len(chunks)}",
                    'word_count': current_length,
                    'sentence_start': i - len(current_chunk),
                    'sentence_end': i - 1
                })
                
                # Start new chunk with overlap
                overlap_sentences = current_chunk[-2:] if len(current_chunk) >= 2 else current_chunk
                current_chunk = overlap_sentences + [sentence]
                current_length = sum(len(s.split()) for s in current_chunk)
            else:
                current_chunk.append(sentence)
                current_length += sentence_length
        
        # Add final chunk
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            chunks.append({
                'text': chunk_text,
                'chunk_id': f"chunk_{len(chunks)}",
                'word_count': current_length,
                'sentence_start': len(sentences) - len(current_chunk),
                'sentence_end': len(sentences) - 1
            })
        
        return chunks

    @staticmethod
    def smart_chunk_enhanced(text: str, metadata: Optional[Dict] = None) -> List[Dict]:
        """
        Enhanced smart chunking that respects document structure.
        This method is called by DocumentProcessor._process_text_parallel.
        
        Uses section headers, paragraph boundaries, and semantic cues
        for more intelligent chunk boundaries.
        """
        if not text or not text.strip():
            return []
        
        # Clean text
        cleaned_text = TextProcessor.clean_text(text)
        
        # Try to detect section boundaries
        section_pattern = re.compile(
            r'\n\s*(?:#{1,4}\s+|(?:Section|Chapter|Part|Article)\s+\d+|'
            r'(?:\d+\.)+\s+[A-Z]|--- Page \d+ ---)',
            re.IGNORECASE
        )
        
        # Split into sections first, then chunk within sections
        sections = section_pattern.split(cleaned_text)
        section_headers = section_pattern.findall(cleaned_text)
        
        chunks = []
        chunk_size = settings.chunk_size
        chunk_overlap = settings.chunk_overlap
        
        for sec_idx, section in enumerate(sections):
            if not section.strip():
                continue
            
            # Prepend header if available
            header = ""
            if sec_idx > 0 and sec_idx - 1 < len(section_headers):
                header = section_headers[sec_idx - 1].strip() + " "
            
            # Split section into sentences
            sentences = re.split(r'(?<=[.!?])\s+', section.strip())
            
            current_chunk_parts = []
            current_word_count = 0
            
            for sent_idx, sentence in enumerate(sentences):
                sentence = sentence.strip()
                if not sentence:
                    continue
                    
                word_count = len(sentence.split())
                
                if current_word_count + word_count > chunk_size and current_chunk_parts:
                    # Emit current chunk
                    chunk_text = header + ' '.join(current_chunk_parts)
                    chunks.append({
                        'text': chunk_text.strip(),
                        'chunk_id': f"chunk_{len(chunks)}",
                        'word_count': len(chunk_text.split()),
                        'section_index': sec_idx,
                        'chunk_type': 'section_aware'
                    })
                    
                    # Overlap: carry last N words worth of sentences
                    overlap_parts = []
                    overlap_count = 0
                    for prev_sent in reversed(current_chunk_parts):
                        prev_words = len(prev_sent.split())
                        if overlap_count + prev_words <= chunk_overlap:
                            overlap_parts.insert(0, prev_sent)
                            overlap_count += prev_words
                        else:
                            break
                    
                    current_chunk_parts = overlap_parts + [sentence]
                    current_word_count = sum(len(s.split()) for s in current_chunk_parts)
                else:
                    current_chunk_parts.append(sentence)
                    current_word_count += word_count
            
            # Emit remaining content
            if current_chunk_parts:
                chunk_text = header + ' '.join(current_chunk_parts)
                chunks.append({
                    'text': chunk_text.strip(),
                    'chunk_id': f"chunk_{len(chunks)}",
                    'word_count': len(chunk_text.split()),
                    'section_index': sec_idx,
                    'chunk_type': 'section_aware'
                })
        
        # Fallback: if no chunks were created, do basic chunking
        if not chunks:
            return TextProcessor.smart_chunk(text)
        
        return chunks

    @staticmethod
    def chunk_text(text: str, metadata: Optional[Dict] = None) -> List[Dict]:
        """
        Wrapper for backward compatibility.
        Called by DocumentProcessor when smart_chunk_enhanced is not found.
        """
        return TextProcessor.smart_chunk_enhanced(text, metadata)
