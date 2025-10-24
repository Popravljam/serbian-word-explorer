// Detect if we're in production or development
const API_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:8000/api' 
    : 'https://www.saptac.online/api';

// DOM elements
const wordInput = document.getElementById('wordInput');
const searchBtn = document.getElementById('searchBtn');
const resultContainer = document.getElementById('resultContainer');

// Event listeners
searchBtn.addEventListener('click', searchWord);
wordInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        searchWord();
    }
});

async function searchWord() {
    const word = wordInput.value.trim();
    
    if (!word) {
        return;
    }
    
    // Show loading state
    showLoading();
    searchBtn.disabled = true;
    
    try {
        const response = await fetch(`${API_URL}/word/${encodeURIComponent(word)}`);
        
        if (!response.ok) {
            if (response.status === 404) {
                showError('Reč nije pronađena u bazi podataka.');
            } else {
                showError('Greška pri pretraživanju reči.');
            }
            return;
        }
        
        const data = await response.json();
        displayResults(data);
        
    } catch (error) {
        console.error('Error:', error);
        showError('Greška pri povezivanju sa serverom. Proverite da li je backend pokrenut.');
    } finally {
        searchBtn.disabled = false;
    }
}

function showLoading() {
    resultContainer.classList.add('show');
    resultContainer.innerHTML = '<div class="loading">⏳ Učitavanje...</div>';
}

function showError(message) {
    resultContainer.classList.add('show');
    resultContainer.innerHTML = `<div class="error">❌ ${message}</div>`;
}

function displayResults(data) {
    let html = '';
    
    // Get the searched word (without accents) for highlighting
    const searchedWord = (data.searched_form || data.word).toLowerCase();
    
    // Word header
    html += '<div class="word-header">';
    html += `<div class="lemma">${data.lemma || data.word}</div>`;
    
    // Grammatical description sentence
    if (data.has_jezik_entry && data.morphology) {
        let description = buildGrammaticalDescription(data);
        if (description) {
            html += `<div style="font-size: 1.1em; color: #444; margin: 15px 0; line-height: 1.6;">${description}</div>`;
        }
    }
    
    // Show alternative interpretations if available
    if (data.variants && data.variants.length > 1) {
        html += '<div style="background: #fff3cd; padding: 12px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #ffc107;">';
        html += '<strong>⚠️ Višeznačnost:</strong> Ova reč može biti:';
        html += '<ul style="margin: 8px 0 0 0; padding-left: 25px;">';
        for (const variant of data.variants) {
            const posSr = cyrillicToLatin(variant.pos_sr);
            const formDescs = variant.labels.map(l => parseFormLabel(l)).filter(d => d);
            const formStr = formDescs.length > 0 ? ` u ${formDescs.join(' ili ')}` : '';
            html += `<li><strong>${posSr}</strong> "${variant.lemma}"${formStr}</li>`;
        }
        html += '</ul></div>';
    }
    
    html += '<div class="badges">';
    
    if (data.frequency) {
        html += `<span class="badge badge-frequency">Rang frekvencije: #${data.frequency.rank.toLocaleString()}</span>`;
    }
    
    html += '</div></div>';
    
    // Frequency info (if available)
    if (data.frequency) {
        html += '<div class="section">';
        html += '<div class="section-title">📊 Frekvencija</div>';
        html += '<div class="info-grid">';
        html += '<div class="info-card">';
        html += '<div class="info-label">Rang učestalosti</div>';
        html += `<div class="info-value">#${data.frequency.rank.toLocaleString()}</div>`;
        html += '</div>';
        html += '<div class="info-card">';
        html += '<div class="info-label">Broj pojavljivanja</div>';
        html += `<div class="info-value">${data.frequency.count.toLocaleString()}</div>`;
        html += '</div>';
        if (data.frequency.percentile) {
            html += '<div class="info-card">';
            html += '<div class="info-label">Percentil</div>';
            html += `<div class="info-value">${data.frequency.percentile}%</div>`;
            html += '</div>';
        }
        html += '</div></div>';
    }
    
    // Morphology table (if available)
    if (data.morphology && Object.keys(data.morphology).length > 0) {
        html += '<div class="section">';
        html += '<div class="section-title">📖 Morfološka tabela</div>';
        
        // Check if this is a noun (has sg/pl nom pattern)
        const isNoun = data.morphology['sg nom'] && data.morphology['pl nom'];
        
        // Check if this is an adjective (has gender and case markers)
        const isAdjective = Object.keys(data.morphology).some(key => 
            key.includes('m sg') || key.includes('f sg') || key.includes('n sg')
        );
        
        if (isNoun) {
            // NOUN TABLE - Two column format
            html += '<table class="morphology-table">';
            html += '<thead><tr><th>Padež</th><th>Jednina</th><th>Množina</th></tr></thead>';
            html += '<tbody>';
            
            const cases = [
                {label: 'Nominativ', sg: 'sg nom', pl: 'pl nom'},
                {label: 'Genitiv', sg: 'sg gen', pl: 'pl gen'},
                {label: 'Dativ', sg: 'sg dat', pl: 'pl dat'},
                {label: 'Akuzativ', sg: 'sg acc', pl: 'pl acc'},
                {label: 'Vokativ', sg: 'sg voc', pl: 'pl voc'},
                {label: 'Instrumental', sg: 'sg ins', pl: 'pl ins'},
                {label: 'Lokativ', sg: 'sg loc', pl: 'pl loc'}
            ];
            
            for (const caseInfo of cases) {
                const sgForms = data.morphology[caseInfo.sg];
                const plForms = data.morphology[caseInfo.pl];
                
                if (sgForms || plForms) {
                    html += '<tr>';
                    html += `<td><strong>${caseInfo.label}</strong></td>`;
                    // Highlight matching forms
                    const sgHtml = sgForms ? sgForms.map(f => highlightIfMatch(f, searchedWord)).join(', ') : '-';
                    const plHtml = plForms ? plForms.map(f => highlightIfMatch(f, searchedWord)).join(', ') : '-';
                    html += `<td class="accented-form">${sgHtml}</td>`;
                    html += `<td class="accented-form">${plHtml}</td>`;
                    html += '</tr>';
                }
            }
            
            html += '</tbody></table>';
        } else if (isAdjective) {
            // ADJECTIVE TABLE - Organized by case, gender, and definiteness
            const genders = ['m', 'f', 'n'];
            const genderNames = {'m': 'Mu\u0161ki', 'f': '\u017denski', 'n': 'Srednji'};
            const definiteness = ['short', 'long'];
            const defNames = {'short': 'Neodre\u0111eni (kratki)', 'long': 'Odre\u0111eni (dugi)'};
            const cases = ['nom', 'gen', 'dat', 'acc', 'voc', 'ins', 'loc'];
            const caseNames = {
                'nom': 'Nominativ', 'gen': 'Genitiv', 'dat': 'Dativ',
                'acc': 'Akuzativ', 'voc': 'Vokativ', 'ins': 'Instrumental', 'loc': 'Lokativ'
            };
            
            for (const def of definiteness) {
                const hasDefData = Object.keys(data.morphology).some(k => k.includes(def));
                if (!hasDefData) continue;
                
                html += `<h4 style="margin: 20px 0 10px 0; color: #667eea;">${defNames[def]}</h4>`;
                
                for (const gender of genders) {
                    const hasGenderData = Object.keys(data.morphology).some(k => 
                        k.includes(`${gender} `) && k.includes(def)
                    );
                    if (!hasGenderData) continue;
                    
                    html += `<h5 style="margin: 15px 0 10px 0; color: #888;">${genderNames[gender]} rod</h5>`;
                    html += '<table class="morphology-table">';
                    html += '<thead><tr><th>Pade\u017e</th><th>Jednina</th><th>Mno\u017eina</th></tr></thead>';
                    html += '<tbody>';
                    
                    for (const caseName of cases) {
                        const sgKey = `${gender} sg ${caseName} ${def}`;
                        const plKey = `${gender} pl ${caseName} ${def}`;
                        const sgForms = data.morphology[sgKey];
                        const plForms = data.morphology[plKey];
                        
                        // Also check for combined gender keys (m f n pl)
                        const combinedPlKey = `m f n pl ${caseName} ${def}`;
                        const combinedPlForms = data.morphology[combinedPlKey];
                        
                        // Show all rows, even if data is missing
                        html += '<tr>';
                        html += `<td><strong>${caseNames[caseName]}</strong></td>`;
                        // Highlight matching forms
                        const sgHtml = sgForms ? sgForms.map(f => highlightIfMatch(f, searchedWord)).join(', ') : '-';
                        const plHtml = (plForms || combinedPlForms) ? (plForms || combinedPlForms).map(f => highlightIfMatch(f, searchedWord)).join(', ') : '-';
                        html += `<td class="accented-form">${sgHtml}</td>`;
                        html += `<td class="accented-form">${plHtml}</td>`;
                        html += '</tr>';
                    }
                    
                    html += '</tbody></table>';
                }
            }
        } else {
            // VERB TABLE - Simple two column format
            html += '<table class="morphology-table">';
            html += '<thead><tr><th>Oblik</th><th>Oblici sa akcentima</th></tr></thead>';
            html += '<tbody>';
            
            for (const [label, forms] of Object.entries(data.morphology)) {
                html += '<tr>';
                html += `<td><strong>${label}</strong></td>`;
                // Highlight matching forms
                const formsHtml = forms.map(f => highlightIfMatch(f, searchedWord)).join(', ');
                html += `<td class="accented-form">${formsHtml}</td>`;
                html += '</tr>';
            }
            
            html += '</tbody></table>';
        }
        
        html += '</div>';
    }
    
    // Related forms from wordlist (if no jezik data)
    if (!data.has_jezik_entry && data.related_forms && data.related_forms.length > 0) {
        html += '<div class="section">';
        html += '<div class="section-title">📋 Povezani oblici (iz liste reči)</div>';
        html += '<div style="background: #f5f5f5; padding: 15px; border-radius: 10px;">';
        html += '<div style="display: flex; flex-wrap: wrap; gap: 8px;">';
        
        // Show only first 10 related forms
        const formsToShow = data.related_forms.slice(0, 10);
        formsToShow.forEach(form => {
            html += `<span style="background: white; padding: 6px 12px; border-radius: 5px; border: 1px solid #e0e0e0;">${form}</span>`;
        });
        
        html += '</div>';
        html += '<div style="margin-top: 10px; color: #666; font-size: 0.9em;">';
        html += '⚠️ Reč nije u bazi Jezik (nema akcenata), ali evo ';
        if (data.related_forms.length > 10) {
            html += `prvih 10 od ${data.related_forms.length} oblika iz liste srpskih reči.`;
        } else {
            html += 'oblika iz liste srpskih reči.';
        }
        html += '</div></div></div>';
    }
    
    // Info section
    if (data.has_jezik_entry) {
        html += '<div class="section">';
        html += '<div class="info-card">';
        html += '<div class="info-label">✓ Podaci iz baze Jezik</div>';
        html += '<div>Ovaj unos sadrži detaljne informacije o akcentima i morfologiji.</div>';
        html += '</div></div>';
    }
    
    resultContainer.innerHTML = html;
    resultContainer.classList.add('show');
}

// Helper to remove accents for comparison
function removeAccents(text) {
    return text.normalize('NFD').replace(/[\u0300-\u036f]/g, '');
}

// Helper to highlight form if it matches searched word
function highlightIfMatch(form, searchedWord) {
    const formClean = removeAccents(form).toLowerCase();
    const searchClean = removeAccents(searchedWord).toLowerCase();
    
    if (formClean === searchClean) {
        return `<span style="background: #fffacd; padding: 2px 4px; border-radius: 3px; font-weight: 600;">${form}</span>`;
    }
    return form;
}

// Cyrillic to Latin conversion for Serbian
function cyrillicToLatin(text) {
    const map = {
        'а':'a', 'б':'b', 'в':'v', 'г':'g', 'д':'d', 'ђ':'đ', 'е':'e', 'ж':'ž', 'з':'z',
        'и':'i', 'ј':'j', 'к':'k', 'л':'l', 'љ':'lj', 'м':'m', 'н':'n', 'њ':'nj', 'о':'o',
        'п':'p', 'р':'r', 'с':'s', 'т':'t', 'ћ':'ć', 'у':'u', 'ф':'f', 'х':'h', 'ц':'c',
        'ч':'č', 'џ':'dž', 'ш':'š',
        'А':'A', 'Б':'B', 'В':'V', 'Г':'G', 'Д':'D', 'Ђ':'Đ', 'Е':'E', 'Ж':'Ž', 'З':'Z',
        'И':'I', 'Ј':'J', 'К':'K', 'Л':'L', 'Љ':'Lj', 'М':'M', 'Н':'N', 'Њ':'Nj', 'О':'O',
        'П':'P', 'Р':'R', 'С':'S', 'Т':'T', 'Ћ':'Ć', 'У':'U', 'Ф':'F', 'Х':'H', 'Ц':'C',
        'Ч':'Č', 'Џ':'Dž', 'Ш':'Š'
    };
    return text.split('').map(char => map[char] || char).join('');
}

function buildGrammaticalDescription(data) {
    const word = data.searched_form || data.word;
    const isInflected = data.searched_form && data.found_lemma;
    
    // Get accented form - use form_info if available, otherwise from morphology
    let accentedForm = '';
    if (data.form_info && data.form_info.accented_form) {
        accentedForm = data.form_info.accented_form;
    } else if (data.morphology) {
        if (data.morphology['sg nom']) {
            accentedForm = data.morphology['sg nom'][0];
        } else if (data.morphology['m sg nom short']) {
            accentedForm = data.morphology['m sg nom short'][0];
        } else {
            const firstKey = Object.keys(data.morphology)[0];
            accentedForm = data.morphology[firstKey][0];
        }
    }
    
    const ipa = data.ipa || '';
    const parts = [];
    
    // Word with phonetic info
    let wordPart = `<strong>${word}</strong>`;
    if (accentedForm || ipa) {
        if (accentedForm) wordPart += ` /${accentedForm}/`;
        if (ipa) wordPart += ` (${cyrillicToLatin(ipa)})`;
    }
    parts.push(wordPart);
    
    // Part of speech
    if (data.pos_sr) {
        parts.push(`je <strong>${cyrillicToLatin(data.pos_sr)}</strong>`);
    }
    
    // Gender for nouns/adjectives
    if ((data.pos === 'noun' || data.pos === 'adjective') && data.gender) {
        const genderMap = {'m': 'muškog', 'f': 'ženskog', 'n': 'srednjeg'};
        if (genderMap[data.gender]) {
            parts.push(`${genderMap[data.gender]} roda`);
        }
    }
    
    // Specific form info if available
    if (isInflected && data.form_info) {
        const labels = data.form_info.labels || [data.form_info.label];
        if (labels && labels.length > 0) {
            const formDescs = labels.map(l => parseFormLabel(l)).filter(d => d);
            if (formDescs.length > 0) {
                if (formDescs.length === 1) {
                    parts.push(`u <strong>${formDescs[0]}</strong>`);
                } else {
                    // Multiple forms (e.g., "genitivu ili akuzativu")
                    const lastForm = formDescs.pop();
                    parts.push(`u <strong>${formDescs.join(', ')} ili ${lastForm}</strong>`);
                }
            }
        }
        parts.push(`(osnova: <strong>${data.found_lemma}</strong>)`);
    } else if (!isInflected) {
        // Base form descriptions
        if (data.pos === 'noun') {
            parts.push('u nominativu jednine');
        } else if (data.pos === 'verb') {
            parts.push('u <strong>infinitivu</strong>');
        }
    }
    
    if (parts.length > 1) {
        return parts.join(' ') + '.';
    }
    
    return null;
}

function parseFormLabel(label) {
    // Parse morphology labels into readable Serbian
    
    // Check for verb forms first
    if (label.includes('prs')) {
        // Present tense: "prs 1 sg" -> "prvom licu jednine prezenta"
        const personMap = {'1': 'prvom', '2': 'drugom', '3': 'trećem'};
        const numberMap = {'sg': 'jednine', 'pl': 'množine'};
        
        const personMatch = label.match(/\d/);
        const person = personMatch ? personMap[personMatch[0]] : '';
        const number = label.includes('sg') ? 'jednine' : label.includes('pl') ? 'množine' : '';
        
        if (person && number) {
            return `${person} licu ${number} prezenta`;
        }
    }
    
    if (label.includes('imv')) {
        // Imperative: "imv 2 sg" -> "imperativu drugog lica jednine"
        const personMap = {'1': 'prvog', '2': 'drugog'};
        const numberMap = {'sg': 'jednine', 'pl': 'množine'};
        
        const personMatch = label.match(/\d/);
        const person = personMatch ? personMap[personMatch[0]] : '';
        const number = label.includes('sg') ? 'jednine' : label.includes('pl') ? 'množine' : '';
        
        if (person && number) {
            return `imperativu ${person} lica ${number}`;
        }
    }
    
    if (label.includes('pf')) {
        // Past participle: "pf m sg" -> "glagolskom pridevu prošlom muškog roda jednine"
        const genderMap = {'m': 'muškog', 'f': 'ženskog', 'n': 'srednjeg'};
        const numberMap = {'sg': 'jednine', 'pl': 'množine'};
        
        let gender = '';
        let number = '';
        
        for (const [key, val] of Object.entries(genderMap)) {
            if (label.includes(` ${key} `)) {
                gender = val;
                break;
            }
        }
        
        for (const [key, val] of Object.entries(numberMap)) {
            if (label.includes(key)) {
                number = val;
                break;
            }
        }
        
        if (gender && number) {
            return `glagolskom pridevu prošlom ${gender} roda ${number}`;
        }
    }
    
    // Noun/adjective cases
    const caseMap = {
        'nom': 'nominativu',
        'gen': 'genitivu', 
        'dat': 'dativu',
        'acc': 'akuzativu',
        'voc': 'vokativu',
        'ins': 'instrumentalu',
        'loc': 'lokativu'
    };
    
    const numberMap = {
        'sg': 'jednine',
        'pl': 'množine'
    };
    
    // Extract case and number from label (e.g. "sg gen", "pl nom")
    let caseName = '';
    let numberName = '';
    
    for (const [key, val] of Object.entries(caseMap)) {
        if (label.includes(key)) {
            caseName = val;
            break;
        }
    }
    
    for (const [key, val] of Object.entries(numberMap)) {
        if (label.includes(key)) {
            numberName = val;
            break;
        }
    }
    
    if (caseName && numberName) {
        return `${caseName} ${numberName}`;
    }
    
    return null;
}

// Focus input on load
wordInput.focus();
