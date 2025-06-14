import os
import re # Added for sequential card ID generation

# SET GOOGLE APPLICATION CREDENTIALS
# The key file is at the workspace root.
# app.py is in story-to-mp3-audiobook-generator/web_interface/
# So we need to go up two levels from app.py's directory to reach the workspace root.
# and then one level up from 'story-to-mp3-audiobook-generator' to the main project root.
# Correct path calculation:
# os.path.dirname(__file__) is /Users/nicoladimarco/code/storellai-audiobook/story-to-mp3-audiobook-generator/web_interface
# '..' -> /Users/nicoladimarco/code/storellai-audiobook/story-to-mp3-audiobook-generator
# '..' -> /Users/nicoladimarco/code/storellai-audiobook
# '..' -> /Users/nicoladimarco/code/ (This is wrong, it should be 2 levels up from web_interface to project root)

# Let's define BASE_DIR first as it's already used and then calculate from there.
# BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # /Users/.../web_interface
# PROJECT_ROOT_FOR_CREDENTIALS = os.path.abspath(os.path.join(BASE_DIR, '..', '..')) # /Users/.../storellai-audiobook
# credentials_path = os.path.join(PROJECT_ROOT_FOR_CREDENTIALS, 'storellai-c5ff1089f6b5.json')

# Simpler: The JSON file is at the root of the workspace.
# The workspace root is /Users/nicoladimarco/code/storellai-audiobook
# The app.py is in /Users/nicoladimarco/code/storellai-audiobook/story-to-mp3-audiobook-generator/web_interface/app.py
# So, from app.py, we go up two directories to get to 'story-to-mp3-audiobook-generator',
# then one more directory up to 'storellai-audiobook'.
# path_to_json_key = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'storellai-c5ff1089f6b5.json'))
# This is still not quite right. Let's use the provided workspace root.
# Workspace root: /Users/nicoladimarco/code/storellai-audiobook
credentials_path = "/Users/nicoladimarco/code/storellai-audiobook/storellai-c5ff1089f6b5.json"

if os.path.exists(credentials_path):
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
    print(f"INFO: GOOGLE_APPLICATION_CREDENTIALS set to: {credentials_path}")
else:
    print(f"WARNING: Google credentials file not found at {credentials_path}. TTS will likely fail.")


import sys
import uuid # Keep for now, though not used for card_id
import json
import secrets # Added secrets for session key

# Add the parent directory (src) to the Python path
# to allow imports from src.audiobook and src.config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
# Add web_interface to sys.path to import story_llm
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


from flask import Flask, request, jsonify, render_template, send_from_directory, session # Added session
from audiobook.tts import synthesize_speech
from config import GOOGLE_TTS_VOICE_PARAMS, AUDIO_CONFIG
from story_llm import generate_story_from_llm, generate_multiple_stories, STORY_TONES # Updated import, added STORY_TONES

app = Flask(__name__)
app.secret_key = secrets.token_hex(16) # Added secret key for session management

# Define base directories relative to this app.py file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, '..')) # This is 'story-to-mp3-audiobook-generator'
STORIES_OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'stories')
# Output audio directly into a web-accessible folder if possible, or serve it
# For simplicity, we'll create a dedicated folder for web-generated audio
# that can be served by Flask.
WEB_AUDIO_SERVE_ROOT_REL = 'web_audio_files' # Relative to PROJECT_ROOT/src/audio
AUDIO_OUTPUT_BASE_DIR = os.path.join(PROJECT_ROOT, 'src', 'audio')
WEB_AUDIO_OUTPUT_DIR_ABS = os.path.join(AUDIO_OUTPUT_BASE_DIR, WEB_AUDIO_SERVE_ROOT_REL)


os.makedirs(STORIES_OUTPUT_DIR, exist_ok=True)
os.makedirs(WEB_AUDIO_OUTPUT_DIR_ABS, exist_ok=True)


@app.route('/')
def index():
    return render_template('index.html')

# Route to serve generated audio files
# session_id here will be used as card_id
@app.route(f'/audio_files/{WEB_AUDIO_SERVE_ROOT_REL}/<path:card_id>/<path:filename>')
def serve_web_audio(card_id, filename):
    directory = os.path.join(WEB_AUDIO_OUTPUT_DIR_ABS, card_id) # card_id here will be "000000", "000001", etc.
    app.logger.info(f"Serving audio file from: {directory}, filename: {filename}")
    return send_from_directory(directory, filename)


@app.route('/api/generate_stories', methods=['POST'])
def api_generate_stories():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        age = data.get('age')
        character = data.get('character')
        context_location = data.get('context_location')
        num_words = data.get('num_words', 250)
        
        # Robust language handling
        language_input = data.get('language')
        if not language_input or language_input.strip() == "":
            language = 'it-IT'  # Default language
            app.logger.warning(f"Language not provided or empty, defaulted to {language}. Input was: '{language_input}'")
        else:
            language = language_input.strip()

        num_stories = data.get('num_stories', 1)
        tones = data.get('tones') # Expected to be a list of tones

        if not all([age, character, context_location]): # Language is now handled above
            return jsonify({"error": "Missing required fields: age, character, context_location"}), 400
        
        if not isinstance(age, int) or not isinstance(num_words, int) or not isinstance(num_stories, int):
            return jsonify({"error": "Age, num_words, and num_stories must be integers"}), 400
        
        if num_stories < 1:
            return jsonify({"error": "num_stories must be at least 1"}), 400

        if not tones or not isinstance(tones, list) or len(tones) != num_stories:
            # If tones are not provided, or mismatch num_stories, assign random ones or default (as per story_llm logic)
            # For now, story_llm.generate_multiple_stories handles missing/mismatched tones by assigning them.
            # We'll pass the provided tones, and let story_llm handle it.
            app.logger.warning(f"Tones not provided or mismatch num_stories. Tones: {tones}, Num Stories: {num_stories}")

        # Generate sequential card ID
        max_id_num = -1
        if os.path.exists(STORIES_OUTPUT_DIR):
            for filename in os.listdir(STORIES_OUTPUT_DIR):
                # Match filenames like "card_000000.json"
                match = re.fullmatch(r"card_(\d{6})\.json", filename)
                if match:
                    current_id_num = int(match.group(1))
                    if current_id_num > max_id_num:
                        max_id_num = current_id_num
        
        next_id_num = max_id_num + 1
        # card_id will now be the numeric string, e.g., "000000", "000001"
        card_id = f"{next_id_num:06d}" 
        
        app.logger.info(f"Generating {num_stories} stories for card ID {card_id} with tones: {tones}")

        # generate_multiple_stories expects a list of tones.
        # If generating a single story, wrap its tone in a list.
        # story_llm.py's generate_multiple_stories should handle the tones list appropriately.
        generated_stories_data = generate_multiple_stories(
            num_stories=num_stories,
            age=age,
            character_idea=character,
            context_location_idea=context_location,
            num_words=num_words,
            language=language,
            tones_list=tones # Pass the list of tones
        )

        if not generated_stories_data or any(story.get("text", "").startswith("Error generating story") for story in generated_stories_data):
            return jsonify({"error": "LLM story generation failed for one or more stories."}), 500

        stories_details_for_client = [] # Renamed for clarity, this goes to client
        stories_details_for_session = [] # This will be stored in session, can be identical or slightly different if needed

        for i, story_data in enumerate(generated_stories_data): # story_data is a dict from story_llm
            story_text = story_data.get("text")
            story_tone = story_data.get("tone")
            story_validation = story_data.get("validation") # Get the validation object
            story_id_from_llm = story_data.get("id", str(i)) # Use ID from story_llm if available

            # Attempt to get the LLM-generated title
            llm_generated_title = story_data.get("story_title")

            # If top-level story_title is missing or empty, try to get it from validation data
            if not llm_generated_title or llm_generated_title.strip() == "":
                app.logger.warning(f"Top-level 'story_title' missing or empty for story {i} in card {card_id}. Attempting to use title from validation data.")
                validation_data_dict = story_data.get("validation", {})
                title_from_validation = validation_data_dict.get("story_title")
                if title_from_validation and title_from_validation.strip() != "":
                    llm_generated_title = title_from_validation
                    app.logger.info(f"Successfully used 'story_title' from validation data: '{llm_generated_title}'")
                else:
                    app.logger.warning(f"Could not find a valid 'story_title' in validation data either for story {i}, card {card_id}.")

            if llm_generated_title and llm_generated_title.strip() != "":
                story_title = llm_generated_title
            else:
                # Fallback title generation if LLM title is still missing or empty
                app.logger.warning(f"LLM did not provide a usable story_title for story {i} in card {card_id} (neither top-level nor in validation). Using app-level fallback.")
                title_prompt_part = character.split('.')[0].split(',')[0].strip()
                base_title = f"Story about {title_prompt_part}"
                if language.startswith("it"):
                    base_title = f"Una storia su {title_prompt_part}"
                story_title = f"{base_title} (Story {story_data.get('story_number', i+1)}) - Tone: {story_tone.capitalize() if story_tone else 'N/A'} [Fallback Title]"
            
            detail = {
                "id": story_id_from_llm, 
                "story_number": story_data.get('story_number', i+1), # Ensure story_number is present
                "text": story_text,
                "tone": story_tone,
                "title": story_title, # This will now be the LLM title or a clear fallback
                "validation": story_validation # Crucial: include the validation object
            }
            stories_details_for_client.append(detail)
            stories_details_for_session.append(detail) # Storing the same detail in session for now

        session['current_card_data'] = {
            "card_id": card_id,
            "age": age,
            "character": character,
            "context_location": context_location,
            "num_words": num_words,
            "language": language, # Storing the processed language
            "num_stories_generated": len(stories_details_for_session),
            "stories_details": stories_details_for_session, # This now includes validation
            "voice_requested_for_card": data.get('voice') 
        }
        app.logger.info(f"Stored in session for card_id {card_id}: {session['current_card_data']}")

        return jsonify({
            "message": f"{len(stories_details_for_client)} stories generated successfully.",
            "card_id": card_id,
            "stories": stories_details_for_client, # This now includes validation for each story
            # Enhancements: Include original/processed parameters for frontend state consistency
            "age": age,
            "character": character,
            "context_location": context_location,
            "num_words": num_words,
            "language": language, # The language used for generation and to be stored in session
            "num_stories_requested": num_stories,
            "tones_requested": tones,
            "voice_requested_for_card": data.get('voice')
        })

    except Exception as e:
        app.logger.error(f"Error in /api/generate_stories: {e}", exc_info=True)
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


@app.route('/api/generate_audio_for_story', methods=['POST'])
def api_generate_audio_for_story():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        card_id = data.get('card_id')
        story_id_str = data.get('story_id') # This will be the index as a string
        user_specified_voice = data.get('voice') # Optional, voice for this specific story

        if not card_id or story_id_str is None: # story_id can be "0"
            return jsonify({"error": "Missing card_id or story_id"}), 400

        current_card_data = session.get('current_card_data')
        if not current_card_data or current_card_data.get('card_id') != card_id:
            app.logger.error(f"Card data not found in session for card_id: {card_id} or mismatch. Session: {session.get('current_card_data')}")
            return jsonify({"error": "Card data not found in session or card_id mismatch. Please generate stories first."}), 404
        
        try:
            story_idx = int(story_id_str)
            story_detail = current_card_data['stories_details'][story_idx]
        except (ValueError, IndexError):
            app.logger.error(f"Invalid story_id: {story_id_str} for card_id: {card_id}")
            return jsonify({"error": "Invalid story_id"}), 400

        story_text = story_detail.get("text")
        story_title = story_detail.get("title", "A story") # Use title if available
        language = current_card_data.get("language")

        combined_text_for_tts = f"{story_title}. {story_text}"

        # Determine TTS voice parameters
        tts_params = GOOGLE_TTS_VOICE_PARAMS.get(language, GOOGLE_TTS_VOICE_PARAMS.get(language.split('-')[0], GOOGLE_TTS_VOICE_PARAMS['default']))
        
        selected_voice_name = user_specified_voice
        if not selected_voice_name: # If user didn't specify for this story, check card-level voice
            selected_voice_name = current_card_data.get('voice_requested_for_card')
        
        if not selected_voice_name: # If still no voice, use default for language
            if isinstance(tts_params['name'], list):
                 selected_voice_name = tts_params['name'][0]
            else:
                 selected_voice_name = tts_params['name']
        
        app.logger.info(f"TTS for story {story_idx} of card {card_id}: lang='{language}', voice='{selected_voice_name}'")

        audio_card_folder_abs = os.path.join(WEB_AUDIO_OUTPUT_DIR_ABS, card_id)
        os.makedirs(audio_card_folder_abs, exist_ok=True)
        
        audio_filename = f"{story_idx}.mp3" # e.g., "0.mp3", "1.mp3"
        audio_output_path_abs = os.path.join(audio_card_folder_abs, audio_filename)
        
        success = synthesize_speech(
            text=combined_text_for_tts,
            language_code=language,
            voice_name=selected_voice_name,
            output_filename=audio_output_path_abs,
            audio_config_params=AUDIO_CONFIG['mp3'],
            ssml_gender_str=tts_params.get("ssml_gender", "NEUTRAL")
        )

        if not success:
            return jsonify({"error": "Speech synthesis failed for story"}), 500

        audio_web_url = f"/audio_files/{WEB_AUDIO_SERVE_ROOT_REL}/{card_id}/{audio_filename}"
        app.logger.info(f"Audio for story {story_idx} (card {card_id}) generated: {audio_output_path_abs}, URL: {audio_web_url}")

        return jsonify({
            "message": "Audio generated successfully for story!",
            "audio_web_url": audio_web_url,
            "card_id": card_id,
            "story_id": story_idx
        })

    except Exception as e:
        app.logger.error(f"Error in /api/generate_audio_for_story: {e}", exc_info=True)
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


@app.route('/api/create_card_file', methods=['POST'])
def api_create_card_file():
    try:
        # card_id is expected to be the numeric string like "000000" from the session
        current_card_data = session.get('current_card_data')
        if not current_card_data:
            return jsonify({"error": "No card data found in session. Please generate stories first."}), 400

        card_id = current_card_data.get('card_id') # This will be "000000", "000001", etc.
        if not card_id:
            return jsonify({"error": "Card ID not found in session data."}), 400

        # Construct filename with "card_" prefix
        output_filename = f"card_{card_id}.json" # e.g., card_000000.json
        output_filepath = os.path.join(STORIES_OUTPUT_DIR, output_filename)

        # Prepare data for JSON output, ensuring it matches card_000000.json structure
        # The top-level "id" field should be the numeric card_id string
        output_data = {
            "id": card_id, 
            "character": current_card_data.get("character"),
            "location": current_card_data.get("context_location"),
            "stories": []
        }

        for story_detail in current_card_data['stories_details']:
            word_count = story_detail.get('validation', {}).get('word_count', current_card_data.get('num_words')) # Fallback to target
            
            output_data['stories'].append({
                "id": story_detail['story_number'], # Use 1-indexed story_number as integer
                "title": story_detail['title'],
                "tone": story_detail['tone'],
                "length_words": word_count, # Added actual word count per story
                "text": story_detail['text']
            })
        
        # File naming: use the card_id to ensure uniqueness and consistency
        # The batch pipeline expects files like card_000000.json. We'll use card_<card_id>.json
        card_file_name = f"card_{current_card_data['card_id']}.json"
        card_json_path_abs = os.path.join(STORIES_OUTPUT_DIR, card_file_name)
        
        with open(card_json_path_abs, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=4)
        
        app.logger.info(f"Card file created: {card_json_path_abs}")

        # Optionally, clear session data for this card after saving
        # session.pop('current_card_data', None)

        return jsonify({
            "message": "Card file created successfully!",
            "card_file_path": card_json_path_abs, # Server-side path
            "card_file_name": card_file_name
        })

    except Exception as e:
        app.logger.error(f"Error in /api/create_card_file: {e}", exc_info=True)
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


# Old endpoints are removed as their functionality is covered by the new ones.
# @app.route('/api/create_story_and_audio', methods=['POST']) ... (Removed)
# @app.route('/api/generate_story_only', methods=['POST']) ... (Removed)

if __name__ == '__main__':
    # Ensure the app is run with a debugger if needed, and specify host/port
    # For development, Flask's built-in server is fine.
    # For production, use a proper WSGI server like Gunicorn or uWSGI.
    app.run(debug=True, host='0.0.0.0', port=5001)
