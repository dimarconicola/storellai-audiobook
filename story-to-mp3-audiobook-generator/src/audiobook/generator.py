import os
from audiobook.tts import synthesize_speech

class AudiobookGenerator:
    def __init__(self, stories):
        self.stories = stories

    def generate_audiobooks(self, audio_folder="audio"):
        for story in self.stories:
            character_id = story.get("id", "unknown")
            character_folder = os.path.join(audio_folder, character_id)
            os.makedirs(character_folder, exist_ok=True)
            for s in story.get("stories", []):
                story_id = s.get("id")
                title = s.get("title", "")
                if not title.endswith("!"):
                    title += "!"
                text = s.get("text", "")
                combined = f"{title} {text}"
                filename = f"{story_id}.mp3"
                output_path = os.path.join(character_folder, filename)
                print(f"Generating: {output_path}")
                synthesize_speech(combined, output_path)

    def test_title_and_story_text(self, story):
        for s in story.get("stories", []):
            title = s.get("title", "")
            if not title.endswith("!"):
                title += "!"
            text = s.get("text", "")
            combined = f"{title} {text}"
            print("=== OUTPUT TO TTS ===")
            print(combined)
            print("=====================")
            break  # Only test the first story for now