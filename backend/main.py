import sys
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, List, Any

# Add jezik to path - works for both development and production
if os.path.exists('/opt/recnik/jezik'):
    # Production path
    JEZIK_PATH = '/opt/recnik/jezik'
else:
    # Development path
    JEZIK_PATH = os.path.join(os.path.dirname(__file__), '../../jezik')
sys.path.insert(0, JEZIK_PATH)

from services.jezik_service import JezikService
from services.frequency_service import FrequencyService
from services.wordlist_service import WordlistService
from services.ipa_service import IPAService

app = FastAPI(title="Serbian Word Explorer API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
jezik_service = JezikService()
frequency_service = FrequencyService()
wordlist_service = WordlistService()
ipa_service = IPAService()


class WordResponse(BaseModel):
    word: str
    exists: bool
    lemma: Optional[str] = None
    lemma_latin: Optional[str] = None
    pos: Optional[str] = None
    pos_sr: Optional[str] = None
    gender: Optional[str] = None
    morphology: Optional[Dict[str, Any]] = None
    frequency: Optional[Dict[str, Any]] = None
    has_jezik_entry: bool = False
    ipa: Optional[str] = None
    stress_pattern: Optional[Dict[str, Any]] = None
    related_forms: Optional[List[str]] = None
    searched_form: Optional[str] = None
    found_lemma: Optional[str] = None
    form_info: Optional[Dict[str, Any]] = None  # Changed to Any to support both str and List[str]
    variants: Optional[List[Dict[str, Any]]] = None  # Multiple POS interpretations


@app.get("/")
def root():
    return {
        "message": "Serbian Word Explorer API",
        "version": "0.1.0",
        "endpoints": {
            "word_lookup": "/api/word/{word}",
            "health": "/health"
        }
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/api/word/{word}", response_model=WordResponse)
def get_word_info(word: str):
    """
    Get comprehensive information about a Serbian word.
    """
    result = {
        "word": word,
        "exists": False,
        "has_jezik_entry": False
    }
    
    # Try to get morphology from jezik
    # First try the word as-is
    jezik_data = jezik_service.lookup_word(word)
    
    # If not found, try to find lemma by searching inflected forms
    # Look for ALL possible interpretations
    if not jezik_data:
        all_lemmas = jezik_service.find_all_lemmas_by_form(word)
        if all_lemmas:
            # Use first result as primary
            lemma_result = all_lemmas[0]
            lemma = lemma_result["lemma"]
            jezik_data = jezik_service.lookup_word(lemma)
            if jezik_data:
                result["searched_form"] = word
                result["found_lemma"] = lemma
                result["form_info"] = {
                    "labels": lemma_result["labels"],
                    "accented_form": lemma_result["accented_form"]
                }
                
                # If there are multiple interpretations, add them as variants
                if len(all_lemmas) > 1:
                    result["variants"] = []
                    for alt_lemma in all_lemmas:
                        alt_data = jezik_service.lookup_word(alt_lemma["lemma"])
                        if alt_data:
                            result["variants"].append({
                                "lemma": alt_lemma["lemma"],
                                "pos": alt_data["pos"],
                                "pos_sr": alt_data["pos_sr"],
                                "labels": alt_lemma["labels"],
                                "accented_form": alt_lemma["accented_form"]
                            })
    
    if jezik_data:
        result["has_jezik_entry"] = True
        result["lemma"] = jezik_data.get("lemma")
        result["pos"] = jezik_data.get("pos")
        result["pos_sr"] = jezik_data.get("pos_sr")
        result["gender"] = jezik_data.get("gender")
        result["morphology"] = jezik_data.get("morphology")
        
        # Add IPA and stress pattern
        accented_form = None
        # If we searched for an inflected form, use that form's accent
        if result.get("form_info") and result["form_info"].get("accented_form"):
            accented_form = result["form_info"]["accented_form"]
        elif result.get("morphology"):
            # Otherwise use nominative singular
            if "sg nom" in result["morphology"]:
                accented_form = result["morphology"]["sg nom"][0]
            elif "m sg nom short" in result["morphology"]:
                accented_form = result["morphology"]["m sg nom short"][0]
            else:
                first_key = list(result["morphology"].keys())[0]
                accented_form = result["morphology"][first_key][0]
        
        if accented_form:
            ipa = ipa_service.to_ipa(accented_form)
            stress = ipa_service.extract_stress_pattern(accented_form)
            if ipa:
                result["ipa"] = ipa
            if stress:
                result["stress_pattern"] = stress
    
    # Check if word exists in word list
    exists = wordlist_service.word_exists(word)
    result["exists"] = exists
    
    # Get related forms from wordlist (inflected forms) - only if no jezik data
    if not jezik_data:
        related_forms = wordlist_service.find_related_forms(word, limit=50)
        if related_forms:
            result["related_forms"] = related_forms
    
    # Get frequency data
    freq_data = frequency_service.get_frequency(word)
    if freq_data:
        result["frequency"] = freq_data
    
    if not exists and not jezik_data:
        raise HTTPException(status_code=404, detail="Word not found")
    
    return result


@app.get("/api/random")
def get_random_word():
    """
    Get a random word from the jezik database.
    """
    word_data = jezik_service.get_random_word()
    if not word_data:
        raise HTTPException(status_code=500, detail="Could not fetch random word")
    
    return word_data


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
