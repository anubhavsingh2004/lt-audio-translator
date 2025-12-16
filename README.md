# 🚀 L&T Live Audio Translator

**Complete offline speech-to-speech translation system** designed for mission-critical / military-grade environments.

**Full Pipeline:** Whisper (STT) → M2M100 (Translation) → Piper (TTS)

---

## ✨ Features

This system is built for security, reliability, and complete local execution:

* **100% Offline Execution**
    * No cloud, no API keys, no internet required.
    * All models (Whisper, M2M100, Piper) run locally on the machine.
* **Secure & Private**
    * Suitable for sensitive / military contexts.
    * **No data leaves the device.**
* **Robust Speech-to-Text (STT)**
    * Uses OpenAI **Whisper** (local model) for multilingual transcription.
    * Handles noisy environments reasonably well.
* **Multilingual Translation**
    * Uses Meta's **M2M100** for direct translation between languages (e.g., English ↔ Hindi, English ↔ French).
* **Natural Text-to-Speech (TTS)**
    * Uses **Piper** neural TTS for high-quality voice synthesis.
    * Supports multiple languages with natural-sounding voices.
    * Fast inference with ONNX runtime.
* **Modern Web UI**
    * React frontend with microphone recording.
    * Live status display (recording, processing, translation complete).
    * Auto-play translated audio output.
    * Copy-to-clipboard functionality.

### Complete Pipeline

$$\text{Speech} \rightarrow \text{Whisper STT} \rightarrow \text{M2M100 Translation} \rightarrow \text{Piper TTS} \rightarrow \text{Speech Output}$$

---

## 💻 Tech Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Backend** | Python 3.11, FastAPI | API server, orchestration |
| **STT Model** | Whisper (local) | Speech-to-Text via PyTorch/Transformers |
| **Translation** | M2M100 (HuggingFace) | Text-to-Text Translation |
| **TTS Engine** | Piper (ONNX) | Neural Text-to-Speech synthesis |
| **Frontend** | React, Axios | User Interface |
| **Audio** | MediaRecorder API | Browser microphone capture |

---

## 🏗️ Architecture

1.  User speaks into the microphone in the browser (Frontend).
2.  Frontend records audio and sends the data to the Backend API.
3.  **Backend Processing:**
    * Runs **Whisper STT** $\rightarrow$ gets source-language text.
    * Runs **M2M100** $\rightarrow$ translates to target language text.
    * Runs **Piper TTS** $\rightarrow$ generates translated speech audio.
4.  Backend returns the **Original transcribed text**, **Translated text**, and **Audio file** (base64-encoded WAV).
5.  Frontend displays both texts and auto-plays the translated audio.

---

## 🌍 Supported Languages

| Language | STT | Translation | TTS Voice |
| :--- | :---: | :---: | :--- |
| **English** | ✅ | ✅ | en_US-lessac (medium) |
| **Hindi** | ✅ | ✅ | hi_IN (high quality) |
| **French** | ✅ | ✅ | fr_FR-siwis (medium) |
| **Spanish** | ✅ | ✅ | es_ES-davefx (medium) |
| **German** | ✅ | ✅ | de_DE-thorsten (medium) |

> **Note:** All languages work offline. Piper voice models are downloaded automatically via `download_models.py`.

---

## 🛠️ Prerequisites

Install these on the target machine:

* **Python 3.11** (recommended)
* **Node.js (LTS)** and **npm**
* **Git**
* **FFmpeg** (required by Whisper for audio decoding)

> **FFmpeg Installation on Windows:**
>
> ```bash
> winget install ffmpeg
> ```
> *Alternatively, download a static build and add `ffmpeg/bin` to your system's PATH.*

---

## ⚙️ Setup & Run (Quick Start)

### 1. Clone Repository

```bash
cd D:\
git clone https://github.com/YOUR_USERNAME/lt-audio-translator.git
cd lt-audio-translator
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\Activate.ps1   # PowerShell
# OR: venv\Scripts\activate.bat  (CMD)

# Install dependencies
pip install -r requirements.txt

# Download AI models (ONE-TIME, requires internet)
# This downloads: Whisper, M2M100, Piper binary, and voice models (~3-4 GB)
python download_models.py
```

**What `download_models.py` does:**
- Downloads Whisper STT model (base)
- Downloads M2M100 translation model (418M parameters)
- Auto-downloads Piper TTS binary from GitHub
- Downloads 5 language voice models from HuggingFace
- Total size: ~3-4 GB (one-time download)

### 3. Frontend Setup

```bash
cd ../frontend

# Install Node.js dependencies
npm install
```

### 4. Run the Application

**Terminal 1 - Backend:**
```bash
cd backend
venv\Scripts\Activate.ps1
python main.py
```
Backend will start on `http://localhost:8000`

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```
Frontend will open automatically at `http://localhost:3000`

---

## 🎯 Usage

1. **Select Languages**: Choose source and target languages from the dropdowns.
2. **Record Audio**: Click "Start Recording" and speak into your microphone.
3. **Stop Recording**: Click "Stop Recording" when done.
4. **Translate**: Click "Translate & Speak" to process.
5. **Results**:
   - View original transcription (left card)
   - View translation (right card)
   - Translated audio auto-plays
   - Click 🔊 to replay audio
   - Click 📋 to copy text

---

## 📁 Project Structure

```
lt-audio-translator/
├── backend/
│   ├── main.py                    # FastAPI server with full pipeline
│   ├── download_models.py         # Auto-download script for all models
│   ├── requirements.txt           # Python dependencies
│   └── piper/                     # Piper TTS (auto-generated)
│       ├── piper.exe              # Piper binary (Windows)
│       ├── piper/                 # espeak-ng data & libraries
│       └── voices/                # ONNX voice models
│           ├── en_US-lessac-medium.onnx
│           ├── hi_IN-high.onnx
│           ├── fr_FR-siwis-medium.onnx
│           ├── es_ES-davefx-medium.onnx
│           └── de_DE-thorsten-medium.onnx
├── frontend/
│   ├── src/
│   │   ├── App.js                 # Main React component
│   │   └── App.css                # Styling
│   ├── package.json
│   └── public/
└── README.md
```

---

## 🔧 Technical Details

### Backend Pipeline (main.py)

1. **Model Loading** (on startup):
   - Whisper base model → CUDA/CPU
   - M2M100 418M model → CUDA/CPU
   - Piper voices (ONNX) → mapped by language

2. **Request Processing** (`/api/translate-audio`):
   ```
   Audio Upload → STT (Whisper) → Translation (M2M100) → TTS (Piper) → Audio Response
   ```

3. **Piper TTS Integration**:
   - Uses subprocess to run `piper.exe`
   - Pipes text via stdin (UTF-8)
   - Outputs WAV file
   - Returns base64-encoded audio

### Frontend (App.js)

- **MediaRecorder API**: Captures microphone input as WAV
- **Axios POST**: Sends audio + language params to backend
- **Audio Playback**: Converts base64 → Blob → Audio object
- **Auto-play**: Plays translated audio automatically
- **State Management**: React hooks for recording/processing states

### Performance

| Operation | Time (CPU) | Time (GPU) |
| :--- | :---: | :---: |
| Whisper STT (base) | ~5-10s | ~2-4s |
| M2M100 Translation | ~1-2s | ~0.5s |
| Piper TTS | ~1-3s | ~1-3s |
| **Total Pipeline** | **~7-15s** | **~4-8s** |

*Tested on: Intel i7-10700, NVIDIA GTX 1660 Ti, 16GB RAM*

---

## 🔒 Security & Privacy Features

✅ **100% Offline** - No internet required after setup  
✅ **No API Keys** - All models run locally  
✅ **No Data Transmission** - Audio never leaves the device  
✅ **No Telemetry** - No usage tracking or analytics  
✅ **Local Storage Only** - Temporary files are auto-deleted  
✅ **Open Source** - Full transparency of the codebase  

**Suitable for:**
- Military / Defense communications
- Secure government operations
- Healthcare (HIPAA compliance)
- Legal / confidential discussions
- Air-gapped environments

---

## 🐛 Troubleshooting

### Backend won't start

**Error:** `ModuleNotFoundError: No module named 'whisper'`
- **Solution:** Activate virtual environment and run `pip install -r requirements.txt`

**Error:** `Piper binary not found`
- **Solution:** Run `python download_models.py` to download Piper

**Error:** `No TTS voices available`
- **Solution:** Re-run `python download_models.py` to download voice models

### Frontend issues

**Error:** `Cannot connect to backend`
- **Solution:** Ensure backend is running on port 8000
- Check: `http://localhost:8000/` should show service info

**Error:** `Microphone access denied`
- **Solution:** Grant browser permission to access microphone
- Chrome: Click lock icon → Site settings → Microphone → Allow

### Audio issues

**Error:** `ffmpeg not found`
- **Solution:** Install FFmpeg and add to PATH
- Windows: `winget install ffmpeg`

**Error:** `Generated audio file is empty`
- **Solution:** Check Piper logs in backend terminal
- Verify voice model exists in `backend/piper/voices/`

### Performance issues

**Slow processing (>30s)**
- Enable GPU acceleration (install CUDA-enabled PyTorch)
- Use smaller Whisper model (base is default)
- Close other applications to free RAM

---

## 🚀 Advanced Configuration

### Change Whisper Model

Edit [main.py](backend/main.py#L45):
```python
self.whisper_model = whisper.load_model("base")  # Options: tiny, base, small, medium, large
```

**Trade-offs:**
- `tiny` - Fastest, lowest accuracy (~1GB RAM)
- `base` - **Default**, good balance (~2GB RAM)
- `small` - Better accuracy (~5GB RAM)
- `medium` - High accuracy, slow (~10GB RAM)

### Add More Languages

1. **Download voice model** from [Piper Voices](https://github.com/rhasspy/piper/blob/master/VOICES.md)
2. **Add to** `download_models.py` VOICE_MODELS dict
3. **Update** `main.py` voice_mapping and LANG_MAP
4. **Update** `frontend/src/App.js` languages array

### Enable GPU Acceleration

```bash
# Uninstall CPU-only PyTorch
pip uninstall torch torchaudio

# Install CUDA version (requires NVIDIA GPU + CUDA Toolkit)
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118
```

---

## 📊 System Requirements

### Minimum (CPU-only)

- **CPU:** Intel i5 / AMD Ryzen 5 (4 cores)
- **RAM:** 8 GB
- **Storage:** 10 GB free space
- **OS:** Windows 10/11, Linux, macOS

### Recommended (GPU-accelerated)

- **CPU:** Intel i7 / AMD Ryzen 7
- **GPU:** NVIDIA GTX 1660 or better (6GB VRAM)
- **RAM:** 16 GB
- **Storage:** 15 GB free space (SSD preferred)
- **OS:** Windows 10/11 with CUDA 11.8+

---

## 📝 API Reference

### GET `/`
Returns service status and loaded models.

**Response:**
```json
{
  "service": "L&T Audio Translator",
  "status": "🔒 100% Offline",
  "mode": "STT + Translation + TTS",
  "models": {
    "stt": "Whisper ✅",
    "translation": "M2M100 ✅",
    "tts": "Piper ✅ (5 voices)",
    "piper_binary": true
  },
  "available_voices": ["english", "hindi", "french", "spanish", "german"]
}
```

### POST `/api/translate-audio`
Process audio through full pipeline.

**Request:**
- `audio` (file): Audio file (WAV/MP3)
- `source_lang` (form): Source language code (e.g., "english")
- `target_lang` (form): Target language code (e.g., "hindi")

**Response:**
```json
{
  "success": true,
  "transcribed_text": "Hello world",
  "translated_text": "नमस्ते दुनिया",
  "source_language": "english",
  "target_language": "hindi",
  "audio_file": "UklGRiQAAABXQVZFZm10...",
  "audio_format": "wav"
}
```

### GET `/api/languages`
Get supported languages.

**Response:**
```json
{
  "languages": [
    {"code": "english", "name": "English"},
    {"code": "hindi", "name": "Hindi"},
    {"code": "french", "name": "French"},
    {"code": "spanish", "name": "Spanish"},
    {"code": "german", "name": "German"}
  ]
}
```

---

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- [ ] Add more language support
- [ ] Implement streaming audio (real-time translation)
- [ ] Add speaker diarization (multi-speaker detection)
- [ ] Optimize Piper TTS performance
- [ ] Create Docker deployment
- [ ] Add batch processing mode
- [ ] Implement conversation history

---

## 📄 License

This project is licensed under the MIT License.

### Third-Party Components

- **Whisper** - MIT License (OpenAI)
- **M2M100** - MIT License (Meta/HuggingFace)
- **Piper** - MIT License (Rhasspy)
- **FastAPI** - MIT License
- **React** - MIT License

---

## 🙏 Acknowledgments

- **OpenAI** for Whisper STT
- **Meta AI** for M2M100 translation
- **Rhasspy** for Piper TTS
- **HuggingFace** for model hosting
- **FastAPI** for the excellent web framework

---

## 📞 Support

For issues, questions, or feature requests:

1. Check the [Troubleshooting](#-troubleshooting) section
2. Open an issue on GitHub
3. Review logs in backend terminal for detailed errors

---

**🔒 Built for Security. Optimized for Privacy. Designed for Offline Use.**
