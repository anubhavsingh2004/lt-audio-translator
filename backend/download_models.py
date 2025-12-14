"""
Download AI models for offline use (WITHOUT TTS)
Run this ONCE with internet connection
"""
import whisper
from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer

print("=" * 60)
print("Downloading AI Models for Offline Use")
print("=" * 60)

print("\n[1/2] Downloading Whisper STT model (base)...")
whisper.load_model("base")
print("✅ Whisper downloaded!")

print("\n[2/2] Downloading M2M100 Translation model (418M)...")
M2M100Tokenizer.from_pretrained("facebook/m2m100_418M")
M2M100ForConditionalGeneration.from_pretrained("facebook/m2m100_418M")
print("✅ M2M100 downloaded!")

print("\n" + "=" * 60)
print("✅ MODELS DOWNLOADED - System ready for offline STT + Translation!")
print("⚠️  Note: TTS (speech output) disabled - install later")
print("=" * 60)
