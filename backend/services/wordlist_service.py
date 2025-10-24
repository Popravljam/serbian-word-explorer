import os
from typing import Set

class WordlistService:
    """Service for word existence validation using spisak-srpskih-reci."""
    
    # Latin to Cyrillic conversion map
    LATIN_TO_CYRILLIC = {
        'a': 'а', 'b': 'б', 'c': 'ц', 'č': 'ч', 'ć': 'ћ',
        'd': 'д', 'dž': 'џ', 'đ': 'ђ', 'e': 'е', 'f': 'ф',
        'g': 'г', 'h': 'х', 'i': 'и', 'j': 'ј', 'k': 'к',
        'l': 'л', 'lj': 'љ', 'm': 'м', 'n': 'н', 'nj': 'њ',
        'o': 'о', 'p': 'п', 'r': 'р', 's': 'с', 'š': 'ш',
        't': 'т', 'u': 'у', 'v': 'в', 'z': 'з', 'ž': 'ж',
        'A': 'А', 'B': 'Б', 'C': 'Ц', 'Č': 'Ч', 'Ć': 'Ћ',
        'D': 'Д', 'Dž': 'Џ', 'Đ': 'Ђ', 'E': 'Е', 'F': 'Ф',
        'G': 'Г', 'H': 'Х', 'I': 'И', 'J': 'Ј', 'K': 'К',
        'L': 'Л', 'Lj': 'Љ', 'M': 'М', 'N': 'Н', 'Nj': 'Њ',
        'O': 'О', 'P': 'П', 'R': 'Р', 'S': 'С', 'Š': 'Ш',
        'T': 'Т', 'U': 'У', 'V': 'В', 'Z': 'З', 'Ž': 'Ж'
    }
    
    def __init__(self):
        self.word_set: Set[str] = set()
        self._load_wordlist()
    
    def _latin_to_cyrillic(self, text: str) -> str:
        """Convert Latin Serbian to Cyrillic."""
        result = []
        i = 0
        while i < len(text):
            # Try digraphs first
            if i + 1 < len(text):
                digraph = text[i:i+2]
                if digraph in self.LATIN_TO_CYRILLIC:
                    result.append(self.LATIN_TO_CYRILLIC[digraph])
                    i += 2
                    continue
            
            # Single character
            char = text[i]
            result.append(self.LATIN_TO_CYRILLIC.get(char, char))
            i += 1
        
        return ''.join(result)
    
    def _load_wordlist(self):
        """Load the Serbian word list into memory."""
        # Check production path first
        if os.path.exists('/opt/recnik/spisak-srpskih-reci/serbian-words.txt'):
            wordlist_file = '/opt/recnik/spisak-srpskih-reci/serbian-words.txt'
        else:
            # Development path
            wordlist_file = os.path.join(
                os.path.dirname(__file__),
                '../../../spisak-srpskih-reci/serbian-words.txt'
            )
        
        if not os.path.exists(wordlist_file):
            print(f"Warning: Word list file not found at {wordlist_file}")
            return
        
        try:
            with open(wordlist_file, 'r', encoding='utf-8') as f:
                for line in f:
                    word = line.strip()
                    if word:
                        self.word_set.add(word)
            
            print(f"Loaded {len(self.word_set)} words into wordlist")
            
        except Exception as e:
            print(f"Error loading wordlist: {e}")
    
    def word_exists(self, word: str) -> bool:
        """Check if a word exists in the wordlist."""
        # Try both Latin and Cyrillic
        if word in self.word_set:
            return True
        cyrillic = self._latin_to_cyrillic(word)
        return cyrillic in self.word_set
    
    def get_word_count(self) -> int:
        """Get total number of words in the list."""
        return len(self.word_set)
    
    def find_related_forms(self, word: str, limit: int = 20) -> list:
        """Find all word forms that start with the given word (inflected forms)."""
        word_lower = word.lower()
        cyrillic_lower = self._latin_to_cyrillic(word_lower)
        related = []
        
        # Find exact match and forms that start with the word (try both Latin and Cyrillic)
        for w in self.word_set:
            w_lower = w.lower()
            if w_lower == word_lower or w_lower == cyrillic_lower or \
               w_lower.startswith(word_lower) or w_lower.startswith(cyrillic_lower):
                related.append(w)
                if len(related) >= limit:
                    break
        
        return sorted(related)
    
    def find_possible_lemmas(self, word: str, max_results: int = 10) -> list:
        """Find possible lemmas (base forms) for an inflected word.
        
        Strategy: Look for words that start with the first few letters of the input.
        Common pattern: inflected forms share root with their lemma.
        """
        if not word or len(word) < 3:
            return []
        
        word_lower = word.lower()
        cyrillic_lower = self._latin_to_cyrillic(word_lower)
        candidates = set()
        
        # If word exists as-is, it might already be a lemma (try both scripts)
        if word_lower in self.word_set:
            candidates.add(word_lower)
        if cyrillic_lower in self.word_set:
            candidates.add(cyrillic_lower)
        
        # Try different root lengths to find lemmas
        for root_length in range(min(len(word_lower) - 1, 6), 2, -1):
            root_latin = word_lower[:root_length]
            root_cyrillic = self._latin_to_cyrillic(root_latin)
            
            for w in self.word_set:
                w_lower = w.lower()
                # Look for words starting with same root (either script)
                if w_lower.startswith(root_latin) or w_lower.startswith(root_cyrillic):
                    candidates.add(w_lower)
                    if len(candidates) >= max_results * 3:  # Get more candidates
                        break
            
            if len(candidates) >= max_results:
                break
        
        # Sort by length (shorter words more likely to be lemmas)
        return sorted(list(candidates), key=len)[:max_results]


# Singleton
_wordlist_service = None

def get_wordlist_service() -> WordlistService:
    global _wordlist_service
    if _wordlist_service is None:
        _wordlist_service = WordlistService()
    return _wordlist_service
