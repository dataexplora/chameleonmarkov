# 🎵 CHAMELEON - Οδηγός Εγκατάστασης και Χρήσης

## Τι είναι το CHAMELEON;

Το **CHAMELEON** είναι ένα σύστημα τεχνητής νοημοσύνης για την **αυτόματη εναρμόνιση μελωδιών** με διαφορετικά μουσικά στυλ. Μπορεί να μάθει από υπάρχοντα μουσικά έργα και να εναρμονίσει νέες μελωδίες στο στυλ που επιλέγετε (π.χ. Bach Chorales, Jazz, Impressionistic, κλπ.).

## Αρχιτεκτονική Συστήματος

```
┌─────────────────────────────────────────────────────────────┐
│                    CHAMELEON SYSTEM                          │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  1. TRAINING PHASE                                           │
│     training_data/*.xml → train_all_idioms.py                │
│                        ↓                                     │
│                    trained_idioms/*.pickle                   │
│                                                               │
│  2. BLENDING PHASE (Optional)                                │
│     trained_idioms/*.pickle → blend_all_idioms.py            │
│                            ↓                                 │
│                    blended_idioms/*.pickle                   │
│                                                               │
│  3. HARMONISATION PHASE                                      │
│     Web UI → Upload Melody → Select Style → Download Result │
│              (chameleon_server.py - Flask)                   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Τεχνολογίες

- **music21**: Ανάλυση και επεξεργασία μουσικών αρχείων
- **TensorFlow + LSTM**: Neural Networks για voice leading
- **HMM (Hidden Markov Models)**: Επιλογή συγχορδιών
- **Flask**: Web server για το UI
- **OpenSheetMusicDisplay**: Εμφάνιση παρτιτούρας στο browser

## Προαπαιτούμενα

### 1. Python 3.8+
Το σύστημα χρειάζεται Python 3.8 ή νεότερο.

```bash
python --version
```

### 2. Εγκατάσταση Dependencies

```bash
pip install -r requirements.txt
```

**Σημαντικά Packages:**
- `music21` - Μουσική ανάλυση (βασική εξάρτηση)
- `tensorflow` - Neural Networks για voice leading
- `Flask` - Web server
- `numpy`, `scipy`, `matplotlib` - Μαθηματικοί υπολογισμοί

## Πώς να Τρέξετε το Σύστημα

### Βήμα 1: Έλεγχος Εκπαιδευμένων Μοντέλων

Τα εκπαιδευμένα μοντέλα (idioms) βρίσκονται στους φακέλους:
- `trained_idioms/` - Βασικά μοντέλα
- `static/trained_idioms/` - Μοντέλα για το web server
- `blended_idioms/` - Συνδυασμένα μοντέλα (blends)

**Διαθέσιμα Στυλ:**
- BachChorales.pickle
- Jazz.pickle
- beatles.pickle
- Hindemith.pickle
- modalChorales.pickle
- organum.pickle
- fauxbourdon.pickle

### Βήμα 2: Εκκίνηση Web Server

```bash
python chameleon_server.py
```

Το server θα ξεκινήσει στο: **http://localhost:8885**

### Βήμα 3: Χρήση Web Interface

1. Ανοίξτε browser στο `http://localhost:8885`
2. Ανεβάστε ένα XML αρχείο μελωδίας (δείτε template format)
3. Επιλέξτε:
   - **Style 1 / Style 2**: Το μουσικό στυλ
   - **Mode**: Την τονικότητα (Auto για αυτόματη ανίχνευση)
   - **Tonal Difference**: Για blending
   - **Voice Leading**: NoVL ή BBVL (bidirectional)
   - **Chord Families**: Για grouping
4. Πατήστε **Harmonise**
5. Κατεβάστε το αποτέλεσμα (XML + MIDI)

## Προχωρημένη Χρήση

### Training Νέων Idioms

Αν θέλετε να εκπαιδεύσετε το σύστημα με νέα μουσικά δεδομένα:

1. Τοποθετήστε XML αρχεία στο `training_data/YOUR_STYLE_NAME/`
2. Τρέξτε:
```bash
python train_all_idioms.py
```

Το script θα:
- Αναλύσει όλα τα αρχεία
- Εξάγει GCTs (Generalised Chord Types)
- Υπολογίσει Markov chains
- Ανιχνεύσει cadences
- Αποθηκεύσει το μοντέλο στο `trained_idioms/YOUR_STYLE_NAME.pickle`

### Blending Idioms

Για να δημιουργήσετε υβριδικά στυλ:

```bash
python blend_all_idioms.py
```

Αυτό θα συνδυάσει όλα τα διαθέσιμα idioms σε ζευγάρια.

### Εκτύπωση Πληροφοριών Idiom

Για να δείτε τι έχει μάθει ένα idiom:

```python
import idiom_printer as prnt
prnt.print_idiom('BachChorales')
```

## Format Μελωδίας (Input Template)

Το XML αρχείο πρέπει να έχει συγκεκριμένη δομή με layers:
- **Part 0**: Μελωδία
- **Part 1**: Important Notes (σημαντικές νότες)
- **Part 2**: Harmonic Rhythm (ρυθμός αρμονίας)
- **Part -3**: Chord Constraints (περιορισμοί συγχορδιών)
- **Part -2**: Tonality (τονικότητα)
- **Part -1**: Grouping

Δείτε παράδειγμα: [Template Example](http://ccm.web.auth.gr/melodyinput.html)

## Αλγόριθμος Εναρμόνισης

```
INPUT: Μελωδία + Constraints
    ↓
1. Ανάλυση Tonality & Grouping
    ↓
2. Εφαρμογή Cadences (τέλη φράσεων)
    ↓
3. cHMM για επιλογή συγχορδιών
    ↓
4. Voice Leading:
   - Simple: Κοντινότερες νότες
   - NN: LSTM Neural Network
   - BBVL: Bidirectional με backtracking
    ↓
OUTPUT: Αρμονισμένη παρτιτούρα (XML + MIDI)
```

## Troubleshooting

### Πρόβλημα: "ModuleNotFoundError: No module named 'music21'"
**Λύση:**
```bash
pip install music21
```

### Πρόβλημα: "ModuleNotFoundError: No module named 'tensorflow'"
**Λύση:**
```bash
pip install tensorflow
```

### Πρόβλημα: Server δεν ξεκινά
**Έλεγχος:**
- Port 8885 μήπως χρησιμοποιείται
- Folder structure σωστός
- Υπάρχουν trained idioms στο `static/trained_idioms/`

### Πρόβλημα: "No trained idioms found"
**Λύση:**
Αντιγράψτε τα idioms από `trained_idioms/` στο `static/trained_idioms/`:
```bash
cp trained_idioms/*.pickle static/trained_idioms/
```

## Δομή Project

```
chameleon/
├── chameleon_server.py          # Flask web server
├── train_all_idioms.py          # Training script
├── blend_all_idioms.py          # Blending script
├── idiom_printer.py             # Εκτύπωση info idiom
│
├── CM_generate/                 # Harmonisation algorithms
│   ├── CM_GN_harmonise_melody.py
│   ├── CM_GN_cHMM_functions.py
│   ├── CM_GN_cadence_functions.py
│   └── CM_GN_voice_leading_functions.py
│
├── CM_train/                    # Training algorithms
│   ├── CM_TR_TrainingIdiom_class.py
│   └── CM_TR_TrainingPiece_class.py
│
├── CM_blending/                 # Blending algorithms
│   ├── CM_BlendingSession.py
│   └── CM_BlendedIdiomCompiler.py
│
├── CM_NN_VL/                    # Neural Network Voice Leading
│   ├── NN_VL_model.py
│   ├── VL_LSTM_train.py
│   └── BachChorales/
│
├── CM_auxiliary/                # Helper functions
│   ├── CM_TonalityGrouping_classes.py
│   ├── CM_similarity_functions.py
│   └── GCT_functions.py
│
├── training_data/               # Training datasets (XML)
├── trained_idioms/              # Trained models (pickle)
├── templates/                   # HTML templates
└── static/                      # Static files (CSS, JS, trained idioms)
```

## Credits

**Author**: Maximos Kaliakatsos-Papakostas (maxk)

## Επόμενα Βήματα

1. ✅ Εγκατάσταση dependencies (`pip install -r requirements.txt`)
2. ✅ Έλεγχος trained idioms
3. ✅ Εκκίνηση server (`python chameleon_server.py`)
4. 🎵 Εναρμόνιση μελωδίας!

