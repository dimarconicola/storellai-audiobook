document.addEventListener('DOMContentLoaded', function () {
    const storyForm = document.getElementById('storyForm');
    const loadingDiv = document.getElementById('loading');
    const resultsDiv = document.getElementById('results');
    const storyOutput = document.getElementById('storyOutput');
    const audioOutput = document.getElementById('audioOutput');
    const errorOutput = document.getElementById('errorOutput');

    storyForm.addEventListener('submit', async function (event) {
        event.preventDefault();

        loadingDiv.style.display = 'block';
        resultsDiv.style.display = 'none';
        storyOutput.textContent = '';
        audioOutput.innerHTML = '';
        errorOutput.textContent = '';

        const formData = new FormData(storyForm);
        const data = {
            age: parseInt(formData.get('age')),
            character: formData.get('character'), // New field
            context_location: formData.get('context_location'), // New field
            num_words: parseInt(formData.get('words')),
            language: formData.get('language'),
            voice: formData.get('voice') || null // Send null if empty
        };

        try {
            const response = await fetch('/api/create_story_and_audio', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            });

            loadingDiv.style.display = 'none';
            resultsDiv.style.display = 'block';

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `Server error: ${response.status}`);
            }

            const result = await response.json();

            if (result.story_text) {
                storyOutput.textContent = result.story_text;
            } else {
                storyOutput.textContent = "Story text not available.";
            }

            if (result.audio_file_path) {
                // Construct the URL to serve the audio file.
                // This assumes your Flask app has a route to serve files from the 'src/audio' directory.
                // For example, if audio files are in 'src/audio/web_generated_stories/<filename>.mp3'
                // and your Flask app serves 'src/audio' at '/audio_files/',
                // the path might be '/audio_files/web_generated_stories/...'
                // We need to adjust this based on how app.py serves the audio.
                // For now, let's assume a relative path that works with a potential static route.

                // The path returned by the API is an absolute server path.
                // We need to make it a URL accessible by the browser.
                // A simple way is to have the backend return a web-accessible URL.
                // Or, if the files are within a 'static' subfolder of 'web_interface',
                // or if Flask is configured to serve 'src/audio', we can construct it.

                // Let's assume the backend returns a path like: "web_generated_stories/unique_id/story.mp3"
                // and that 'src/audio' is the base for these.
                // We'll need a Flask route to serve these files.

                const audioPlayer = document.createElement('audio');
                audioPlayer.controls = true;
                // The `result.audio_file_path` from the backend is currently an OS path.
                // We need a URL. Let's assume the backend will provide a web-accessible URL
                // or a relative path that can be resolved by a Flask route.
                // For now, we'll use a placeholder and log the path.
                
                // If Flask serves 'src/audio' as '/audio_files', and the path is like 'web_generated_stories/story_id/audio.mp3'
                // then src would be `/audio_files/web_generated_stories/story_id/audio.mp3`
                // The current `result.audio_file_path` is an absolute OS path.
                // We need to modify app.py to return a web-accessible path.

                // For now, let's assume app.py will be modified to return a path like:
                // /audio_files/web_generated_stories/some_unique_id/audio.mp3
                // And that a route @app.route('/audio_files/<path:filename>') exists.

                // If result.audio_web_url is provided by the backend:
                if (result.audio_web_url) {
                    audioPlayer.src = result.audio_web_url;
                    audioOutput.appendChild(audioPlayer);
                    const downloadLink = document.createElement('a');
                    downloadLink.href = result.audio_web_url;
                    downloadLink.textContent = 'Download Audiobook';
                    downloadLink.setAttribute('download', '');
                    audioOutput.appendChild(document.createElement('br'));
                    audioOutput.appendChild(downloadLink);
                } else if (result.audio_file_path) {
                     // Fallback if audio_web_url is not provided, try to guess
                    console.warn("audio_web_url not provided, attempting to construct. This might fail.");
                    console.log("Raw audio_file_path from server:", result.audio_file_path);
                    // This part needs a robust solution in app.py to serve the file
                    // and provide a correct URL.
                    audioOutput.textContent = `Audio generated at: ${result.audio_file_path}. Playback via browser requires server to serve this path.`;
                } else {
                    audioOutput.textContent = "Audio file path not available.";
                }

            } else {
                audioOutput.textContent = "Audio generation failed or path not returned.";
            }

            if(result.error) {
                errorOutput.textContent = `Error: ${result.error}`;
            }

        } catch (error) {
            console.error('Error:', error);
            loadingDiv.style.display = 'none';
            resultsDiv.style.display = 'block'; // Show results div to display the error
            errorOutput.textContent = `An error occurred: ${error.message}. Check the console for details.`;
        }
    });
});
