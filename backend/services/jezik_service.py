import sys
import os
from typing import Optional, Dict, Any, List

# Add jezik to path - works for both development and production
if os.path.exists('/opt/recnik/jezik'):
    JEZIK_PATH = '/opt/recnik/jezik'
else:
    JEZIK_PATH = os.path.join(os.path.dirname(__file__), '../../../jezik')
sys.path.insert(0, JEZIK_PATH)

try:
    from lookup import lookup, random_key
except ImportError as e:
    print(f"Warning: Could not import jezik library: {e}")
    lookup = None
    random_key = None


class JezikService:
    """Service for interacting with the jezik morphology library."""
    
    def __init__(self):
        self.available = lookup is not None
    
    def lookup_word(self, word: str) -> Optional[Dict[str, Any]]:
        """
        Look up a word in the jezik database and return structured data.
        """
        if not self.available:
            return None
        
        try:
            result = lookup(word)
            
            if not result or len(result) == 0:
                return None
            
            # Get the first table (first variant)
            table = result[0]
            
            # Extract basic info
            data = {
                "lemma": word,
                "pos": table.pos,
                "pos_sr": self._get_pos_serbian(table.pos),
                "gender": self._extract_gender(table),
                "morphology": self._parse_morphology(table),
                "variants": len(result) if len(result) > 1 else None
            }
            
            return data
            
        except Exception as e:
            print(f"Error looking up word '{word}': {e}")
            return None
    
    def get_random_word(self) -> Optional[Dict[str, str]]:
        """Get a random word from the jezik database."""
        if not self.available or random_key is None:
            return None
        
        try:
            key, yat = random_key()
            word_data = self.lookup_word(key)
            if word_data:
                word_data["word"] = key
                return word_data
            return {"word": key}
        except Exception as e:
            print(f"Error getting random word: {e}")
            return None
    
    def _get_pos_serbian(self, pos: str) -> str:
        """Convert POS tag to Serbian."""
        pos_map = {
            "noun": "именица",
            "verb": "глагол",
            "adjective": "придев",
            "adverb": "прилог"
        }
        return pos_map.get(pos, pos)
    
    def _extract_gender(self, table) -> Optional[str]:
        """Extract gender from the table caption or data."""
        # Try to extract from morphology labels
        for label, forms in table:
            if "m " in label:
                return "m"
            elif "f " in label:
                return "f"
            elif "n " in label:
                return "n"
        return None
    
    def _parse_morphology(self, table) -> Dict[str, Any]:
        """Parse the morphology table into a structured format."""
        morphology = {}
        
        for label, forms in table:
            # Clean up the label
            clean_label = label.strip()
            
            # Store the forms
            morphology[clean_label] = forms
        
        return morphology
    
    def find_all_lemmas_by_form(self, word: str) -> List[Dict[str, Any]]:
        """Find ALL possible lemmas for a word form.
        
        Returns a list of all matches (e.g., 'zlo' as noun AND as adjective 'zao').
        """
        if not self.available or not word or len(word) < 3:
            return []
        
        word_clean = self._remove_accents(word.lower())
        all_results = []
        seen_lemmas = set()  # Track which lemmas we've already checked
        
        # Strategy 1: Try different root lengths (prefix)
        for root_len in range(len(word), 2, -1):
            root = word[:root_len]
            self._check_lemma_match(root, word_clean, all_results, seen_lemmas)
        
        # Strategy 2: Try character substitutions for last char(s)
        # e.g., "zla" -> try "zlo", "zao", etc.
        if len(word) >= 3:
            # Common Serbian endings substitutions
            substitutions = [
                (word[:-1] + 'o'),  # zla -> zlo
                (word[:-1] + 'a'),  # zlo -> zla  
                (word[:-1] + 'i'),  # zla -> zli
                (word[:-1] + 'e'),  # zla -> zle
                (word[:-2] + 'ao') if len(word) >= 3 else None,  # zla -> zao
                (word[:-2] + 'eo') if len(word) >= 3 else None,  # zla -> zeo
            ]
            
            # Verb infinitive substitutions (for inflected verb forms)
            # e.g., "piši" -> "pisati", "pišem" -> "pisati"
            # Problem: consonant alternations (š->s, č->c, ž->z, etc.)
            if len(word) >= 3:
                # Try different root lengths
                for trim_len in [1, 2, 3]:
                    if len(word) > trim_len:
                        root = word[:-trim_len]
                        # Try infinitive endings
                        for inf_ending in ['ati', 'iti', 'eti']:
                            substitutions.append(root + inf_ending)
                            
                            # Also try with consonant alternations
                            # š->s, č->c, ž->z, ć->t, đ->d
                            if root and root[-1] in 'ščžćđ':
                                alt_map = {'š': 's', 'č': 'c', 'ž': 'z', 'ć': 't', 'đ': 'd'}
                                alt_root = root[:-1] + alt_map.get(root[-1], root[-1])
                                substitutions.append(alt_root + inf_ending)
            
            for sub in substitutions:
                if sub and sub != word:
                    self._check_lemma_match(sub, word_clean, all_results, seen_lemmas)
        
        return all_results
    
    def _check_lemma_match(self, root: str, word_clean: str, all_results: list, seen_lemmas: set):
        """Helper to check if a root matches the word form."""
        if root in seen_lemmas:
            return
        seen_lemmas.add(root)
        
        try:
            result = lookup(root)
            if result and len(result) > 0:
                # Check ALL variants returned by lookup
                for variant_idx, table in enumerate(result):
                    matching_labels = []
                    accented_form = None
                    
                    for label, forms in table:
                        for form in forms:
                            form_clean = self._remove_accents(form)
                            if form_clean == word_clean:
                                matching_labels.append(label.strip())
                                if not accented_form:
                                    accented_form = form
                                break
                    
                    if matching_labels:
                        # Check if we already have this lemma+pos combo
                        combo_key = f"{root}:{table.pos}"
                        if not any(r.get('lemma') == root and r.get('pos') == table.pos for r in all_results):
                            all_results.append({
                                "lemma": root,
                                "labels": matching_labels,
                                "accented_form": accented_form,
                                "pos": table.pos,
                                "variant_idx": variant_idx
                            })
        except:
            pass
    
    def find_lemma_by_form(self, word: str) -> Optional[Dict[str, Any]]:
        """Try to find a lemma by searching for an inflected form.
        
        Strategy: Try progressively shorter roots of the word.
        Returns all matching forms (e.g., genitiv and akuzativ for "čoveka").
        """
        if not self.available or not word or len(word) < 3:
            return None
        
        word_clean = self._remove_accents(word.lower())
        
        # Try different root lengths
        for root_len in range(len(word), 2, -1):
            root = word[:root_len]
            
            # Try the root as a potential lemma
            try:
                result = lookup(root)
                if result and len(result) > 0:
                    table = result[0]
                    
                    # Collect ALL matching forms
                    matching_labels = []
                    accented_form = None
                    
                    for label, forms in table:
                        for form in forms:
                            form_clean = self._remove_accents(form)
                            if form_clean == word_clean:
                                matching_labels.append(label.strip())
                                if not accented_form:
                                    accented_form = form
                                break
                    
                    if matching_labels:
                        return {
                            "lemma": root,
                            "labels": matching_labels,  # Multiple labels
                            "accented_form": accented_form,
                            "table": table
                        }
            except:
                continue
        
        return None
    
    def identify_form(self, word: str, lemma: str) -> Optional[Dict[str, str]]:
        """Identify which specific form the word is (case, number, etc.)."""
        if not self.available:
            return None
        
        try:
            result = lookup(lemma)
            if not result or len(result) == 0:
                return None
            
            table = result[0]
            
            # Remove accents from search word for comparison
            word_clean = self._remove_accents(word)
            
            # Search through all forms to find a match
            for label, forms in table:
                for form in forms:
                    form_clean = self._remove_accents(form)
                    if form_clean == word_clean:
                        return {
                            "label": label.strip(),
                            "accented_form": form
                        }
            
            return None
            
        except Exception as e:
            print(f"Error identifying form for '{word}': {e}")
            return None
    
    def _remove_accents(self, text: str) -> str:
        """Remove accent marks from text."""
        import unicodedata
        # Normalize and remove combining characters (accents)
        normalized = unicodedata.normalize('NFD', text)
        return ''.join(char for char in normalized if unicodedata.category(char) != 'Mn')


# Singleton instance
_jezik_service = None

def get_jezik_service() -> JezikService:
    global _jezik_service
    if _jezik_service is None:
        _jezik_service = JezikService()
    return _jezik_service
