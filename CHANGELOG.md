# 📝 Changelog - Piper TTS Integration

**Date:** December 16, 2025  
**Version:** 2.0 (Full Speech-to-Speech Pipeline)

---

## 🎯 Summary of Changes

This update completes the **full offline speech-to-speech translation pipeline** by integrating Piper TTS and updating all documentation.

### Before (v1.0):
```
Speech → Whisper STT → M2M100 Translation → Text Output ❌
```

### After (v2.0):
```
Speech → Whisper STT → M2M100 Translation → Piper TTS → Speech Output ✅
```

---

## ✨ New Features

### 1. Piper TTS Integration ✅
- **Neural Text-to-Speech** using Piper (ONNX runtime)
- **5 Language Voices:**
  - English (en_US-lessac-medium)
  - Hindi (hi_IN-high)
  - French (fr_FR-siwis-medium)
  - Spanish (es_ES-davefx-medium)
  - German (de_DE-thorsten-medium)
- **Auto-download** of Piper binary via `download_models.py`
- **Auto-download** of voice models from HuggingFace
- **Base64 audio encoding** for efficient frontend delivery

### 2. Frontend Enhancements ✅
- **Auto-play** translated audio
- **Manual replay** button (🔊)
- **Audio status indicator** ("🔊 Audio ready")
- **Copy to clipboard** functionality (📋)
- **Improved UI/UX** with visual feedback

### 3. Backend Improvements ✅
- **Full pipeline** implementation in `main.py`
- **Piper subprocess** management with proper error handling
- **Temporary file** cleanup
- **Comprehensive logging** for debugging
- **Voice model mapping** by language

### 5. Convenience Scripts ✅
- **start.ps1** - PowerShell quick-start script
- **start.bat** - Windows Batch quick-start script
- **Automatic environment checks** before launch

---

## 📁 Files Modified

### Updated Files:
| File | Changes |
|:-----|:--------|
| `README.md` | Complete rewrite with TTS pipeline, API docs, troubleshooting |
| `backend/main.py` | Fixed Hindi voice filename (`hi_IN-high.onnx`) |

### New Files:
| File | Purpose |
|:-----|:--------|

| `start.ps1` | PowerShell launcher for both backend/frontend |
| `start.bat` | Batch file launcher (alternative to .ps1) |

---

## 🔧 Technical Changes

### Backend (`main.py`)

#### Added:
```python
class ModelManager:
    def __init__(self):
        # Piper paths
        self.piper_dir = os.path.join(os.path.dirname(__file__), "piper")
        self.piper_exe = os.path.join(self.piper_dir, "piper.exe")
        self.voices_dir = os.path.join(self.piper_dir, "voices")
        self.piper_voices = {}
    
    def _load_piper_voices(self):
        """Map voice files for each language"""
        voice_mapping = {
            "english": "en_US-lessac-medium.onnx",
            "hindi": "hi_IN-high.onnx",
            "french": "fr_FR-siwis-medium.onnx",
            "spanish": "es_ES-davefx-medium.onnx",
            "german": "de_DE-thorsten-medium.onnx"
        }
        # Load and verify voices...
    
    def generate_speech(self, text, language):
        """Generate speech using Piper binary"""
        # Subprocess execution with proper error handling
        # Base64 encoding for frontend delivery
```

#### Modified:
```python
@app.post("/api/translate-audio")
async def translate_audio(...):
    # Step 1: STT (Whisper) ✅
    # Step 2: Translation (M2M100) ✅
    # Step 3: TTS (Piper) ✅ NEW!
    
    return {
        "transcribed_text": transcribed,
        "translated_text": translated,
        "audio_file": audio_base64,  # NEW!
        "audio_format": "wav"  # NEW!
    }
```

### Frontend (`App.js`)

#### Added:
```javascript
const [translatedAudioBlob, setTranslatedAudioBlob] = useState(null);
const [isPlayingTranslation, setIsPlayingTranslation] = useState(false);
const translationAudioRef = useRef(null);

// Convert base64 to Blob
const base64ToBlob = (base64, contentType) => { ... }

// Play translated audio
const playTranslation = (audioBlob) => {
    const audio = new Audio(audioUrl);
    audio.play();
}

// Auto-play after translation
if (res.data.audio_file) {
    const audioBlob = base64ToBlob(res.data.audio_file, 'audio/wav');
    setTranslatedAudioBlob(audioBlob);
    setTimeout(() => playTranslation(audioBlob), 500);
}
```

#### UI Updates:
```jsx
{/* Manual replay button */}
<button 
    className={`icon-btn ${isPlayingTranslation ? 'playing' : ''}`}
    onClick={() => playTranslation()}
    disabled={!translatedAudioBlob}
>
    <FaVolumeUp />
</button>

{/* Audio ready indicator */}
{translatedAudioBlob && (
    <div className="audio-badge">🔊 Audio ready</div>
)}
```

### Download Script (`download_models.py`)

#### Enhanced:
```python
# Auto-detect latest Piper release from GitHub API
api_url = "https://api.github.com/repos/rhasspy/piper/releases/latest"
# Download Windows AMD64 binary automatically
# Extract and verify installation
# Download 5 voice models from HuggingFace

VOICE_MODELS = {
    "english": {...},
    "hindi": {...},
    "french": {...},
    "spanish": {...},
    "german": {...}
}
```

---

## 🔒 Security & Privacy

### Maintained 100% Offline Operation:
- ✅ No internet required (after setup)
- ✅ No API calls
- ✅ No data transmission
- ✅ All processing local
- ✅ Temporary files auto-deleted

### New Components (All Offline):
- ✅ Piper binary (standalone executable)
- ✅ ONNX voice models (local files)
- ✅ espeak-ng phoneme data (local files)

---

## 📊 Download Requirements

### New Downloads (One-Time):
| Component | Size | Notes |
|:----------|-----:|:------|
| Piper binary | ~50 MB | Auto-downloaded |
| English voice | ~63 MB | en_US-lessac |
| Hindi voice | ~85 MB | hi_IN-high |
| French voice | ~63 MB | fr_FR-siwis |
| Spanish voice | ~63 MB | es_ES-davefx |
| German voice | ~63 MB | de_DE-thorsten |
| **Total New** | **~390 MB** | Added to existing ~3GB |

### Total System Size:
- **Before:** ~3 GB (Whisper + M2M100 + packages)
- **After:** ~3.4 GB (+ Piper + voices)

---

## 🐛 Bug Fixes

### Fixed Issues:
1. ✅ **Hindi voice filename mismatch**
   - Changed `hi_IN-medium.onnx` → `hi_IN-high.onnx`
   - Matches actual downloaded voice model

2. ✅ **Missing TTS in pipeline**
   - Implemented full Piper TTS integration
   - Added subprocess management

3. ✅ **Documentation outdated**
   - README said "TTS intentionally disabled"
   - Updated to reflect current implementation

4. ✅ **No usage examples**
   - Created comprehensive USAGE_GUIDE.md
   - Added practical scenarios

---

## 🔮 Future Enhancements (Not in This Release)

### Planned for v3.0:
- [ ] Real-time streaming audio translation
- [ ] Multiple speaker detection (diarization)
- [ ] Conversation history/logging
- [ ] Additional language support (Arabic, Russian, Chinese)
- [ ] Docker containerization
- [ ] Batch processing mode
- [ ] GPU optimization for Piper TTS
- [ ] Voice selection per language (multiple voices)

---
