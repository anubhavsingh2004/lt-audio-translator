"""
Quick test script to verify Piper TTS is working
Run this after installing dependencies
"""
import os
import sys

def check_piper_setup():
    """Verify Piper TTS installation"""
    print("=" * 60)
    print("🔍 Checking Piper TTS Setup")
    print("=" * 60)
    
    piper_dir = os.path.join(os.path.dirname(__file__), "piper")
    piper_exe = os.path.join(piper_dir, "piper.exe")
    voices_dir = os.path.join(piper_dir, "voices")
    
    # Check Piper binary
    print("\n[1/3] Checking Piper binary...")
    if os.path.exists(piper_exe):
        size_mb = os.path.getsize(piper_exe) / (1024 * 1024)
        print(f"  ✅ piper.exe found ({size_mb:.1f} MB)")
    else:
        print(f"  ❌ piper.exe NOT found at: {piper_exe}")
        print("     Run: python download_models.py")
        return False
    
    # Check voices directory
    print("\n[2/3] Checking voice models...")
    if not os.path.exists(voices_dir):
        print(f"  ❌ Voices directory not found: {voices_dir}")
        print("     Run: python download_models.py")
        return False
    
    voice_files = [f for f in os.listdir(voices_dir) if f.endswith('.onnx')]
    if voice_files:
        print(f"  ✅ Found {len(voice_files)} voice models:")
        for voice in voice_files:
            size_mb = os.path.getsize(os.path.join(voices_dir, voice)) / (1024 * 1024)
            print(f"     - {voice} ({size_mb:.1f} MB)")
    else:
        print("  ❌ No voice models (.onnx) found")
        print("     Run: python download_models.py")
        return False
    
    # Check espeak-ng data
    print("\n[3/3] Checking espeak-ng data...")
    espeak_dir = os.path.join(piper_dir, "piper", "espeak-ng-data")
    if os.path.exists(espeak_dir):
        print(f"  ✅ espeak-ng data found")
    else:
        print(f"  ❌ espeak-ng data not found: {espeak_dir}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ Piper TTS setup is complete!")
    print("=" * 60)
    print("\n🚀 Ready to run:")
    print("   python main.py")
    print("\nThen open: http://localhost:8000")
    return True

def test_piper_tts():
    """Test Piper TTS generation"""
    print("\n" + "=" * 60)
    print("🧪 Testing Piper TTS (Optional)")
    print("=" * 60)
    
    piper_dir = os.path.join(os.path.dirname(__file__), "piper")
    piper_exe = os.path.join(piper_dir, "piper.exe")
    voices_dir = os.path.join(piper_dir, "voices")
    
    # Find an English voice
    voice_file = None
    for f in os.listdir(voices_dir):
        if f.startswith("en_") and f.endswith(".onnx"):
            voice_file = os.path.join(voices_dir, f)
            break
    
    if not voice_file:
        print("  ⚠️ No English voice found for testing")
        return
    
    print(f"\n  Using voice: {os.path.basename(voice_file)}")
    print("  Testing with: 'Hello, this is a test.'")
    
    import subprocess
    import tempfile
    
    try:
        # Create temp output file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_output:
            output_path = temp_output.name
        
        # Run Piper
        cmd = [
            piper_exe,
            "--model", voice_file,
            "--output_file", output_path
        ]
        
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=piper_dir
        )
        
        test_text = "Hello, this is a test of the Piper text to speech system."
        stdout, stderr = process.communicate(input=test_text.encode('utf-8'), timeout=10)
        
        if process.returncode == 0 and os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            if file_size > 0:
                print(f"  ✅ Generated {file_size} bytes ({file_size/1024:.1f} KB) of audio")
                print(f"  📁 Test file: {output_path}")
                print("  🔊 Play this file to verify audio quality")
            else:
                print("  ❌ Generated file is empty")
        else:
            print(f"  ❌ Piper failed with exit code {process.returncode}")
            if stderr:
                print(f"  Error: {stderr.decode('utf-8', errors='ignore')}")
        
        # Cleanup
        if os.path.exists(output_path):
            os.unlink(output_path)
    
    except subprocess.TimeoutExpired:
        print("  ❌ Test timed out (>10s)")
    except Exception as e:
        print(f"  ❌ Test failed: {str(e)}")

if __name__ == "__main__":
    print("\n🔧 L&T Audio Translator - Piper TTS Verification\n")
    
    if check_piper_setup():
        # Ask if user wants to test TTS
        try:
            response = input("\n🧪 Run TTS test? (y/n): ").strip().lower()
            if response == 'y':
                test_piper_tts()
        except KeyboardInterrupt:
            print("\n\n✅ Setup check complete!")
    else:
        print("\n❌ Setup incomplete. Please run:")
        print("   python download_models.py")
        sys.exit(1)
