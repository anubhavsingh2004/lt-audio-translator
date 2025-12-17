from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import whisper
from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer
import torch
import tempfile
import os
import logging
import subprocess
import base64
from glossary import get_glossary

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="L&T Audio Translator with Piper TTS")

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
        
        # Piper paths
        self.piper_dir = os.path.join(os.path.dirname(__file__), "piper")
        self.piper_exe = os.path.join(self.piper_dir, "piper.exe")
        self.voices_dir = os.path.join(self.piper_dir, "voices")
        self.piper_voices = {}
        
        logger.info(f"🔧 Using device: {self.device}")
    
    def load_models(self):
        logger.info("📥 Loading Whisper STT...")
        # Use "medium" model for excellent multilingual support (Hindi, French, etc.)
        # Options: tiny, base, small, medium, large
        # medium = best balance for production Hindi transcription
        self.whisper_model = whisper.load_model("medium", device=self.device)
        
        logger.info("📥 Loading M2M100 Translation...")
        self.m2m_tokenizer = M2M100Tokenizer.from_pretrained("facebook/m2m100_418M")
        self.m2m_model = M2M100ForConditionalGeneration.from_pretrained("facebook/m2m100_418M").to(self.device)
        
        logger.info("📥 Loading Piper TTS...")
        self._load_piper_voices()
        
        logger.info("✅ All models loaded successfully!")
    
    def _load_piper_voices(self):
        """Map voice files for each language"""
        if not os.path.exists(self.piper_exe):
            logger.error(f"❌ Piper binary not found at: {self.piper_exe}")
            logger.error("   Run: python download_models.py")
            return
        
        voice_mapping = {
            "english": "en_US-lessac-medium.onnx",
            "hindi": "hi_IN-pratham-medium.onnx",  # Hindi voice (Pratham speaker)
            "french": "fr_FR-siwis-medium.onnx",
            "spanish": "es_ES-davefx-medium.onnx",
            "german": "de_DE-thorsten-medium.onnx"
        }
        
        for lang, filename in voice_mapping.items():
            voice_path = os.path.join(self.voices_dir, filename)
            if os.path.exists(voice_path):
                self.piper_voices[lang] = voice_path
                logger.info(f"  ✅ {lang.capitalize()} voice loaded")
            else:
                logger.warning(f"  ⚠️  {lang.capitalize()} voice not found")
        
        if not self.piper_voices:
            logger.error("❌ No Piper voices found! Run download_models.py")
    
    def generate_speech(self, text, language):
        """Generate speech using Piper binary"""
        voice_path = self.piper_voices.get(language.lower())
        
        if not voice_path:
            logger.warning(f"Voice for {language} not available, using English")
            voice_path = self.piper_voices.get("english")
        
        if not voice_path:
            raise Exception("No TTS voices available")
        
        # Create temp output file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_output:
            output_path = temp_output.name
        
        try:
            # Path to espeak-ng data
            espeak_data_path = os.path.join(self.piper_dir, "piper", "espeak-ng-data")
            
            # Command to run Piper
            cmd = [
                self.piper_exe,
                "--model", voice_path,
                "--output_file", output_path,
                "--espeak_data", espeak_data_path
            ]
            
            logger.info(f"🔊 TTS Command: {' '.join(cmd)}")
            logger.info(f"📝 Text to speak: {text}")
            
            # Run Piper and pipe text via stdin
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.piper_dir,  # Important: run in piper directory
                shell=False
            )
            
            # Send text via stdin (Piper expects UTF-8)
            stdout, stderr = process.communicate(input=text.encode('utf-8'), timeout=30)
            
            # Log output for debugging
            if stdout:
                logger.info(f"Piper stdout: {stdout.decode('utf-8', errors='ignore').strip()}")
            if stderr:
                stderr_text = stderr.decode('utf-8', errors='ignore').strip()
                if stderr_text:
                    logger.info(f"Piper stderr: {stderr_text}")
            
            # Check return code
            if process.returncode != 0:
                raise Exception(f"Piper failed with exit code {process.returncode}")
            
            # Verify output file exists and has content
            if not os.path.exists(output_path):
                raise Exception(f"Output file not created: {output_path}")
            
            file_size = os.path.getsize(output_path)
            if file_size == 0:
                raise Exception("Generated audio file is empty")
            
            # Read the generated audio
            with open(output_path, "rb") as f:
                audio_data = f.read()
            
            logger.info(f"✅ Generated {len(audio_data)} bytes ({file_size/1024:.1f} KB) of audio")
            return audio_data
            
        except subprocess.TimeoutExpired:
            process.kill()
            raise Exception("TTS generation timed out (>30s)")
        except Exception as e:
            logger.error(f"❌ TTS generation failed: {str(e)}")
            raise
        finally:
            # Cleanup temp file
            if os.path.exists(output_path):
                try:
                    os.unlink(output_path)
                    logger.info("🗑️ Cleaned up temp audio file")
                except Exception as e:
                    logger.warning(f"⚠️ Could not delete temp file: {e}")

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
        "mode": "STT + Translation + TTS",
        "models": {
            "stt": "Whisper ✅",
            "translation": "M2M100 ✅",
            "tts": f"Piper ✅ ({len(model_manager.piper_voices)} voices)",
            "piper_binary": os.path.exists(model_manager.piper_exe)
        },
        "available_voices": list(model_manager.piper_voices.keys())
    }

@app.post("/api/translate-audio")
async def translate_audio(
    audio: UploadFile = File(...),
    source_lang: str = Form(...),
    target_lang: str = Form(...)
):
    """
    Full Pipeline: Audio → STT → Translation (with ALWAYS-ON defense glossary) → TTS
    
    Defense glossary is ALWAYS enabled for military communication.
    """
    temp_input_path = None
    
    try:
        # Save uploaded audio
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav", mode='wb')
        temp_input_path = temp_file.name
        content = await audio.read()
        temp_file.write(content)
        temp_file.close()
        
        logger.info(f"🎤 Processing [MILITARY MODE]: {source_lang} → {target_lang}")
        
        # Step 1: STT
        logger.info("Step 1/3: Transcribing with Whisper...")
        src_code = LANG_MAP.get(source_lang.lower(), "en")
        
        # Better transcription parameters for accuracy
        result = model_manager.whisper_model.transcribe(
            temp_input_path, 
            language=src_code, 
            task="transcribe", 
            fp16=False,
            beam_size=5,  # Better accuracy with beam search
            best_of=5,    # Consider multiple candidates
            temperature=0.0  # Deterministic output
        )
        transcribed = result["text"].strip()
        logger.info(f"📝 Transcribed: {transcribed}")
        
        if not transcribed:
            raise HTTPException(status_code=400, detail="No speech detected")
        
        # Step 2: Translation with ALWAYS-ON Defense Glossary
        logger.info("Step 2/3: Translating with M2M100 + Defense Glossary...")
        
        # ALWAYS protect military/technical terms
        glossary = get_glossary()
        protected_text, placeholder_map = glossary.protect_terms(
            transcribed,
            target_lang
        )
        
        if placeholder_map:
            logger.info(f"🔒 Protected {len(placeholder_map)} military terms with placeholders")
        
        # Translate (possibly with placeholders)
        tgt_code = LANG_MAP.get(target_lang.lower(), "fr")
        model_manager.m2m_tokenizer.src_lang = src_code
        encoded = model_manager.m2m_tokenizer(protected_text, return_tensors="pt").to(model_manager.device)
        
        # Use conservative generation parameters for military context
        generated = model_manager.m2m_model.generate(
            **encoded,
            forced_bos_token_id=model_manager.m2m_tokenizer.get_lang_id(tgt_code),
            max_new_tokens=256,
            num_beams=4,
            early_stopping=True,
            no_repeat_ngram_size=3
        )

        translated_raw = model_manager.m2m_tokenizer.batch_decode(generated, skip_special_tokens=True)[0]
        
        # Debug: Log the raw translation to see placeholder state
        logger.info(f"🔍 Raw translation (before restore): {translated_raw}")
        
        # ALWAYS restore protected military terms
        translated = glossary.restore_terms(translated_raw, placeholder_map)
        
        logger.info(f"🌍 Translated: {translated}")
        
        # Step 3: TTS
        logger.info("Step 3/3: Generating speech with Piper...")
        audio_data = model_manager.generate_speech(translated, target_lang)
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        
        logger.info("✅ Full pipeline complete!")
        
        return {
            "success": True,
            "transcribed_text": transcribed,
            "translated_text": translated,
            "source_language": source_lang,
            "target_language": target_lang,
            "audio_file": audio_base64,
            "audio_format": "wav"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")
    finally:
        if temp_input_path and os.path.exists(temp_input_path):
            try:
                os.unlink(temp_input_path)
            except:
                pass

@app.get("/api/languages")
async def languages():
    return {
        "languages": [
            {"code": "english", "name": "English"},
            {"code": "hindi", "name": "Hindi"},
            {"code": "french", "name": "French"},
            {"code": "spanish", "name": "Spanish"},
            {"code": "german", "name": "German"}
        ]
    }

@app.get("/api/glossary/stats")
async def glossary_stats():
    """Get defense glossary statistics (always-on system)"""
    glossary = get_glossary()
    stats = glossary.get_stats()
    return {
        "mode": "ALWAYS-ON (Military Communication)",
        "glossary_stats": stats
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)