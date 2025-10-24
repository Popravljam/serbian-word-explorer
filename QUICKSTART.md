# Quick Start Guide 🚀

## Running the Application

### Option 1: Use the run script (Recommended)

```bash
cd /Users/lazar/serbian-word-explorer
./run.sh
```

This will:
1. Start the backend API on port 8000 (if not already running)
2. Start the frontend on port 3000
3. Open your browser to http://localhost:3000

### Option 2: Manual startup

**Terminal 1 - Backend:**
```bash
cd /Users/lazar/serbian-word-explorer/backend
source venv/bin/activate
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd /Users/lazar/serbian-word-explorer/frontend
python3 -m http.server 3000
```

Then open: http://localhost:3000

## Testing the API Directly

```bash
# Health check
curl http://localhost:8000/health

# Look up a word
curl http://localhost:8000/api/word/школа

# Get a random word
curl http://localhost:8000/api/random
```

## Example Searches

Try these words in the web interface:

- **школа** - school (noun with full declension)
- **човек** - person (irregular plural: људи)
- **добар** - good (adjective with short/long forms)
- **grad** - city
- **књига** - book
- **учитељ** - teacher

## Current Features

✅ Word validation (2.8M words)
✅ Full morphological paradigms with accents
✅ Frequency rankings
✅ Part of speech tagging
✅ Gender information

## Data Statistics

- **Jezik database**: ~12,000 lemmas with full accent info
- **Word list**: 2,788,833 words
- **Frequency data**: 2,800,421 word forms

## Troubleshooting

### Backend won't start
```bash
# Kill any existing process on port 8000
lsof -ti:8000 | xargs kill -9

# Restart
cd backend
source venv/bin/activate
python main.py
```

### Frontend shows connection error
- Make sure backend is running on port 8000
- Check: `curl http://localhost:8000/health`

### Word not found
- The word might not be in the jezik database (only ~12K lemmas have full data)
- But it should still validate existence if it's in the 2.8M word list

## Next Steps

See README.md for:
- Detailed architecture
- API documentation
- Future enhancements
- Contributing guidelines
