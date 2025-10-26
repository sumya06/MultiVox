from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import tempfile
import os
import traceback
import speech_recognition as sr
from deep_translator import GoogleTranslator
import io
import subprocess
from gtts import gTTS
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
# Fix CORS configuration - allow all origins for development
CORS(app)

app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50 MB

# Use environment variable for FFmpeg path or default to system PATH
FFMPEG_PATH = os.environ.get("FFMPEG_PATH", "ffmpeg")
FFPROBE_PATH = os.environ.get("FFPROBE_PATH", "ffprobe")

# Supported languages for translation
SUPPORTED_LANGUAGES = {
    'en': 'English', 'es': 'Spanish', 'fr': 'French', 'de': 'German', 
    'it': 'Italian', 'pt': 'Portuguese', 'ru': 'Russian', 'ja': 'Japanese',
    'ko': 'Korean', 'zh': 'Chinese', 'ar': 'Arabic', 'hi': 'Hindi',
    'ur': 'Urdu', 'tr': 'Turkish', 'nl': 'Dutch', 'sv': 'Swedish',
    'pl': 'Polish', 'vi': 'Vietnamese', 'th': 'Thai'
}

def convert_audio_to_wav(audio_data, input_ext=".webm"):
    """
    Convert any audio format to WAV using FFmpeg
    """
    try:
        # Create temporary files
        with tempfile.NamedTemporaryFile(delete=False, suffix=input_ext) as input_file:
            input_file.write(audio_data)
            input_path = input_file.name
            
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as output_file:
            output_path = output_file.name
            
        # Convert using FFmpeg
        cmd = [
            FFMPEG_PATH,
            '-i', input_path,
            '-acodec', 'pcm_s16le',
            '-ac', '1',
            '-ar', '16000',
            output_path,
            '-y'
        ]
        
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        if result.returncode == 0:
            # Read the converted file
            with open(output_path, 'rb') as f:
                wav_data = f.read()
                
            # Clean up
            os.unlink(input_path)
            os.unlink(output_path)
            
            return wav_data
        else:
            logging.error(f"FFmpeg conversion failed: {result.stderr}")
            return None
            
    except Exception as e:
        logging.error(f"Error in FFmpeg conversion: {e}")
        try:
            os.unlink(input_path)
            os.unlink(output_path)
        except:
            pass
        return None

def detect_audio_format(audio_data):
    """
    Try to detect audio format from magic bytes
    """
    if audio_data.startswith(b'OggS') or audio_data.startswith(b'RIFF'):
        return '.wav'
    elif audio_data.startswith(b'\xFF\xFB') or audio_data.startswith(b'ID3'):
        return '.mp3'
    elif audio_data.startswith(b'\x1aE\xdf\xa3'):
        return '.webm'
    elif audio_data.startswith(b'fLaC'):
        return '.flac'
    else:
        # Default to webm for Chrome recordings
        return '.webm'

def transcribe_audio(audio_data):
    """
    Transcribe audio using Google Speech Recognition
    """
    try:
        recognizer = sr.Recognizer()
        
        # Create a temporary file in memory
        with sr.AudioFile(io.BytesIO(audio_data)) as source:
            audio_data = recognizer.record(source)
        print("Attempting recognition...")
        text = recognizer.recognize_google(audio_data)
        print("Recognized text:", text)
        return text
    except sr.UnknownValueError:
        print("Google SR could not understand audio.")
        return "Could not understand audio"
    except sr.RequestError as e:
        return f"Error with speech recognition service: {e}"
    except Exception as e:
        return f"Error transcribing audio: {str(e)}"

def translate_text(text, target_lang):
    """
    Translate text using deep_translator library
    """
    try:
        if text.strip() and target_lang in SUPPORTED_LANGUAGES:
            translation = GoogleTranslator(source='auto', target=target_lang).translate(text)
            return translation
        return text
    except Exception as e:
        return f"Translation error: {str(e)}"

def text_to_speech(text, lang='en'):
    """
    Convert text to speech using gTTS
    """
    try:
        if not text.strip():
            return None
            
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
            tts = gTTS(text=text, lang=lang, slow=False)
            tts.save(tmp_file.name)
            return tmp_file.name
    except Exception as e:
        print(f"TTS error: {e}")
        return None

@app.route("/health", methods=["GET"])
def health():
    info = {"status": "ok", "free_apis_available": True, "mode": "free_apis"}
    return jsonify(info)

@app.route("/translate", methods=["POST", "OPTIONS"])
def translate_audio():
    """
    Accepts a recorded audio blob, transcribes it, and translates it
    """
    if request.method == "OPTIONS":
        return jsonify({}), 200
        
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded (field name must be 'file')."}), 400

        audio_file = request.files["file"]
        source_lang = request.form.get("source_lang", "auto")
        target_lang = request.form.get("target_lang", "en")

        # Validate target language
        if target_lang not in SUPPORTED_LANGUAGES:
            return jsonify({"error": f"Unsupported target language: {target_lang}"}), 400

        # Read the audio file into memory
        audio_data = audio_file.read()
        
        # Check if audio data is empty
        if not audio_data:
            return jsonify({"error": "Uploaded audio file is empty."}), 400
        
        # Try to convert to WAV format
        wav_data = convert_audio_to_wav(audio_data)
        
        if not wav_data:
            return jsonify({"error": "Failed to process audio file. Please try a different format or check FFmpeg installation."}), 400
        
        # Transcribe audio
        original_text = transcribe_audio(wav_data)
        
        # If transcription failed, return error
        if "Error" in original_text or "Could not understand" in original_text:
            return jsonify({"error": original_text}), 400

        # Translate text
        translated_text = translate_text(original_text, target_lang)

        # Return JSON response
        return jsonify({
            "transcript": original_text,
            "translated_text": translated_text
        })

    except Exception as e:
        logging.error(f"Server exception in translate_audio: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Server exception: {str(e)}"}), 500

@app.route("/text-to-speech", methods=["POST", "OPTIONS"])
def handle_text_to_speech():
    """
    Convert text to speech and return audio file
    """
    if request.method == "OPTIONS":
        return jsonify({}), 200
        
    try:
        data = request.get_json(force=True, silent=True) or {}
        text = (data.get("text") or "").strip()
        lang = data.get("lang", "en")
        
        if not text:
            return jsonify({"error": "Field 'text' required."}), 400
            
        # Validate language
        if lang not in SUPPORTED_LANGUAGES:
            return jsonify({"error": f"Unsupported language: {lang}"}), 400
            
        # Generate speech
        audio_file = text_to_speech(text, lang)
        
        if not audio_file:
            return jsonify({"error": "Failed to generate speech"}), 500
            
        # Return the audio file
        return send_file(
            audio_file,
            mimetype="audio/mpeg",
            as_attachment=True,
            download_name="speech.mp3"
        )
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Server exception: {str(e)}"}), 500

@app.route("/text-translate", methods=["POST", "OPTIONS"])
def text_translate():
    """
    JSON: { text, source_lang, target_lang }
    Returns JSON translation
    """
    if request.method == "OPTIONS":
        return jsonify({}), 200
        
    try:
        data = request.get_json(force=True, silent=True) or {}
        text = (data.get("text") or "").strip()
        if not text:
            return jsonify({"error": "Field 'text' required."}), 400

        source_lang = data.get("source_lang", "auto")
        target_lang = data.get("target_lang", "en")
        
        # Validate target language
        if target_lang not in SUPPORTED_LANGUAGES:
            return jsonify({"error": f"Unsupported target language: {target_lang}"}), 400

        translated = translate_text(text, target_lang)
        return jsonify({"translated_text": translated})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Server exception: {str(e)}"}), 500

@app.route("/languages", methods=["GET"])
def get_languages():
    """
    Return supported languages
    """
    return jsonify(SUPPORTED_LANGUAGES)

@app.route("/", methods=["GET"])
def index():
    return jsonify({"message": "Voice Translation API is running", "mode": "free_apis"})

if __name__ == "__main__":
    print("Starting Flask server with free speech-to-text and translation APIs")
    print("Supported languages:", SUPPORTED_LANGUAGES)
    app.run(debug=True, port=5000, host="0.0.0.0")