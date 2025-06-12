# File: /story-to-mp3-audiobook-generator/story-to-mp3-audiobook-generator/src/audiobook/tts.py

import os
from google.cloud import texttospeech
from config import GOOGLE_TTS_VOICE_PARAMS, AUDIO_CONFIG

def add_ssml_pauses(text: str) -> str:
    """
    Adds SSML pause tags to the text to improve narration rhythm.
    """
    # Add a long pause after periods
    text_with_pauses = text.replace('.', '. <break time="1000ms"/>')
    # Add a short pause after commas
    text_with_pauses = text_with_pauses.replace(',', ', <break time="700ms"/>')
    # Wrap in <speak> tags for SSML
    return f"<speak>{text_with_pauses}</speak>"

def synthesize_speech(text, output_path):
    client = texttospeech.TextToSpeechClient()
    voice_name = GOOGLE_TTS_VOICE_PARAMS["name"]

    # Chirp3 voices do NOT support SSML
    if "Chirp3" in voice_name or "Chirp" in voice_name:
        synthesis_input = texttospeech.SynthesisInput(text=text)
    else:
        ssml_text = add_ssml_pauses(text)
        synthesis_input = texttospeech.SynthesisInput(ssml=ssml_text)

    voice = texttospeech.VoiceSelectionParams(
        language_code=GOOGLE_TTS_VOICE_PARAMS["language_code"],
        name=voice_name,
        ssml_gender=getattr(texttospeech.SsmlVoiceGender, GOOGLE_TTS_VOICE_PARAMS.get("ssml_gender", "NEUTRAL"))
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=getattr(texttospeech.AudioEncoding, AUDIO_CONFIG.get("audio_encoding", "MP3")),
        speaking_rate=AUDIO_CONFIG.get("speaking_rate", 1.0),
        volume_gain_db=AUDIO_CONFIG.get("volume_gain_db", 0.0),
        effects_profile_id=AUDIO_CONFIG.get("effects_profile_id", []),
        # Only add sample_rate_hertz if you want to override the default
        # sample_rate_hertz=AUDIO_CONFIG.get("sample_rate_hertz", None)
    )

    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config
    )

    with open(output_path, "wb") as out:
        out.write(response.audio_content)
    print(f"Audio content written to {output_path}")