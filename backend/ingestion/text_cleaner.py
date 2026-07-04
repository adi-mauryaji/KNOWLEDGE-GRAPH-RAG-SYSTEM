import re
from dataclasses import dataclass

@dataclass
class CleaningConfig:
    remove_headers: bool = True
    remove_footers: bool = True
    normalize_whitespace: bool = True
    min_line_length: int = 20

class TextCleaner:
    def __init__(self, config: CleaningConfig = None):
        self.config = config or CleaningConfig()

    def clean(self, text: str) -> str:
        if self.config.normalize_whitespace:
            text = self._normalize_whitespace(text)
        if self.config.remove_headers:
            text = self._remove_headers_footers(text)
        text = self._remove_artifacts(text)
        return text.strip()
    
    def _normalize_whitespace(self, text: str) -> str:
        text = re.sub(r' {2,}', ' ', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text
    
    def _remove_headers_footers(self, text: str) -> str:
        lines = text.split('\n')
        cleaned = []
        for line in lines:
            stripped = line.strip()
            if len(stripped) < self.config.min_line_length:
                if not re.match(r'^[\d\s\-–—|/\\]+$', stripped):
                    cleaned.append(line)
            else:
                cleaned.append(line)
        return '\n'.join(cleaned)
    
    def _remove_artifacts(self, text: str) -> str:
        text = re.sub(r'Page\s+\d+\s+of\s+\d+', '', text, flags=re.IGNORECASE)
        text = re.sub(r'^\s*[-–—]+\s*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'[_\-=]{5,}', '', text)
        return text
    

