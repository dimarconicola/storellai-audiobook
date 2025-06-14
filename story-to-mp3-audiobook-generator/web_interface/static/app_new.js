document.addEventListener('DOMContentLoaded', function () {
    const storyForm = document.getElementById('storyForm');
    const loadingDiv = document.getElementById('loading');
    const storyValidationDiv = document.getElementById('storyValidation');
    const audioGenerationDiv = document.getElementById('audioGeneration');
    const resultsDiv = document.getElementById('results');
    
    // Elements for story validation
    const validationStatus = document.getElementById('validationStatus');
    const storyOutput = document.getElementById('storyOutput');
    const approveStoryBtn = document.getElementById('approveStory');
    const editStoryBtn = document.getElementById('editStory');
    const regenerateStoryBtn = document.getElementById('regenerateStory');
    
    // Elements for story editing
    const storyEditor = document.getElementById('storyEditor');
    const storyTextarea = document.getElementById('storyTextarea');
    const saveStoryEditBtn = document.getElementById('saveStoryEdit');
    const cancelEditBtn = document.getElementById('cancelEdit');
    
    // Elements for final results
    const finalStoryOutput = document.getElementById('finalStoryOutput');
    const audioOutput = document.getElementById('audioOutput');
    const errorOutput = document.getElementById('errorOutput');

    let currentStoryData = null;

    // Reset UI to initial state
    function resetUI() {
        loadingDiv.style.display = 'none';
        storyValidationDiv.style.display = 'none';
        audioGenerationDiv.style.display = 'none';
        resultsDiv.style.display = 'none';
        storyEditor.style.display = 'none';
        errorOutput.textContent = '';
        currentStoryData = null;
    }

    // Show error message
    function showError(message) {
        resetUI();
        errorOutput.textContent = message;
        resultsDiv.style.display = 'block';
    }

    // Generate validation status HTML
    function generateValidationHTML(validation) {
        let overallStatus = 'success';
        let validationItems = [];

        // Word count check
        if (validation.word_count_ok) {
            validationItems.push(`<div class="validation-item pass">✓ Word count: ${validation.word_count}/${validation.target_word_count} (within range)</div>`);
        } else {
            validationItems.push(`<div class="validation-item warning">⚠ Word count: ${validation.word_count}/${validation.target_word_count} (outside target range)</div>`);
            overallStatus = 'warning';
        }

        // Ending check
        if (validation.ends_properly) {
            validationItems.push(`<div class="validation-item pass">✓ Story ends properly with punctuation</div>`);
        } else {
            validationItems.push(`<div class="validation-item fail">✗ Story doesn't end properly (missing punctuation)</div>`);
            overallStatus = 'warning';
        }

        // Minimum length check
        if (validation.min_length_ok) {
            validationItems.push(`<div class="validation-item pass">✓ Story meets minimum length requirement</div>`);
        } else {
            validationItems.push(`<div class="validation-item fail">✗ Story is too short</div>`);
            overallStatus = 'warning';
        }

        const statusClass = overallStatus === 'success' ? 'success' : 'warning';
        const statusMessage = overallStatus === 'success' ? 
            '✓ Story looks good! You can approve it or make edits if needed.' : 
            '⚠ Story needs attention. Please review and edit if necessary.';

        return `<div class="${statusClass}">${statusMessage}</div>${validationItems.join('')}`;
    }

    // Step 1: Generate story only
    storyForm.addEventListener('submit', async function (event) {
        event.preventDefault();
        resetUI();
        loadingDiv.style.display = 'block';

        const formData = new FormData(storyForm);
        const data = {
            age: parseInt(formData.get('age')),
            character: formData.get('character'),
            context_location: formData.get('context_location'),
            num_words: parseInt(formData.get('words')),
            language: formData.get('language'),
            voice: formData.get('voice') || null
        };

        try {
            const response = await fetch('/api/generate_story_only', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            });

            loadingDiv.style.display = 'none';

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `Server error: ${response.status}`);
            }

            const result = await response.json();
            currentStoryData = result;

            // Show validation UI
            validationStatus.innerHTML = generateValidationHTML(result.validation);
            storyOutput.textContent = result.story_text;
            storyValidationDiv.style.display = 'block';

        } catch (error) {
            showError(`Error generating story: ${error.message}`);
        }
    });

    // Approve story and generate audio
    approveStoryBtn.addEventListener('click', async function() {
        if (!currentStoryData) return;
        
        storyValidationDiv.style.display = 'none';
        audioGenerationDiv.style.display = 'block';

        await generateAudio(currentStoryData.story_text);
    });

    // Edit story
    editStoryBtn.addEventListener('click', function() {
        if (!currentStoryData) return;
        
        storyTextarea.value = currentStoryData.story_text;
        storyEditor.style.display = 'block';
    });

    // Save edited story and generate audio
    saveStoryEditBtn.addEventListener('click', async function() {
        const editedText = storyTextarea.value.trim();
        if (!editedText) {
            alert('Please enter story text');
            return;
        }

        currentStoryData.story_text = editedText;
        storyEditor.style.display = 'none';
        storyValidationDiv.style.display = 'none';
        audioGenerationDiv.style.display = 'block';

        await generateAudio(editedText);
    });

    // Cancel editing
    cancelEditBtn.addEventListener('click', function() {
        storyEditor.style.display = 'none';
    });

    // Regenerate story
    regenerateStoryBtn.addEventListener('click', function() {
        // Trigger form submission again
        storyForm.dispatchEvent(new Event('submit'));
    });

    // Generate audio from approved/edited story
    async function generateAudio(storyText) {
        if (!currentStoryData) return;

        const audioData = {
            session_id: currentStoryData.session_id,
            story_text: storyText,
            character_idea: currentStoryData.character_idea,
            context_location_idea: currentStoryData.context_location_idea,
            age: currentStoryData.age,
            num_words: currentStoryData.num_words,
            language: currentStoryData.language,
            voice: currentStoryData.voice
        };

        try {
            const response = await fetch('/api/generate_audio_from_story', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            });

            audioGenerationDiv.style.display = 'none';

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `Server error: ${response.status}`);
            }

            const result = await response.json();

            // Show final results
            finalStoryOutput.textContent = result.story_text;
            
            if (result.audio_web_url) {
                const audioPlayer = document.createElement('audio');
                audioPlayer.controls = true;
                audioPlayer.src = result.audio_web_url;
                audioOutput.innerHTML = '';
                audioOutput.appendChild(audioPlayer);
                
                const downloadLink = document.createElement('a');
                downloadLink.href = result.audio_web_url;
                downloadLink.textContent = 'Download Audiobook';
                downloadLink.setAttribute('download', '');
                audioOutput.appendChild(document.createElement('br'));
                audioOutput.appendChild(downloadLink);
            }

            resultsDiv.style.display = 'block';

        } catch (error) {
            showError(`Error generating audio: ${error.message}`);
        }
    }
});
