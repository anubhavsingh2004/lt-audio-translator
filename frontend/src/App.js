import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { FaMicrophone, FaStop, FaExchangeAlt, FaVolumeUp, FaCopy } from 'react-icons/fa';
import './App.css';

const API_URL = 'http://localhost:8000';

function App() {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [sourceLang, setSourceLang] = useState('english');
  const [targetLang, setTargetLang] = useState('hindi');
  const [transcribed, setTranscribed] = useState('');
  const [translated, setTranslated] = useState('');
  const [languages, setLanguages] = useState([]);
  const [audioBlob, setAudioBlob] = useState(null);
  const [translatedAudioBlob, setTranslatedAudioBlob] = useState(null); // TTS audio
  const [status, setStatus] = useState('');
  const [isPlayingTranslation, setIsPlayingTranslation] = useState(false);
  
  const mediaRecorder = useRef(null);
  const audioChunks = useRef([]);
  const translationAudioRef = useRef(null); // Audio player ref

  useEffect(() => {
    axios.get(`${API_URL}/api/languages`)
      .then(res => setLanguages(res.data.languages))
      .catch(err => console.error('Error fetching languages:', err));
  }, []);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder.current = new MediaRecorder(stream);
      audioChunks.current = [];

      mediaRecorder.current.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunks.current.push(e.data);
      };

      mediaRecorder.current.onstop = () => {
        const blob = new Blob(audioChunks.current, { type: 'audio/wav' });
        setAudioBlob(blob);
        stream.getTracks().forEach(t => t.stop());
      };

      mediaRecorder.current.start();
      setIsRecording(true);
      setTranscribed('');
      setTranslated('');
      setTranslatedAudioBlob(null); // Clear previous TTS audio
      setStatus('');
    } catch (err) {
      alert('Microphone access denied!');
      console.error(err);
    }
  };

  const stopRecording = () => {
    if (mediaRecorder.current && isRecording) {
      mediaRecorder.current.stop();
      setIsRecording(false);
    }
  };

  const translateAudio = async () => {
    if (!audioBlob) {
      alert('Record audio first!');
      return;
    }

    setIsProcessing(true);
    setStatus('Processing... (STT → Translation → TTS)');

    const formData = new FormData();
    formData.append('audio', audioBlob, 'audio.wav');
    formData.append('source_lang', sourceLang);
    formData.append('target_lang', targetLang);

    try {
      const res = await axios.post(`${API_URL}/api/translate-audio`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 180000
      });

      setTranscribed(res.data.transcribed_text);
      setTranslated(res.data.translated_text);
      
      // Convert base64 audio to Blob for playback
      if (res.data.audio_file) {
        const audioBlob = base64ToBlob(res.data.audio_file, 'audio/wav');
        setTranslatedAudioBlob(audioBlob);
        
        // Auto-play translated audio
        setTimeout(() => playTranslation(audioBlob), 500);
      }
      
      setStatus('');
      setAudioBlob(null); // Reset input audio
    } catch (err) {
      alert(`Error: ${err.response?.data?.detail || err.message}`);
      setStatus('');
      console.error(err);
    } finally {
      setIsProcessing(false);
    }
  };

  // Convert base64 to Blob
  const base64ToBlob = (base64, contentType) => {
    const byteCharacters = atob(base64);
    const byteArrays = [];
    
    for (let i = 0; i < byteCharacters.length; i++) {
      byteArrays.push(byteCharacters.charCodeAt(i));
    }
    
    const byteArray = new Uint8Array(byteArrays);
    return new Blob([byteArray], { type: contentType });
  };

  // Play translated audio
  const playTranslation = (audioBlob = translatedAudioBlob) => {
    if (!audioBlob) {
      alert('No audio available to play!');
      return;
    }

    // Stop any currently playing audio
    if (translationAudioRef.current) {
      translationAudioRef.current.pause();
      translationAudioRef.current.currentTime = 0;
    }

    const audioUrl = URL.createObjectURL(audioBlob);
    const audio = new Audio(audioUrl);
    translationAudioRef.current = audio;

    audio.onplay = () => setIsPlayingTranslation(true);
    audio.onended = () => {
      setIsPlayingTranslation(false);
      URL.revokeObjectURL(audioUrl); // Cleanup
    };
    audio.onerror = () => {
      setIsPlayingTranslation(false);
      alert('Error playing audio');
    };

    audio.play().catch(err => {
      console.error('Audio playback error:', err);
      alert('Could not play audio');
    });
  };

  const swapLanguages = () => {
    const temp = sourceLang;
    setSourceLang(targetLang);
    setTargetLang(temp);
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    alert('Copied to clipboard!');
  };

  return (
    <div className="App">
      <div className="main-container">
        <h1 className="title">🔒 Military Audio Translator</h1>
        <p className="subtitle">Secure Offline Translation System</p>

        {/* Language Selector Bar */}
        <div className="language-bar">
          <select 
            className="lang-dropdown"
            value={sourceLang} 
            onChange={e => setSourceLang(e.target.value)} 
            disabled={isProcessing || isRecording}
          >
            {languages.map(l => (
              <option key={l.code} value={l.code}>{l.name}</option>
            ))}
          </select>

          <button 
            className="swap-icon-btn" 
            onClick={swapLanguages}
            disabled={isProcessing || isRecording}
          >
            <FaExchangeAlt />
          </button>

          <select 
            className="lang-dropdown"
            value={targetLang} 
            onChange={e => setTargetLang(e.target.value)} 
            disabled={isProcessing || isRecording}
          >
            {languages.map(l => (
              <option key={l.code} value={l.code}>{l.name}</option>
            ))}
          </select>
        </div>

        {/* Recording Button */}
        <div className="record-section">
          {!isRecording && !audioBlob && (
            <button 
              className="record-btn" 
              onClick={startRecording}
              disabled={isProcessing}
            >
              <FaMicrophone size={24} />
              <span>Start Recording</span>
            </button>
          )}

          {isRecording && (
            <button 
              className="record-btn recording" 
              onClick={stopRecording}
            >
              <FaStop size={24} />
              <span>Stop Recording</span>
            </button>
          )}

          {audioBlob && !isRecording && !isProcessing && (
            <button 
              className="translate-btn" 
              onClick={translateAudio}
            >
              Translate & Speak
            </button>
          )}

          {isProcessing && (
            <div className="processing-indicator">
              <div className="spinner"></div>
              <span>{status}</span>
            </div>
          )}
        </div>

        {/* Results Section */}
        {(transcribed || translated) && (
          <div className="results-grid">
            <div className="result-card">
              <div className="card-header">
                <h3>Transcript ({sourceLang})</h3>
                <div className="card-actions">
                  <button className="icon-btn" title="TTS not available for source" disabled>
                    <FaVolumeUp />
                  </button>
                  <button className="icon-btn" onClick={() => copyToClipboard(transcribed)}>
                    <FaCopy />
                  </button>
                </div>
              </div>
              <p className="card-content">{transcribed}</p>
              <div className="verified-badge">✓</div>
            </div>

            <div className="result-card">
              <div className="card-header">
                <h3>Translation ({targetLang})</h3>
                <div className="card-actions">
                  <button 
                    className={`icon-btn ${isPlayingTranslation ? 'playing' : ''}`}
                    onClick={() => playTranslation()}
                    disabled={!translatedAudioBlob}
                    title="Play translated audio"
                  >
                    <FaVolumeUp />
                  </button>
                  <button className="icon-btn" onClick={() => copyToClipboard(translated)}>
                    <FaCopy />
                  </button>
                </div>
              </div>
              <p className="card-content">{translated}</p>
              {translatedAudioBlob && (
                <div className="audio-badge">🔊 Audio ready</div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
