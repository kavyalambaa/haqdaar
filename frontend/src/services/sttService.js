/**
 * HAQDAAR Multilingual Speech-to-Text (STT) Service
 * 
 * Architecture:
 * 1. Primary: Browser Web Speech API (Instant interim results, zero latency).
 * 2. Secondary Fallback: MediaRecorder Audio Capture -> Backend Gemini STT (/api/stt).
 * 3. Fail-Safe: Emits error states that trigger typed input focus.
 */

export const STT_STATES = {
  IDLE: 'IDLE',
  RECORDING: 'RECORDING',
  PROCESSING: 'PROCESSING',
  ERROR: 'ERROR'
};

export const STT_ERRORS = {
  PERMISSION_DENIED: 'PERMISSION_DENIED',
  NO_SPEECH: 'NO_SPEECH',
  NETWORK_ERROR: 'NETWORK_ERROR',
  AUDIO_CAPTURE: 'AUDIO_CAPTURE',
  UNSUPPORTED_LANGUAGE: 'UNSUPPORTED_LANGUAGE',
  UNSUPPORTED_BROWSER: 'UNSUPPORTED_BROWSER',
  BACKEND_ERROR: 'BACKEND_ERROR'
};

export const SUPPORTED_LANGUAGES = {
  hi: { code: 'hi', locale: 'hi-IN', name: 'Hindi' },
  mr: { code: 'mr', locale: 'mr-IN', name: 'Marathi' },
  ta: { code: 'ta', locale: 'ta-IN', name: 'Tamil' }
};

export class STTManager {
  constructor(options = {}) {
    this.apiBaseUrl = options.apiBaseUrl || 'https://haqdaar.onrender.com';
    this.state = STT_STATES.IDLE;
    this.currentLanguage = 'hi';
    
    // Callbacks
    this.onStateChange = options.onStateChange || (() => {});
    this.onInterimTranscript = options.onInterimTranscript || (() => {});
    this.onFinalTranscript = options.onFinalTranscript || (() => {});
    this.onError = options.onError || (() => {});

    // SpeechRecognition instance
    this.recognition = null;
    this.isWebSpeechActive = false;
    this.silenceTimer = null;

    // MediaRecorder fallback instances
    this.mediaRecorder = null;
    this.mediaStream = null;
    this.audioChunks = [];

    this._initWebSpeech();
  }

  _initWebSpeech() {
    if (typeof window === 'undefined') return;
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      this.recognition = new SpeechRecognition();
      this.recognition.continuous = true; // Turn-based continuous mode allowing natural conversational pauses
      this.recognition.interimResults = true;
      this.recognition.maxAlternatives = 1;

      this.lastCapturedText = '';

      this.recognition.onstart = () => {
        this.isWebSpeechActive = true;
        this.lastCapturedText = '';
        if (this.silenceTimer) {
          clearTimeout(this.silenceTimer);
          this.silenceTimer = null;
        }
        this._setState(STT_STATES.RECORDING);
      };

      this.recognition.onresult = (event) => {
        if (this.silenceTimer) {
          clearTimeout(this.silenceTimer);
          this.silenceTimer = null;
        }

        let interimText = '';
        let finalText = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcriptChunk = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalText += transcriptChunk;
          } else {
            interimText += transcriptChunk;
          }
        }

        if (interimText) {
          this.lastCapturedText = interimText;
          this.onInterimTranscript(interimText);
        }

        if (finalText) {
          this.lastCapturedText = '';
          this.onFinalTranscript(finalText.trim(), this.currentLanguage, 'web_speech');
        }

        // Set a natural 2-second silence timer to stop listening once the user finishes speaking
        this.silenceTimer = setTimeout(() => {
          if (this.isWebSpeechActive) {
            this.stopListening();
          }
        }, 2000);
      };

      this.recognition.onerror = (event) => {
        this.isWebSpeechActive = false;
        this.lastCapturedText = '';
        if (this.silenceTimer) {
          clearTimeout(this.silenceTimer);
          this.silenceTimer = null;
        }
        const err = event.error;

        if (err === 'not-allowed') {
          this._emitError(STT_ERRORS.PERMISSION_DENIED, 'Microphone access denied. Please grant permission or type your query.');
        } else if (err === 'no-speech') {
          // Gracefully reset on silence detection in continuous mode
          this._setState(STT_STATES.IDLE);
        } else if (err === 'network') {
          // Fall back to MediaRecorder + Backend STT on network glitch
          console.warn('[STTManager] Web Speech API network error. Falling back to backend audio recording...');
          this._startMediaRecorderFallback(this.currentLanguage);
        } else if (err === 'audio-capture') {
          this._emitError(STT_ERRORS.AUDIO_CAPTURE, 'No microphone device was found on this system.');
        } else {
          this._emitError(STT_ERRORS.NETWORK_ERROR, `Speech recognition error: ${err}`);
        }
      };

      this.recognition.onend = () => {
        this.isWebSpeechActive = false;
        if (this.silenceTimer) {
          clearTimeout(this.silenceTimer);
          this.silenceTimer = null;
        }
        // On mobile browsers where recognition ends before emitting isFinal, commit captured speech
        if (this.lastCapturedText && this.lastCapturedText.trim().length > 0) {
          const textToCommit = this.lastCapturedText.trim();
          this.lastCapturedText = '';
          this._setState(STT_STATES.PROCESSING);
          this.onFinalTranscript(textToCommit, this.currentLanguage, 'web_speech');
        }
        this._setState(STT_STATES.IDLE);
      };
    }
  }

  isWebSpeechSupported() {
    return Boolean(this.recognition);
  }

  isMediaRecorderSupported() {
    return typeof window !== 'undefined' && 
           Boolean(navigator.mediaDevices && navigator.mediaDevices.getUserMedia && window.MediaRecorder);
  }

  _setState(newState) {
    this.state = newState;
    this.onStateChange(this.state);
  }

  _emitError(code, message) {
    this._setState(STT_STATES.ERROR);
    this.onError(code, message);
  }

  async startListening(langCode = 'hi') {
    const cleanLang = (langCode || 'hi').toLowerCase().trim();
    if (!SUPPORTED_LANGUAGES[cleanLang]) {
      this._emitError(
        STT_ERRORS.UNSUPPORTED_LANGUAGE,
        `Unsupported language '${langCode}'. Supported languages: Hindi ('hi'), Marathi ('mr'), Tamil ('ta'). Silent substitution is prohibited.`
      );
      return;
    }

    this.currentLanguage = cleanLang;
    const langConfig = SUPPORTED_LANGUAGES[cleanLang];

    // Priority 1: Use Web Speech API if available
    if (this.isWebSpeechSupported()) {
      try {
        this.recognition.lang = langConfig.locale;
        this.recognition.start();
        return;
      } catch (e) {
        console.warn('[STTManager] Web Speech start failed, falling back to MediaRecorder:', e);
      }
    }

    // Priority 2: Fall back to MediaRecorder + Backend STT
    if (this.isMediaRecorderSupported()) {
      await this._startMediaRecorderFallback(cleanLang);
      return;
    }

    // Priority 3: Neither is supported -> Direct user to typed input
    this._emitError(
      STT_ERRORS.UNSUPPORTED_BROWSER,
      'Speech recognition is not supported in this browser. Please use the typed input box.'
    );
  }

  async _startMediaRecorderFallback(langCode) {
    this.audioChunks = [];
    try {
      this.mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      const mimeType = MediaRecorder.isTypeSupported('audio/webm') ? 'audio/webm' : 'audio/wav';
      this.mediaRecorder = new MediaRecorder(this.mediaStream, { mimeType });

      this.mediaRecorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
          this.audioChunks.push(event.data);
        }
      };

      this.mediaRecorder.onstop = async () => {
        this._setState(STT_STATES.PROCESSING);
        
        // Stop audio tracks
        if (this.mediaStream) {
          this.mediaStream.getTracks().forEach(track => track.stop());
          this.mediaStream = null;
        }

        if (this.audioChunks.length === 0) {
          this._emitError(STT_ERRORS.NO_SPEECH, 'No audio recorded. Please try again.');
          return;
        }

        const audioBlob = new Blob(this.audioChunks, { type: mimeType });
        await this._sendToBackendSTT(audioBlob, langCode);
      };

      this.mediaRecorder.start();
      this._setState(STT_STATES.RECORDING);

    } catch (err) {
      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
        this._emitError(STT_ERRORS.PERMISSION_DENIED, 'Microphone permission was denied. Please use the typed input box.');
      } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
        this._emitError(STT_ERRORS.AUDIO_CAPTURE, 'No microphone found on this device.');
      } else {
        this._emitError(STT_ERRORS.AUDIO_CAPTURE, `Audio capture failed: ${err.message}`);
      }
    }
  }

  async _sendToBackendSTT(audioBlob, langCode) {
    const formData = new FormData();
    const extension = audioBlob.type.includes('wav') ? 'wav' : 'webm';
    formData.append('file', audioBlob, `speech_recording.${extension}`);
    formData.append('language', langCode);

    try {
      const response = await fetch(`${this.apiBaseUrl}/api/stt`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Server returned ${response.status}`);
      }

      const result = await response.json();
      if (result.transcript) {
        this.onFinalTranscript(result.transcript, langCode, 'backend_gemini');
        this._setState(STT_STATES.IDLE);
      } else {
        this._emitError(STT_ERRORS.NO_SPEECH, 'No speech was recognized from audio. Please speak clearly or type.');
      }
    } catch (err) {
      this._emitError(STT_ERRORS.BACKEND_ERROR, `Backend STT failed: ${err.message}. Please use typed input.`);
    }
  }

  stopListening() {
    if (this.silenceTimer) {
      clearTimeout(this.silenceTimer);
      this.silenceTimer = null;
    }

    if (this.isWebSpeechActive && this.recognition) {
      try {
        this.recognition.stop();
      } catch (e) {
        // Safe ignore
      }
      this.isWebSpeechActive = false;
    }

    if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
      try {
        this.mediaRecorder.stop();
      } catch (e) {
        // Safe ignore
      }
    }

    if (this.state === STT_STATES.RECORDING) {
      this._setState(STT_STATES.PROCESSING);
    }
  }

  abort() {
    if (this.silenceTimer) {
      clearTimeout(this.silenceTimer);
      this.silenceTimer = null;
    }
    if (this.recognition) {
      try {
        this.recognition.abort();
      } catch (e) {}
    }
    if (this.mediaStream) {
      this.mediaStream.getTracks().forEach(track => track.stop());
      this.mediaStream = null;
    }
    this._setState(STT_STATES.IDLE);
  }
}

