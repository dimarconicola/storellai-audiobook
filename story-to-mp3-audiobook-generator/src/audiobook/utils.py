def read_json_file(file_path):
    import json
    with open(file_path, 'r') as file:
        return json.load(file)

def write_json_file(file_path, data):
    import json
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def create_audio_directory(audio_path):
    import os
    if not os.path.exists(audio_path):
        os.makedirs(audio_path)

def log_message(message):
    import logging
    logging.basicConfig(level=logging.INFO)
    logging.info(message)