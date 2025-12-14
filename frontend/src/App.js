import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { FaMicrophone, FaStop, FaExchangeAlt, FaShieldAlt } from 'react-icons/fa';
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
  const [status, setStatus] = useState('');
  const [note, setNote] = useState('');
  
  const mediaRecorder = useRef(null);
  const audioChunks = useRef([]);

  useEffect(() => {
    // Fetch supported languages on load
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
      setNote('');
      setStatus('🎤 Recording...');
    } catch (err) {
      alert('Microphone access denied!');
      console.error(err);
    }
  };

  const stopRecording = () => {
    if (mediaRecorder.current && isRecording) {
      mediaRecorder.current.stop();
      setIsRecording(false);
      setStatus('✅ Recording stopped');
    }
  };

  const translateAudio = async () => {
    if (!audioBlob) {
      alert('Record audio first!');
      return;
    }

    setIsProcessing(true);
    setStatus('⏳ Processing...');

    const formData = new FormData();
    formData.append('audio', audioBlob, 'audio.wav');
    formData.append('source_lang', sourceLang);
    formData.append('target_lang', targetLang);

    try {
      setStatus('🎤 Transcribing with Whisper...');
      
      const res = await axios.post(`${API_URL}/api/translate-audio`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 180000 // 3 minutes
      });

      setTranscribed(res.data.transcribed_text);
      setTranslated(res.data.translated_text);
      setNote(res.data.note || '');
      setStatus('✅ Translation complete!');
    } catch (err) {
      alert(`Error: ${err.response?.data?.detail || err.message}`);
      setStatus('❌ Translation failed');
      console.error(err);
    } finally {
      setIsProcessing(false);
    }
  };

  const swapLanguages = () => {
    const temp = sourceLang;
    setSourceLang(targetLang);
    setTargetLang(temp);
  };

  return (
    <div className="App">
      <header>
        <FaShieldAlt size={50} color="#00d9ff" />
        <h1>L&T Live Audio Translator</h1>
        <p className="subtitle">🔒 100% Offline • Military-Grade Security</p>
        <div className="badges">
          <span className="badge">Whisper STT ✅</span>
          <span className="badge">M2M100 Translation ✅</span>
          <span className="badge-disabled">TTS ⚠️ (Disabled)</span>
        </div>
      </header>

      <div className="container">
        {/* Language Selector */}
        <div className="lang-selector">
          <div className="lang-box">
            <label>Source Language</label>
            <select 
              value={sourceLang} 
              onChange={e => setSourceLang(e.target.value)} 
              disabled={isProcessing || isRecording}
            >
              {languages.map(l => (
                <option key={l.code} value={l.code}>{l.name}</option>
              ))}
            </select>
          </div>

          <button 
            className="swap-btn" 
            onClick={swapLanguages}
            disabled={isProcessing || isRecording}
          >
            <FaExchangeAlt />
          </button>

          <div className="lang-box">
            <label>Target Language</label>
            <select 
              value={targetLang} 
              onChange={e => setTargetLang(e.target.value)} 
              disabled={isProcessing || isRecording}
            >
              {languages.map(l => (
                <option key={l.code} value={l.code}>{l.name}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Status Display */}
        {status && (
          <div className="status-bar">
            {status}
          </div>
        )}

        {/* Recording Controls */}
        <div className="controls">
          {!isRecording ? (
            <button 
              className="btn-record" 
              onClick={startRecording} 
              disabled={isProcessing}
            >
              <FaMicrophone size={20} />
              <span>Start Recording</span>
            </button>
          ) : (
            <button 
              className="btn-stop" 
              onClick={stopRecording}
            >
              <FaStop size={20} />
              <span>Stop Recording</span>
            </button>
          )}

          {audioBlob && !isRecording && (
            <button 
              className="btn-translate" 
              onClick={translateAudio} 
              disabled={isProcessing}
            >
              {isProcessing ? '⏳ Processing...' : '🌐 Translate'}
            </button>
          )}
        </div>

        {/* Results */}
        {transcribed && (
          <div className="results">
            <div className="result-box">
              <h3>📝 Original Text ({sourceLang})</h3>
              <p>{transcribed}</p>
            </div>

            <div className="result-box success">
              <h3>🌐 Translated Text ({targetLang})</h3>
              <p>{translated}</p>
            </div>

            {note && (
              <div className="note-box">
                <p>⚠️ {note}</p>
              </div>
            )}
          </div>
        )}
      </div>

      <footer>
        <p>⚠️ Offline System • No Internet • No Cloud • No Data Transmission</p>
        <p className="small">TTS disabled - Install Visual C++ Build Tools + TTS library to enable speech output</p>
      </footer>
    </div>
  );
}

export default App;
