from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import whisper
from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer
import torch
import tempfile
import os
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI(title="L&T Audio Translator (No TTS)")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ModelManager:
    def __init__(self):
        self.whisper_model = None
        self.m2m_model = None
        self.m2m_tokenizer = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"🔧 Using device: {self.device}")
    
    def load_models(self):
        logger.info("📥 Loading Whisper STT...")
        self.whisper_model = whisper.load_model("base", device=self.device)
        
        logger.info("📥 Loading M2M100 Translation...")
        self.m2m_tokenizer = M2M100Tokenizer.from_pretrained("facebook/m2m100_418M")
        self.m2m_model = M2M100ForConditionalGeneration.from_pretrained("facebook/m2m100_418M").to(self.device)
        
        logger.info("✅ Models loaded (TTS disabled)")


model_manager = ModelManager()


LANG_MAP = {
    "english": "en", "hindi": "hi", "french": "fr", 
    "spanish": "es", "german": "de", "arabic": "ar",
    "russian": "ru", "chinese": "zh"
}


@app.on_event("startup")
async def startup():
    model_manager.load_models()


@app.get("/")
async def root():
    return {
        "service": "L&T Audio Translator",
        "status": "🔒 100% Offline",
        "mode": "STT + Translation (TTS disabled)",
        "models": {
            "stt": "Whisper ✅",
            "translation": "M2M100 ✅",
            "tts": "Disabled ⚠️ (Install Visual C++ Build Tools + TTS later)"
        }
    }


@app.post("/api/translate-audio")
async def translate_audio(
    audio: UploadFile = File(...),
    source_lang: str = Form(...),
    target_lang: str = Form(...)
):
    """
    Pipeline: Audio → STT → Translation (No TTS output)
    """
    temp_input_path = None
    
    try:
        # Create temp file and get path
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav", mode='wb')
        temp_input_path = temp_file.name
        
        # Write audio content
        content = await audio.read()
        temp_file.write(content)
        temp_file.close()  # IMPORTANT: Close before Whisper reads it
        
        logger.info(f"🎤 Processing: {source_lang} → {target_lang}")
        logger.info(f"📁 Temp file: {temp_input_path}")
        
        # Verify file exists and has content
        if not os.path.exists(temp_input_path):
            raise HTTPException(status_code=500, detail="Failed to save audio file")
        
        file_size = os.path.getsize(temp_input_path)
        logger.info(f"📊 Audio file size: {file_size} bytes")
        
        if file_size == 0:
            raise HTTPException(status_code=400, detail="Received empty audio file")
        
        # Step 1: STT
        logger.info("Step 1/2: Transcribing with Whisper...")
        src_code = LANG_MAP.get(source_lang.lower(), "en")
        
        result = model_manager.whisper_model.transcribe(
            temp_input_path,
            language=src_code,
            task="transcribe",
            fp16=False  # Force CPU compatibility
        )
        transcribed = result["text"].strip()
        logger.info(f"📝 Transcribed: {transcribed}")
        
        if not transcribed:
            raise HTTPException(status_code=400, detail="No speech detected in audio")
        
        # Step 2: Translation
        logger.info("Step 2/2: Translating with M2M100...")
        tgt_code = LANG_MAP.get(target_lang.lower(), "fr")
        
        model_manager.m2m_tokenizer.src_lang = src_code
        encoded = model_manager.m2m_tokenizer(transcribed, return_tensors="pt").to(model_manager.device)
        
        generated = model_manager.m2m_model.generate(
            **encoded,
            forced_bos_token_id=model_manager.m2m_tokenizer.get_lang_id(tgt_code),
            max_length=512
        )
        
        translated = model_manager.m2m_tokenizer.batch_decode(generated, skip_special_tokens=True)[0]
        logger.info(f"🌍 Translated: {translated}")
        
        logger.info("✅ Translation complete!")
        
        return {
            "success": True,
            "transcribed_text": transcribed,
            "translated_text": translated,
            "source_language": source_lang,
            "target_language": target_lang,
            "audio_file": None,  # TTS disabled
            "note": "Speech output disabled. Install TTS to enable audio output."
        }
    
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")
    finally:
        # Cleanup temp file
        if temp_input_path and os.path.exists(temp_input_path):
            try:
                os.unlink(temp_input_path)
                logger.info("🗑️ Temp file cleaned up")
            except Exception as e:
                logger.warning(f"⚠️ Failed to delete temp file: {e}")


@app.get("/api/languages")
async def languages():
    return {
        "languages": [
            {"code": "english", "name": "English"},
            {"code": "hindi", "name": "Hindi"},
            {"code": "french", "name": "French"},
            {"code": "spanish", "name": "Spanish"},
            {"code": "german", "name": "German"},
            {"code": "arabic", "name": "Arabic"},
            {"code": "russian", "name": "Russian"},
            {"code": "chinese", "name": "Chinese"}
        ]
    }


@app.post("/api/transcribe-only")
async def transcribe_only(
    audio: UploadFile = File(...),
    language: str = Form(...)
):
    """STT only endpoint"""
    temp_file_path = None
    
    try:
        # Create and write temp file properly
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav", mode='wb')
        temp_file_path = temp_file.name
        
        content = await audio.read()
        temp_file.write(content)
        temp_file.close()
        
        result = model_manager.whisper_model.transcribe(
            temp_file_path,
            language=LANG_MAP.get(language.lower(), language),
            fp16=False
        )
        
        return {
            "text": result["text"],
            "language": language
        }
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except Exception as e:
                logger.warning(f"Failed to delete temp file: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
