import unittest
from src.audiobook.generator import AudiobookGenerator

class TestAudiobookGenerator(unittest.TestCase):

    def setUp(self):
        self.generator = AudiobookGenerator(stories_folder='stories', audio_folder='audio')

    def test_load_stories(self):
        stories = self.generator.load_stories()
        self.assertIsInstance(stories, list)
        self.assertGreater(len(stories), 0)

    def test_generate_audio(self):
        story = {
            "id": "000000",
            "character": "Character Name",
            "location": "Story Location",
            "stories": [
                {
                    "id": 1,
                    "title": "Story Title 1",
                    "tone": "calm",
                    "length_words": 350,
                    "text": "The full text of the story goes here..."
                }
            ]
        }
        audio_file = self.generator.generate_audio(story)
        self.assertTrue(audio_file.endswith('.mp3'))

    def test_output_structure(self):
        self.generator.generate_audiobook()
        # Check if audio folder is created
        self.assertTrue(os.path.exists('audio'))
        # Check if specific character folder is created
        self.assertTrue(os.path.exists('audio/000000'))

if __name__ == '__main__':
    unittest.main()