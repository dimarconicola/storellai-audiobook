# main.py

import os
import json
from audiobook.generator import AudiobookGenerator
from config import STORIES_FOLDER, AUDIO_FOLDER

def main():
    if not os.path.exists(AUDIO_FOLDER):
        os.makedirs(AUDIO_FOLDER)

    stories = load_stories(STORIES_FOLDER)
    generator = AudiobookGenerator(stories)
    generator.generate_audiobooks()

def load_stories(folder):
    stories = []
    for filename in os.listdir(folder):
        if filename.endswith('.json'):
            with open(os.path.join(folder, filename), 'r') as file:
                story_data = json.load(file)
                stories.append(story_data)
    return stories

if __name__ == '__main__':
    main()

    # TEST: Print title + story for the first story of the first character
    from audiobook.generator import AudiobookGenerator
    from config import STORIES_FOLDER
    import os

    # Load stories
    import json
    stories = []
    for filename in os.listdir(STORIES_FOLDER):
        if filename.endswith('.json'):
            with open(os.path.join(STORIES_FOLDER, filename), 'r') as file:
                story_data = json.load(file)
                stories.append(story_data)

    # Test the function
    generator = AudiobookGenerator(stories)
    generator.test_title_and_story_text(stories[0])