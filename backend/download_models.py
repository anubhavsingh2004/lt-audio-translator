"""
Download AI models + Piper voices for offline use
Run this ONCE with internet connection
FULLY AUTOMATED - NO MANUAL STEPS!
"""
import whisper
from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer
import os
import urllib.request
import zipfile
import sys
import json

print("=" * 60)
print("Downloading AI Models for Offline Use")
print("=" * 60)

print("\n[1/4] Downloading Whisper STT model (base)...")
whisper.load_model("base")
print("✅ Whisper downloaded!")

print("\n[2/4] Downloading M2M100 Translation model (418M)...")
M2M100Tokenizer.from_pretrained("facebook/m2m100_418M")
M2M100ForConditionalGeneration.from_pretrained("facebook/m2m100_418M")
print("✅ M2M100 downloaded!")

print("\n[3/4] Downloading Piper TTS binary...")
piper_dir = os.path.join(os.path.dirname(__file__), "piper")
os.makedirs(piper_dir, exist_ok=True)

piper_exe = os.path.join(piper_dir, "piper.exe")

if not os.path.exists(piper_exe):
    print("  📥 Auto-detecting latest Piper release...")
    
    try:
        # Get latest release info from GitHub API
        api_url = "https://api.github.com/repos/rhasspy/piper/releases/latest"
        with urllib.request.urlopen(api_url) as response:
            release_data = json.loads(response.read().decode())
        
        # Find Windows AMD64 asset
        download_url = None
        for asset in release_data.get("assets", []):
            if "windows_amd64" in asset["name"] and asset["name"].endswith(".zip"):
                download_url = asset["browser_download_url"]
                file_size_mb = asset["size"] / (1024 * 1024)
                print(f"  ✅ Found: {asset['name']} ({file_size_mb:.1f} MB)")
                break
        
        if not download_url:
            raise Exception("Could not find Windows AMD64 release")
        
        # Download ZIP
        zip_path = os.path.join(piper_dir, "piper_temp.zip")
        print(f"  📥 Downloading from: {download_url}")
        print("     This may take 1-2 minutes...")
        
        def download_progress(block_num, block_size, total_size):
            downloaded = block_num * block_size
            percent = min(100, (downloaded / total_size) * 100)
            print(f"\r     Progress: {percent:.1f}%", end="", flush=True)
        
        urllib.request.urlretrieve(download_url, zip_path, reporthook=download_progress)
        print("\n  ✅ Download complete!")
        
        # Extract ZIP
        print("  📦 Extracting...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Extract all files
            zip_ref.extractall(piper_dir)
        
        # Remove ZIP
        os.remove(zip_path)
        
        # Find piper.exe in extracted files (might be in subdirectory)
        found = False
        for root, dirs, files in os.walk(piper_dir):
            if "piper.exe" in files:
                source = os.path.join(root, "piper.exe")
                if source != piper_exe:
                    # Move to correct location
                    import shutil
                    shutil.move(source, piper_exe)
                found = True
                break
        
        if not found or not os.path.exists(piper_exe):
            raise Exception(f"piper.exe not found after extraction")
        
        print("  ✅ Piper binary installed successfully!")
        
    except Exception as e:
        print(f"\n  ❌ Auto-download failed: {e}")
        print("\n  📥 MANUAL FALLBACK:")
        print("     1. Visit: https://github.com/rhasspy/piper/releases/latest")
        print("     2. Download: piper_windows_amd64.zip")
        print(f"     3. Extract piper.exe to: {piper_dir}")
        sys.exit(1)
else:
    print("  ✅ Piper binary already exists!")

print("\n[4/4] Downloading Piper TTS voice models...")

# Create voices directory
voices_dir = os.path.join(piper_dir, "voices")
os.makedirs(voices_dir, exist_ok=True)

# Voice models to download (these URLs are stable)
VOICE_MODELS = {
    "english": {
        "model": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx",
        "config": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json"
    },
    "hindi": {
        "model": "https://huggingface.co/rhasspy/piper-voices/resolve/main/hi/hi_IN/pratham/medium/hi_IN-pratham-medium.onnx",
        "config": "https://huggingface.co/rhasspy/piper-voices/resolve/main/hi/hi_IN/pratham/medium/hi_IN-pratham-medium.onnx.json"
    },
    "french": {
        "model": "https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/siwis/medium/fr_FR-siwis-medium.onnx",
        "config": "https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/siwis/medium/fr_FR-siwis-medium.onnx.json"
    },
    "spanish": {
        "model": "https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/davefx/medium/es_ES-davefx-medium.onnx",
        "config": "https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/davefx/medium/es_ES-davefx-medium.onnx.json"
    },
    "german": {
        "model": "https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/thorsten/medium/de_DE-thorsten-medium.onnx",
        "config": "https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/thorsten/medium/de_DE-thorsten-medium.onnx.json"
    }
}

def download_file(url, destination):
    """Download file with progress"""
    filename = os.path.basename(destination)
    print(f"    📥 {filename}...", end=" ", flush=True)
    try:
        urllib.request.urlretrieve(url, destination)
        file_size_mb = os.path.getsize(destination) / (1024 * 1024)
        print(f"✅ ({file_size_mb:.1f} MB)")
        return True
    except Exception as e:
        print(f"❌ {e}")
        return False

for lang, urls in VOICE_MODELS.items():
    print(f"\n  🎤 {lang.capitalize()} voice:")
    
    model_filename = urls["model"].split("/")[-1]
    config_filename = urls["config"].split("/")[-1]
    
    model_path = os.path.join(voices_dir, model_filename)
    config_path = os.path.join(voices_dir, config_filename)
    
    if not os.path.exists(model_path):
        download_file(urls["model"], model_path)
    else:
        print(f"    {model_filename} already exists ✅")
    
    if not os.path.exists(config_path):
        download_file(urls["config"], config_path)
    else:
        print(f"    {config_filename} already exists ✅")

print("\n" + "=" * 60)
print("✅ ALL MODELS DOWNLOADED!")
print("=" * 60)
print("Pipeline: Speech → Whisper STT → M2M100 → Piper TTS → Speech")
print(f"📁 Piper binary: {piper_exe}")
print(f"📁 Voice models: {voices_dir}")
print(f"📊 Total voices: {len(VOICE_MODELS)}")
print("=" * 60)
print("\n🚀 Ready to run: python main.py")
