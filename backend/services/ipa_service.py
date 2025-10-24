"""
Service for converting Serbian Cyrillic text with accent marks to IPA notation.
"""

class IPAService:
    """Convert Serbian text with accents to IPA phonetic notation."""
    
    # Cyrillic to IPA mapping
    CYRILLIC_TO_IPA = {
        'а': 'a', 'б': 'b', 'в': 'ʋ', 'г': 'ɡ', 'д': 'd',
        'ђ': 'dʑ', 'е': 'e', 'ж': 'ʒ', 'з': 'z', 'и': 'i',
        'ј': 'j', 'к': 'k', 'л': 'l', 'љ': 'ʎ', 'м': 'm',
        'н': 'n', 'њ': 'ɲ', 'о': 'o', 'п': 'p', 'р': 'r',
        'с': 's', 'т': 't', 'ћ': 'tɕ', 'у': 'u', 'ф': 'f',
        'х': 'x', 'ц': 'ts', 'ч': 'tʃ', 'џ': 'dʒ', 'ш': 'ʃ'
    }
    
    # Latin Serbian to IPA mapping
    LATIN_TO_IPA = {
        'a': 'a', 'b': 'b', 'c': 'ts', 'č': 'tʃ', 'ć': 'tɕ',
        'd': 'd', 'dž': 'dʒ', 'đ': 'dʑ', 'e': 'e', 'f': 'f',
        'g': 'ɡ', 'h': 'x', 'i': 'i', 'j': 'j', 'k': 'k',
        'l': 'l', 'lj': 'ʎ', 'm': 'm', 'n': 'n', 'nj': 'ɲ',
        'o': 'o', 'p': 'p', 'r': 'r', 's': 's', 'š': 'ʃ',
        't': 't', 'u': 'u', 'v': 'ʋ', 'z': 'z', 'ž': 'ʒ'
    }
    
    # Accent marks to IPA stress/tone
    ACCENT_TO_IPA = {
        '\u0300': '',           # Grave (short rising) - unmarked
        '\u0301': 'ː',          # Acute (long) - length marker
        '\u030f': 'ˆː',         # Double grave (long falling) - falling + length
        '\u0311': 'ˆ',          # Inverted breve (short falling) - falling
        '\u0304': 'ː',          # Macron (long)
    }
    
    def to_ipa(self, text: str) -> str:
        """
        Convert Serbian text with accent marks to IPA.
        
        Args:
            text: Serbian text (Cyrillic or Latin) with accent marks
            
        Returns:
            IPA transcription
        """
        if not text:
            return ""
        
        result = []
        text_lower = text.lower()
        
        i = 0
        while i < len(text_lower):
            char = text_lower[i]
            
            # Check for digraphs first (lj, nj, dž)
            if i + 1 < len(text_lower):
                digraph = text_lower[i:i+2]
                if digraph in self.LATIN_TO_IPA:
                    result.append(self.LATIN_TO_IPA[digraph])
                    # Check for accent after digraph
                    if i + 2 < len(text_lower) and text_lower[i + 2] in self.ACCENT_TO_IPA:
                        accent_mark = self.ACCENT_TO_IPA[text_lower[i + 2]]
                        if accent_mark:
                            result.append(accent_mark)
                        i += 1
                    i += 2
                    continue
            
            # Check if it's a Cyrillic letter
            if char in self.CYRILLIC_TO_IPA:
                ipa_char = self.CYRILLIC_TO_IPA[char]
                result.append(ipa_char)
                
                # Check for accent marks after this character
                if i + 1 < len(text_lower) and text_lower[i + 1] in self.ACCENT_TO_IPA:
                    accent_mark = self.ACCENT_TO_IPA[text_lower[i + 1]]
                    if accent_mark:
                        result.append(accent_mark)
                    i += 1  # Skip the accent mark
            # Check if it's a Latin letter
            elif char in self.LATIN_TO_IPA:
                ipa_char = self.LATIN_TO_IPA[char]
                result.append(ipa_char)
                
                # Check for accent marks after this character
                if i + 1 < len(text_lower) and text_lower[i + 1] in self.ACCENT_TO_IPA:
                    accent_mark = self.ACCENT_TO_IPA[text_lower[i + 1]]
                    if accent_mark:
                        result.append(accent_mark)
                    i += 1  # Skip the accent mark
            else:
                # Keep other characters as is
                result.append(char)
            
            i += 1
        
        return ''.join(result)
    
    def extract_stress_pattern(self, text: str) -> dict:
        """
        Extract stress pattern information from accented text.
        
        Returns:
            dict with 'position', 'type', 'length' info
        """
        if not text:
            return {}
        
        stress_pos = -1
        stress_type = None
        is_long = False
        
        for i, char in enumerate(text):
            if char in self.ACCENT_TO_IPA:
                stress_pos = i - 1  # Position of the vowel before the accent
                if char == '\u0300':
                    stress_type = 'rising'
                    is_long = False
                elif char == '\u0301':
                    stress_type = 'rising'
                    is_long = True
                elif char == '\u030f':
                    stress_type = 'falling'
                    is_long = True
                elif char == '\u0311':
                    stress_type = 'falling'
                    is_long = False
                elif char == '\u0304':
                    is_long = True
                break
        
        if stress_pos >= 0:
            return {
                'position': stress_pos,
                'type': stress_type,
                'length': 'long' if is_long else 'short'
            }
        
        return {}


# Singleton
_ipa_service = None

def get_ipa_service() -> IPAService:
    global _ipa_service
    if _ipa_service is None:
        _ipa_service = IPAService()
    return _ipa_service
