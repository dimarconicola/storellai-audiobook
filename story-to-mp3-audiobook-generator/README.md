# **Story to MP3 Audiobook Generator**

A beginner-friendly Python project that converts structured story files into MP3 audiobooks using the Google Cloud Text-to-Speech API. This project is designed for easy debugging and step-by-step development.

## **Project Structure**

```
story-to-mp3-audiobook-generator
├── src
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── audiobook
│   │   ├── __init__.py
│   │   ├── generator.py
│   │   ├── tts.py
│   │   └── utils.py
│   └── tests
│       ├── __init__.py
│       ├── test_generator.py
│       └── test_utils.py
├── stories
│   └── example_story.json
├── audio
├── requirements.txt
└── README.md
```

## **Features**

- **Batch Processing:** Automatically processes all JSON story files in the specified folder.
- **Structured Output:** Generates audio files organized by character and story.
- **Highly Configurable:** Customize voice, language, and audio parameters easily.
- **Stateful Generation:** Skips existing audio files to save time and costs.
- **High-Quality Audio:** Utilizes Google's advanced text-to-speech technology for natural narration.

## **Prerequisites**

Before running the project, ensure you have the following:

1. **Python 3.6+** installed.
2. A **Google Cloud Platform (GCP) Account** with billing enabled.
3. The **Cloud Text-to-Speech API** enabled in your GCP project.
4. A **Service Account Key** (.json file) for authentication.

## **Setup & Installation**

1. **Install Required Libraries:**
   Run the following command to install the necessary Python libraries:
   ```
   pip install -r requirements.txt
   ```

2. **Configure Google Cloud Authentication:**
   Set the environment variable for your service account key:
   - On macOS or Linux:
     ```
     export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/keyfile.json"
     ```
   - On Windows:
     ```
     setx GOOGLE_APPLICATION_CREDENTIALS "C:\\path\\to\\your\\keyfile.json"
     ```

## **How to Run the Application**

To generate audiobooks from your stories, navigate to the project directory and run:
```
python src/main.py
```

## **Input JSON Format**

Each JSON file in the `stories` folder should follow this structure:
{
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
    },
    {
      "id": 2,
      "title": "Story Title 2",
      "tone": "adventurous",
      "length_words": 352,
      "text": "The full text of the second story..."
    }
  ]
}

## **License**

© 2025 Your Name - Licensed under the [MIT License](https://opensource.org/licenses/MIT)