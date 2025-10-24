import os
from typing import Optional, Dict

class FrequencyService:
    """Service for word frequency data."""
    
    def __init__(self):
        self.frequency_data = {}
        self.total_words = 0
        self._load_frequency_data()
    
    def _load_frequency_data(self):
        """Load frequency data from TSV file."""
        # Check production path first
        if os.path.exists('/opt/recnik/inflection-sr/data/word_frequency_table.tsv'):
            freq_file = '/opt/recnik/inflection-sr/data/word_frequency_table.tsv'
        else:
            # Development path
            freq_file = os.path.join(
                os.path.dirname(__file__),
                '../../../inflection-sr/data/word_frequency_table.tsv'
            )
        
        if not os.path.exists(freq_file):
            print(f"Warning: Frequency file not found at {freq_file}")
            return
        
        try:
            with open(freq_file, 'r', encoding='utf-8') as f:
                for i, line in enumerate(f, 1):
                    parts = line.strip().split('\t')
                    if len(parts) >= 2:
                        try:
                            count = int(parts[0])
                            word = parts[1]
                            # Store primary word form
                            self.frequency_data[word] = {
                                'count': count,
                                'rank': i
                            }
                            # Also store all variants if provided
                            if len(parts) >= 3:
                                variants = parts[2].split(', ')
                                for variant in variants:
                                    if variant and variant not in self.frequency_data:
                                        self.frequency_data[variant] = {
                                            'count': count,
                                            'rank': i
                                        }
                        except ValueError:
                            continue
            
            self.total_words = len(self.frequency_data)
            print(f"Loaded {self.total_words} words with frequency data")
            
        except Exception as e:
            print(f"Error loading frequency data: {e}")
    
    def get_frequency(self, word: str) -> Optional[Dict[str, int]]:
        """Get frequency data for a word with percentile."""
        data = self.frequency_data.get(word)
        if data and self.total_words > 0:
            # Calculate percentile (lower rank = higher percentile)
            percentile = 100 * (1 - (data['rank'] / self.total_words))
            data['percentile'] = round(percentile, 2)
        return data
    
    def get_rank(self, word: str) -> Optional[int]:
        """Get frequency rank for a word (1 = most frequent)."""
        data = self.frequency_data.get(word)
        return data['rank'] if data else None


# Singleton
_frequency_service = None

def get_frequency_service() -> FrequencyService:
    global _frequency_service
    if _frequency_service is None:
        _frequency_service = FrequencyService()
    return _frequency_service
