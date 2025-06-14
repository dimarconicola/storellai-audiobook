# File: /story-to-mp3-audiobook-generator/story-to-mp3-audiobook-generator/src/audiobook/tts.py

import os
from google.cloud import texttospeech
# config.py is still used for fallback or general defaults if not provided, 
# but core parameters will now be passed to the function.
from config import TTS_MODEL # Example: still might use some general config

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

def synthesize_speech(text: str, output_filename: str, language_code: str, voice_name: str, audio_config_params: dict, ssml_gender_str: str = "NEUTRAL"):
    """
    Synthesizes speech from text using Google Cloud Text-to-Speech.

    Args:
        text: The text to synthesize.
        output_filename: Path to save the output audio file.
        language_code: The language code (e.g., "en-US", "it-IT").
        voice_name: The name of the voice to use.
        audio_config_params: A dictionary with audio configuration like encoding, rate, etc.
        ssml_gender_str: The SSML gender as a string ("FEMALE", "MALE", "NEUTRAL").
    """
    client = texttospeech.TextToSpeechClient()

    # Chirp3 voices (and potentially others) might not support SSML or have limitations.
    # This logic can be expanded based on voice capabilities.
    # For now, assume Chirp voices don't use the add_ssml_pauses function.
    if "chirp" in voice_name.lower(): # A simple check for Chirp voices
        synthesis_input = texttospeech.SynthesisInput(text=text)
        print(f"[TTS] Using plain text input for Chirp voice: {voice_name}")
    else:
        ssml_text = add_ssml_pauses(text)
        synthesis_input = texttospeech.SynthesisInput(ssml=ssml_text)
        print(f"[TTS] Using SSML input for voice: {voice_name}")

    try:
        ssml_gender_enum = getattr(texttospeech.SsmlVoiceGender, ssml_gender_str.upper(), texttospeech.SsmlVoiceGender.NEUTRAL)
    except AttributeError:
        print(f"[TTS] Warning: Invalid SSML gender string '{ssml_gender_str}'. Defaulting to NEUTRAL.")
        ssml_gender_enum = texttospeech.SsmlVoiceGender.NEUTRAL

    voice = texttospeech.VoiceSelectionParams(
        language_code=language_code,
        name=voice_name,
        ssml_gender=ssml_gender_enum
    )

    # Ensure audio_encoding is an enum member
    audio_encoding_str = audio_config_params.get("audio_encoding", "MP3")
    try:
        audio_encoding_enum = getattr(texttospeech.AudioEncoding, audio_encoding_str.upper())
    except AttributeError:
        print(f"[TTS] Warning: Invalid audio encoding string '{audio_encoding_str}'. Defaulting to MP3.")
        audio_encoding_enum = texttospeech.AudioEncoding.MP3

    audio_config_args = {
        "audio_encoding": audio_encoding_enum,
        "speaking_rate": audio_config_params.get("speaking_rate", 1.0),
        "volume_gain_db": audio_config_params.get("volume_gain_db", 0.0),
        "effects_profile_id": audio_config_params.get("effects_profile_id", []),
    }
    if "sample_rate_hertz" in audio_config_params and audio_config_params["sample_rate_hertz"] is not None:
        audio_config_args["sample_rate_hertz"] = audio_config_params["sample_rate_hertz"]

    audio_config_obj = texttospeech.AudioConfig(**audio_config_args)

    try:
        print(f"[TTS] Requesting synthesis: lang={language_code}, voice={voice_name}, output={output_filename}")
        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config_obj
        )

        with open(output_filename, "wb") as out:
            out.write(response.audio_content)
        print(f"[TTS] Audio content written to {output_filename}")
        return True
    except Exception as e:
        print(f"[TTS] Error during speech synthesis: {e}")
        # Log more details for debugging if possible
        if hasattr(e, 'details'):
            print(f"[TTS] Error details: {e.details()}")
        return False