from groq import Groq
from groq.types.audio.translation import Translation

import os

class SpeechToTextService:
    def __init__(self):
        self.client = Groq(
            api_key=os.getenv('GROQ_API_KEY'),
        )

    def transcribe(self, audio_file: bytes, filename: str) -> str:
        '''
        Transcribe audio file to text using Groq's Whisper model.

        Args:
            audio_file (bytes): The audio file content to transcribe.
        
        Returns:
            str: The transcribed text from the audio file.
        '''
        translation: Translation = self.client.audio.translations.create(
            file=(filename, audio_file),
            model="whisper-large-v3",
            prompt="Transcribe what the user is saying",
            response_format="json",
            temperature=0.0
        )

        return translation.text