# Serbian Word Explorer 🔤

A comprehensive web application for exploring Serbian words with detailed morphological information, accent patterns, and frequency data.

## Features

- ✅ **Full morphological paradigms** - All case forms for nouns, conjugations for verbs
- ✅ **Accent information** - Precise pitch accent marking from jezik database
- ✅ **Word validation** - Check if a word exists (2.8M word database)
- ✅ **Frequency data** - See how common a word is
- ✅ **Multi-source data** - Combines jezik, spisak-srpskih-reci, and frequency corpus

## Data Sources

1. **[jezik](https://github.com/Zabolekar/jezik)** - Morphology with detailed accent information (~12K lemmas)
2. **[spisak-srpskih-reci](https://github.com/turanjanin/spisak-srpskih-reci)** - Serbian word list (2.8M words)
3. **[inflection-sr](https://github.com/nciric/inflection-sr)** - Word frequency data

## Setup

### Prerequisites

- Python 3.9+
- Web browser

### Installation

1. **Backend setup:**

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

2. **Ensure data repositories are in place:**

The project expects these repositories to be in the parent directory:
- `../jezik`
- `../spisak-srpskih-reci`
- `../inflection-sr`

If they're not already cloned, they should be there from earlier steps.

## Running the Application

### 1. Start the Backend

```bash
cd backend
source venv/bin/activate  # Activate virtual environment
python main.py
```

The API will start on `http://localhost:8000`

### 2. Start the Frontend

Simply open the HTML file in a browser:

```bash
cd frontend
open index.html  # macOS
# or
xdg-open index.html  # Linux
# or just double-click index.html in file explorer
```

Or use a simple HTTP server:

```bash
cd frontend
python3 -m http.server 3000
# Then open http://localhost:3000 in browser
```

## Usage

1. Open the web interface
2. Type a Serbian word in Cyrillic (e.g., `школа`, `човек`, `добар`)
3. Press Enter or click "Претражи"
4. View comprehensive word information:
   - Part of speech
   - Gender (for nouns)
   - Full declension/conjugation table with accents
   - Word frequency ranking
   - Validation status

## API Endpoints

### `GET /api/word/{word}`

Get complete information about a word.

**Example:**
```bash
curl http://localhost:8000/api/word/школа
```

**Response:**
```json
{
  "word": "школа",
  "exists": true,
  "lemma": "школа",
  "pos": "noun",
  "pos_sr": "именица",
  "gender": "f",
  "morphology": {
    "sg nom": ["шко̑ла"],
    "sg gen": ["шко̑ле̄"],
    "sg dat": ["шко̑ли"],
    ...
  },
  "frequency": {
    "rank": 1247,
    "count": 8532
  },
  "has_jezik_entry": true
}
```

### `GET /api/random`

Get a random word from the jezik database.

## Project Structure

```
serbian-word-explorer/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   └── services/
│       ├── jezik_service.py      # Jezik integration
│       ├── frequency_service.py  # Frequency data
│       └── wordlist_service.py   # Word validation
├── frontend/
│   ├── index.html          # Main UI
│   └── app.js              # Frontend logic
└── README.md
```

## Future Enhancements

- [ ] IPA pronunciation generation
- [ ] Definitions from Wiktionary
- [ ] Etymology information
- [ ] Example sentences
- [ ] Synonyms/antonyms
- [ ] Latin/Cyrillic toggle
- [ ] Ekavian/Ijekavian variants
- [ ] Audio pronunciation
- [ ] Database caching for performance
- [ ] User contributions

## License

This project combines data from multiple sources, each with their own licenses. Please refer to the individual repositories for licensing information.

## Credits

- **jezik** by @Zabolekar - Morphology and accent data
- **spisak-srpskih-reci** by @turanjanin - Word list
- **inflection-sr** by @nciric - Frequency data
