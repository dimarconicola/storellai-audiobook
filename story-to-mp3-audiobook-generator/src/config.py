# Configuration settings for the Story to MP3 Audiobook Generator

STORIES_FOLDER = "stories"
AUDIO_FOLDER = "audio"

# Preferred voices: "it-IT-Chirp3-HD-Callirrhoe" (premium), fallback: "it-IT-Neural2-E"
GOOGLE_TTS_VOICE_PARAMS = {
    "language_code": "it-IT",
    "name": "it-IT-Chirp3-HD-Callirrhoe",  
    "ssml_gender": "FEMALE",
}

# alt voices it-IT-Chirp3-HD-Achernar it-IT-Chirp-HD-O it-IT-Chirp3-HD-Callirrhoe

AUDIO_CONFIG = {
    "audio_encoding": "MP3",
    "speaking_rate": 0.85,
    # "pitch": -2.5,  # Only for WaveNet/Neural2 voices
    "volume_gain_db": 0.0,
    # "effects_profile_id": [],  # No special processing
    # "sample_rate_hertz": 44000,  # Comment out to use default for the voice
}
TTS_MODEL = "chirp"  # or "chirp" for Chirp3 voices

# Example voices: https://cloud.google.com/text-to-speech/docs/voices