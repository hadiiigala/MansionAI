import base64
import os
import tempfile
import wave
from io import BytesIO

import pyttsx3
import speech_recognition as sr

class AudioHandler:
    def __init__(self):
        """Initialize audio handler with TTS engine"""
        self.engine = pyttsx3.init()
        self.recognizer = sr.Recognizer()
        
        # Set TTS properties
        self.engine.setProperty('rate', 150)  # Speed of speech
        self.engine.setProperty('volume', 0.9)  # Volume level
        
    def text_to_speech(self, text, output_format='base64'):
        """
        Convert text to speech and return as audio file or base64
        
        Args:
            text (str): Text to convert to speech
            output_format (str): 'base64' or 'file' - return format
            
        Returns:
            dict: Contains audio data and metadata
        """
        try:
            if not text or not isinstance(text, str):
                return {
                    "success": False,
                    "error": "Text must be a non-empty string"
                }
            
            temp_audio_path = None
            try:
                # Create a temporary file for TTS output in an OS-safe location
                with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_audio:
                    temp_audio_path = temp_audio.name
                
                self.engine.save_to_file(text, temp_audio_path)
                self.engine.runAndWait()

                if not temp_audio_path or not os.path.exists(temp_audio_path):
                    return {
                        "success": False,
                        "error": "Failed to generate audio file"
                    }

                with open(temp_audio_path, 'rb') as audio_file:
                    audio_data = audio_file.read()

                if output_format == 'base64':
                    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                    result = {
                        "success": True,
                        "audio": f"data:audio/wav;base64,{audio_base64}",
                        "text": text,
                        "format": "wav"
                    }
                else:
                    result = {
                        "success": True,
                        "audio_path": temp_audio_path,
                        "text": text,
                        "format": "wav"
                    }

                return result
            finally:
                if temp_audio_path and os.path.exists(temp_audio_path):
                    try:
                        os.remove(temp_audio_path)
                    except OSError:
                        pass
                
        except Exception as e:
            print(f"Error in text_to_speech: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def speech_to_text(self, audio_data_base64, language='en-US'):
        """
        Convert speech (audio) to text
        
        Args:
            audio_data_base64 (str): Base64 encoded audio data (WAV or MP3)
            language (str): Language code (default: en-US)
            
        Returns:
            dict: Contains transcribed text and metadata
        """
        try:
            # Decode base64 audio data (already WAV from frontend)
            audio_data = base64.b64decode(audio_data_base64)

            with wave.open(BytesIO(audio_data)) as wav_file:
                sample_rate = wav_file.getframerate()
                sample_width = wav_file.getsampwidth()
                frames = wav_file.readframes(wav_file.getnframes())

            if not sample_rate or not sample_width:
                raise ValueError("Invalid WAV data provided")

            # Create an audio source from the bytes
            audio_source = sr.AudioData(frames, sample_rate, sample_width)
            
            # Recognize speech using Google Speech Recognition
            text = self.recognizer.recognize_google(audio_source, language=language)
            
            return {
                "success": True,
                "text": text,
                "language": language,
                "confidence": "high"
            }
            
        except sr.UnknownValueError:
            return {
                "success": False,
                "error": "Could not understand audio. Please try again.",
                "error_type": "unknown_value"
            }
        except sr.RequestError as e:
            return {
                "success": False,
                "error": f"Could not request results from Google Speech Recognition service; {str(e)}",
                "error_type": "request_error"
            }
        except Exception as e:
            print(f"Error in speech_to_text: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_type": "general_error"
            }
    
    def set_voice_properties(self, rate=150, volume=0.9):
        """
        Set TTS voice properties
        
        Args:
            rate (int): Speed of speech (default 150, range 50-300)
            volume (float): Volume level (default 0.9, range 0.0-1.0)
        """
        try:
            self.engine.setProperty('rate', max(50, min(300, rate)))
            self.engine.setProperty('volume', max(0.0, min(1.0, volume)))
            return {"success": True, "message": "Voice properties updated"}
        except Exception as e:
            return {"success": False, "error": str(e)}
