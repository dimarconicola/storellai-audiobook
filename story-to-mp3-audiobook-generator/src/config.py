# Configuration settings for the Story to MP3 Audiobook Generator

STORIES_FOLDER = "stories"
AUDIO_FOLDER = "audio"

# Google TTS Voice Parameters
# Structure: 
# { 
#   "language_code_full": { "name": "voice_name_or_list", "ssml_gender": "GENDER" (optional) },
#   "language_code_short": { "name": "voice_name_or_list", ... }, (fallback for region-specific)
#   "default": { "name": "default_voice_for_unlisted_languages", ... }
# }
GOOGLE_TTS_VOICE_PARAMS = {
    "it-IT": {
        "name": ["it-IT-Chirp3-HD-Callirrhoe", "it-IT-Neural2-E"], # Premium first, then standard
        "ssml_gender": "FEMALE",
    },
    "it": { # Fallback for general Italian
        "name": ["it-IT-Chirp3-HD-Callirrhoe", "it-IT-Neural2-E"],
        "ssml_gender": "FEMALE",
    },
    "en-US": {
        "name": ["en-US-Standard-C", "en-US-Wavenet-D"], # Example: Standard female, Wavenet female
        "ssml_gender": "FEMALE", # Can be overridden by specific voice choice if needed
    },
    "en": { # Fallback for general English
        "name": ["en-US-Standard-C", "en-US-Wavenet-D"],
    },
    "es-ES": {
        "name": ["es-ES-Standard-A", "es-ES-Wavenet-B"], # Example voices
    },
    "es": {
        "name": ["es-ES-Standard-A", "es-ES-Wavenet-B"],
    },
    "fr-FR": {
        "name": ["fr-FR-Standard-A", "fr-FR-Wavenet-B"], # Example voices
    },
    "fr": {
        "name": ["fr-FR-Standard-A", "fr-FR-Wavenet-B"],
    },
    "de-DE": {
        "name": ["de-DE-Standard-A", "de-DE-Wavenet-B"], # Example voices
    },
    "de": {
        "name": ["de-DE-Standard-A", "de-DE-Wavenet-B"],
    },
    "default": { # Default voice if language not found above
        "name": "en-US-Standard-C", # A sensible default
        "language_code": "en-US" # Specify language_code for the default voice itself
    }
}

# alt voices it-IT-Chirp3-HD-Achernar it-IT-Chirp-HD-O it-IT-Chirp3-HD-Callirrhoe

AUDIO_CONFIG = {
    "mp3": { # Configuration for MP3 output
        "audio_encoding": "MP3",
        "speaking_rate": 0.90, # Adjusted slightly
        "volume_gain_db": 0.0,
    },
    "wav": { # Example for WAV if needed later
        "audio_encoding": "LINEAR16",
        "speaking_rate": 0.90,
        "sample_rate_hertz": 24000 # For LINEAR16, sample rate is often specified
    }
    # "pitch": -2.5,  # Only for WaveNet/Neural2 voices, can be added per-voice if needed
    # "effects_profile_id": [],  # No special processing
}

# Default model for TTS, can be overridden by specific voice capabilities
# Chirp voices are generally higher quality. Standard voices might not use "chirp".
# The synthesize_speech function might need to adapt based on voice type if model is critical.
TTS_MODEL = "default" # "chirp" or "default" (some voices might not support chirp)

# Example voices: https://cloud.google.com/text-to-speech/docs/voices