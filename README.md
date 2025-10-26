# Serbian Word Explorer

A comprehensive web application for exploring Serbian words with detailed morphological information, accent patterns, and frequency data.

**🌐 Live at:** [https://saptac.online/recnik/](https://saptac.online/recnik/)

## Features

- ✅ **Full morphological paradigms** - All case forms for nouns, conjugations for verbs with precise accent marking
- ✅ **Accent information** - Precise pitch accent marking from jezik database (~3,000 lemmas)
- ✅ **Etymology** - Word origins from Serbian Wiktionary
- ✅ **Definitions** - Word meanings from Serbian Wiktionary  
- ✅ **Word validation** - Check if a word exists (2.8M word database)
- ✅ **Frequency data** - See how common a word is (2.8M word forms)
- ✅ **Multi-source data** - Combines jezik, spisak-srpskih-reci, inflection-sr, and Wiktionary
- ✅ **Clean, responsive interface** - Works on desktop and mobile devices

## Data Sources

1. **[jezik](https://github.com/Zabolekar/jezik)** - Morphology with detailed accent information (~3K lemmas)
2. **[spisak-srpskih-reci](https://github.com/turanjanin/spisak-srpskih-reci)** - Serbian word list (2.8M words)
3. **[inflection-sr](https://github.com/nciric/inflection-sr)** - Word frequency data
4. **[Serbian Wiktionary](https://sr.wiktionary.org/)** - Etymology and definitions

## Usage

Visit [https://saptac.online/recnik/](https://saptac.online/recnik/) and:

1. Type a Serbian word in Cyrillic (e.g., `школа`, `човек`, `добар`)
2. Press Enter or click "Претражи"
3. View comprehensive information:
   - Part of speech and grammatical gender
   - Full declension/conjugation table with accent marks
   - Word frequency ranking
   - Existence validation

## Local Development

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

## Running Locally

### Quick Start

```bash
./run.sh
```

This starts both backend (port 8000) and frontend (port 3000).

### Manual Start

**Backend:**
```bash
cd backend
source venv/bin/activate
python main.py
```

**Frontend:**
```bash
cd frontend
python3 -m http.server 3000
```

Then open http://localhost:3000

## API Endpoints

**Production:** `https://saptac.online/api/`  
**Local:** `http://localhost:8000/api/`

### `GET /api/word/{word}`

Get complete information about a word.

**Example:**
```bash
curl https://saptac.online/api/word/школа
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

### `GET /health`

Health check endpoint.

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

## Deployment

The application is deployed on a VPS server at **saptac.online**.

### Architecture
- **Frontend:** Static HTML/JS served via Nginx
- **Backend:** FastAPI service running as systemd service
- **Data:** ~12K lemmas (jezik) + 2.8M words (spisak-srpskih-reci + inflection-sr)

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment documentation.

## Future Enhancements

- [ ] IPA pronunciation generation
- [x] Definitions from Wiktionary
- [x] Etymology information
- [ ] Example sentences
- [ ] Synonyms/antonyms (partially available via definitions)
- [ ] Latin/Cyrillic toggle
- [ ] Ekavian/Ijekavian variants
- [ ] Audio pronunciation
- [ ] Redis caching for performance
- [ ] User contributions
- [ ] Search history
- [ ] Expand Wiktionary coverage (currently ~3K lemmas)

## License

This project combines data from multiple sources, each with their own licenses. Please refer to the individual repositories for licensing information.

## Credits

- **jezik** by @Zabolekar - Morphology and accent data
- **spisak-srpskih-reci** by @turanjanin - Word list
- **inflection-sr** by @nciric - Frequency data
