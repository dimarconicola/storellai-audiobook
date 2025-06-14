document.addEventListener('DOMContentLoaded', function () {
    const storyForm = document.getElementById('storyForm');
    const loadingDiv = document.getElementById('loading');
    const storyValidationDiv = document.getElementById('storyValidation');
    const audioGenerationDiv = document.getElementById('audioGeneration');
    const resultsDiv = document.getElementById('results');
    
    // Elements for story validation
    const validationStatus = document.getElementById('validationStatus');
    const storyOutput = document.getElementById('storyOutput');
    const storyTitleOutput = document.getElementById('storyTitleOutput'); // Added for the title display
    const approveStoryBtn = document.getElementById('approveStory');
    const editStoryBtn = document.getElementById('editStory');
    const regenerateStoryBtn = document.getElementById('regenerateStory');
    const storyControls = document.querySelector('.story-controls'); // Get the div
    
    // Elements for story editing
    const storyEditor = document.getElementById('storyEditor');
    const storyTextarea = document.getElementById('storyTextarea');
    const saveStoryEditBtn = document.getElementById('saveStoryEdit');
    const cancelEditBtn = document.getElementById('cancelEdit');
    
    // Elements for final results
    // const finalStoryOutput = document.getElementById('finalStoryOutput'); // Not used, can be removed
    const audioOutput = document.getElementById('audioOutput');
    const errorOutput = document.getElementById('errorOutput');

    // Tone selection
    const numStoriesInput = document.getElementById('num_stories');
    const toneSelectionArea = document.getElementById('toneSelectionArea');
    const availableTones = ['calmo', 'avventuroso', 'divertente', 'misterioso', 'tenero', 'random']; // Add 'random'

    // Card creation
    const cardCreationControls = document.getElementById('cardCreationControls');
    const createCardFileBtn = document.getElementById('createCardFileBtn');

    let currentStoryData = null; // Holds data for single story flow or the selected story from multiple
    let allGeneratedStoriesData = null; // Holds data for all stories when multiple are generated

    // Reset UI to initial state
    function resetUI() {
        loadingDiv.style.display = 'none';
        storyValidationDiv.style.display = 'none';
        audioGenerationDiv.style.display = 'none';
        resultsDiv.style.display = 'none';
        storyEditor.style.display = 'none';
        storyControls.style.display = 'none'; // Hide story controls
        // Remove back button specifically if it exists within storyControls
        const backBtn = document.getElementById('backToStoryListBtn');
        if (backBtn && backBtn.parentElement === storyControls) {
            backBtn.remove();
        }
        cardCreationControls.style.display = 'none'; // Hide card creation controls
        errorOutput.textContent = '';
        currentStoryData = null;
        allGeneratedStoriesData = null;
        storyTitleOutput.style.display = 'none'; // Hide title on reset
        storyTitleOutput.textContent = ''; // Clear title on reset
        storyOutput.style.display = 'none'; // Ensure single story output is hidden
        validationStatus.innerHTML = ''; // Clear previous validation/story list
    }

    // Show error message
    function showError(message) {
        resetUI(); // Reset most of UI
        errorOutput.textContent = message;
        resultsDiv.style.display = 'block'; // Show results div to display the error
        loadingDiv.style.display = 'none';
        audioGenerationDiv.style.display = 'none';
    }
    
    // Update tone selection inputs based on number of stories
    function updateToneSelectionUI() {
        const numStories = parseInt(numStoriesInput.value) || 1;
        toneSelectionArea.innerHTML = ''; // Clear previous inputs

        if (numStories > 0) {
            const header = document.createElement('h3');
            header.textContent = 'Select Tone for Each Story:';
            header.style.marginBottom = '10px';
            toneSelectionArea.appendChild(header);
        }

        for (let i = 0; i < numStories; i++) {
            const storyToneDiv = document.createElement('div');
            storyToneDiv.style.marginBottom = '8px';
            storyToneDiv.style.display = 'flex';
            storyToneDiv.style.alignItems = 'center';

            const label = document.createElement('label');
            label.htmlFor = `tone_story_${i + 1}`;
            label.textContent = `Tone for Story ${i + 1}:`;
            label.style.marginRight = '10px';
            label.style.minWidth = '150px';


            const select = document.createElement('select');
            select.id = `tone_story_${i + 1}`;
            select.name = `tone_story_${i + 1}`;
            select.className = 'tone-select'; // Add a class for easy selection

            availableTones.forEach(tone => {
                const option = document.createElement('option');
                option.value = tone;
                option.textContent = tone.charAt(0).toUpperCase() + tone.slice(1); // Capitalize
                select.appendChild(option);
            });
            // Set default to random for subsequent stories if more than one
            if (i > 0) {
                select.value = 'random';
            } else {
                 select.value = availableTones[0]; // Default to first tone for the first story
            }


            storyToneDiv.appendChild(label);
            storyToneDiv.appendChild(select);
            toneSelectionArea.appendChild(storyToneDiv);
        }
    }
    
    // Initialize tone selection UI on page load and when num_stories changes
    numStoriesInput.addEventListener('change', updateToneSelectionUI);
    updateToneSelectionUI(); // Initial call


    // Generate validation status HTML
    function generateValidationHTML(validation, storyTitle = "Story") {
        let overallStatus = 'success';
        let validationItems = [];

        if (!validation) { // Handle cases where validation might be missing
            return '<div class="warning">Validation data not available.</div>';
        }

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
        
        // Tone display
        if (validation.tone) {
             validationItems.push(`<div class="validation-item info">Tone: ${validation.tone}</div>`);
        }


        const statusClass = overallStatus === 'success' ? 'success' : 'warning';
        const statusMessage = overallStatus === 'success' ? 
            `✓ ${storyTitle} looks good! You can approve it or make edits if needed.` : 
            `⚠ ${storyTitle} needs attention. Please review and edit if necessary.`;

        return `<div class="${statusClass}">${statusMessage}</div>${validationItems.join('')}`;
    }

    // Display multiple stories with selection interface
    function displayMultipleStories(dataToDisplay) { // dataToDisplay is allGeneratedStoriesData
        // allGeneratedStoriesData is already set globally, but good to be explicit if passing data around
        const stories = dataToDisplay.stories;
        const current_session_id = dataToDisplay.session_id; // session_id is now correctly mapped here
        
        // Clear any existing "Back to List" button from storyControls if it was added previously
        // This is a safeguard, though the button is typically removed or hidden with storyControls
        const existingGlobalBackBtn = document.getElementById('backToStoryListBtn');
        if (existingGlobalBackBtn && existingGlobalBackBtn.parentElement === storyControls) {
            existingGlobalBackBtn.remove();
        }
        
        let storiesHTML = `
            <div class="multiple-stories-header">
                <h3>📚 Generated ${stories.length} Stories</h3>
                <p>Review the stories below. You can select one to view, edit, and generate audio, or create a batch card file with all stories.</p>
            </div>
        `;
        
        stories.forEach((story, index) => {
            const storyNumber = story.story_number || (index + 1);
            // Use story.title (LLM generated title) if available, otherwise fallback.
            const displayableTitle = story.title || `Story ${storyNumber}`;
            // Pass the best title to validation HTML generator
            const validationHTML = generateValidationHTML(story.validation, displayableTitle); 
            const toneDisplay = story.tone ? ` (Tone: ${story.tone})` : '';
            
            storiesHTML += `
                <div class="story-option" data-story-index="${index}">
                    <div class="story-header">
                        <h4>${displayableTitle}${toneDisplay}</h4>
                        <button class="select-story-btn" data-story-index="${index}">View & Edit/Listen</button>
                    </div>
                    <div class="story-validation">${validationHTML}</div>
                    <div class="story-preview">${story.text}</div>
                </div>
            `;
        });
        
        validationStatus.innerHTML = storiesHTML;
        storyTitleOutput.style.display = 'none'; // Ensure single story title is hidden INITIALLY when list is shown
        storyOutput.style.display = 'none';      // Ensure single story output is hidden
        storyControls.style.display = 'none';    // Ensure single story controls are hidden
        storyValidationDiv.style.display = 'block';
        cardCreationControls.style.display = 'block'; // Show card creation button
        
        document.querySelectorAll('.select-story-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const storyIndex = parseInt(this.getAttribute('data-story-index')); // This is 0-indexed
                const selectedStory = dataToDisplay.stories[storyIndex]; // Correctly uses 0-indexed storyIndex
                
                currentStoryData = { 
                    // Carry over initial form data from the main data object
                    age: dataToDisplay.age, 
                    character: dataToDisplay.character,
                    context_location: dataToDisplay.context_location,
                    num_words: dataToDisplay.num_words,
                    language: dataToDisplay.language,
                    voice: dataToDisplay.voice,
                    // Story specific data
                    story_text: selectedStory.text,
                    story_title: selectedStory.title || `Story ${selectedStory.story_number || (storyIndex + 1)}`,
                    tone: selectedStory.tone, 
                    validation: selectedStory.validation,
                    session_id: current_session_id, // Use the session_id from the parent data object
                    selected_story_id: storyIndex.toString() // CRITICAL FIX: Store the 0-indexed storyIndex as a string
                };
                
                // Display the selected story's details
                validationStatus.innerHTML = generateValidationHTML(selectedStory.validation, currentStoryData.story_title);
                storyTitleOutput.textContent = currentStoryData.story_title; 
                storyTitleOutput.style.display = 'block'; // Ensure title is visible for selected story
                storyOutput.textContent = selectedStory.text;
                storyOutput.style.display = 'block';
                
                // Manage controls
                storyControls.style.display = 'flex';
                cardCreationControls.style.display = 'none'; 

                // Remove any old "Back to List" button before adding a new one
                const existingBackBtn = document.getElementById('backToStoryListBtn');
                if (existingBackBtn) {
                    existingBackBtn.remove();
                }

                // Add "Back to Story List" button to the storyControls div
                if (allGeneratedStoriesData && allGeneratedStoriesData.stories.length > 1) {
                    const backBtn = document.createElement('button');
                    backBtn.id = 'backToStoryListBtn';
                    backBtn.textContent = '← Back to Story List';
                    backBtn.className = 'control-button'; 
                    backBtn.style.marginRight = 'auto'; // Pushes other buttons to the right

                    backBtn.addEventListener('click', function() {
                        displayMultipleStories(allGeneratedStoriesData); 
                        // displayMultipleStories handles hiding/showing relevant sections
                    });
                    storyControls.insertBefore(backBtn, storyControls.firstChild);
                }
            });
        });
    }
    
    // Step 1: Generate story or multiple stories
    storyForm.addEventListener('submit', async function (event) {
        event.preventDefault();
        resetUI();
        loadingDiv.style.display = 'block';

        const formData = new FormData(storyForm);
        // ... (formData processing) ...
        const data = {
            age: parseInt(formData.get('age')),
            character: formData.get('character'),
            context_location: formData.get('context_location'),
            num_words: parseInt(formData.get('words')),
            language: formData.get('language'),
            voice: formData.get('voice') || null,
            num_stories: parseInt(formData.get('num_stories')),
            tones: (() => {
                const num = parseInt(formData.get('num_stories'));
                const t = [];
                if (num > 0) {
                    for (let i = 0; i < num; i++) {
                        t.push(document.getElementById(`tone_story_${i + 1}`).value);
                    }
                }
                return t;
            })()
        };

        try {
            const response = await fetch('/api/generate_stories', { 
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            });

            loadingDiv.style.display = 'none';

            if (!response.ok) {
                let errorMsg = `Server error: ${response.status}`;
                try {
                    const errorData = await response.json();
                    errorMsg = errorData.error || errorMsg;
                } catch (e) { /* Ignore if error response isn't json */ }
                throw new Error(errorMsg);
            }

            const result = await response.json();

            // CRITICAL CHECK: Ensure session_id (which is card_id from backend) is present in the result
            if (!result.card_id) { // MODIFIED: Check for card_id instead of session_id
                console.error("CRITICAL: card_id (as session_id) is missing from server result.", result);
                showError("Critical error: Story generation response from server is incomplete (missing session/card ID). Cannot proceed. Please try again.");
                return; // Stop further processing
            }

            // Store the full result, including card_id (as session_id) and original params
            allGeneratedStoriesData = {
                ...result, // Spread the original result
                session_id: result.card_id, // Explicitly map card_id to session_id for frontend use
                // Ensure original form parameters are consistently stored from the response
                age: result.age, 
                character: result.character,
                context_location: result.context_location,
                num_words: result.num_words,
                language: result.language, // CRITICAL: Ensure language is captured here
                voice: result.voice_requested_for_card, // Use the key from backend response
                num_stories_requested: result.num_stories_requested,
                tones_requested: result.tones_requested
            };

            if (result.stories && result.stories.length > 1) {
                displayMultipleStories(allGeneratedStoriesData); // Pass the augmented data
            } else if (result.stories && result.stories.length === 1) {
                currentStoryData = { 
                    // Parameters from the original form submission for this session
                    // These should ideally come from an echo in allGeneratedStoriesData if backend provides them
                    // For now, let's assume they are in allGeneratedStoriesData or reconstruct if needed.
                    age: allGeneratedStoriesData.age, 
                    character: allGeneratedStoriesData.character,
                    context_location: allGeneratedStoriesData.context_location,
                    num_words: allGeneratedStoriesData.num_words,
                    language: allGeneratedStoriesData.language, // CRITICAL: Ensure language is populated
                    voice: allGeneratedStoriesData.voice,
                    
                    // Specifics for the single story generated
                    story_text: result.stories[0].text,
                    story_title: result.stories[0].title || "Generated Story",
                    tone: result.stories[0].tone,
                    validation: result.stories[0].validation,
                    session_id: allGeneratedStoriesData.session_id, // Use the mapped session_id
                    selected_story_id: "0" // For a single story, its index is always 0
                };
                validationStatus.innerHTML = generateValidationHTML(currentStoryData.validation, currentStoryData.story_title);
                storyTitleOutput.textContent = currentStoryData.story_title;
                storyTitleOutput.style.display = 'block';
                storyOutput.textContent = currentStoryData.story_text;
                storyOutput.style.display = 'block';
                storyControls.style.display = 'flex';
                storyValidationDiv.style.display = 'block';
                cardCreationControls.style.display = 'block'; 
            } else {
                throw new Error("Received unexpected response format from server (no stories found).");
            }

        } catch (error) {
            showError(`Error generating story/stories: ${error.message}`);
        }
    });

    // Approve story and generate audio (for single story view)
    approveStoryBtn.addEventListener('click', async function() {
        if (!currentStoryData || !currentStoryData.story_text) {
            showError("No story selected or story text is missing.");
            return;
        }
        
        storyControls.style.display = 'none';
        audioGenerationDiv.style.display = 'block';
        resultsDiv.style.display = 'none';

        const storyIdForAudio = currentStoryData.selected_story_id || (currentStoryData.stories && currentStoryData.stories.length > 0 ? currentStoryData.stories[0].id : "0");
        console.log(`[Debug AppJS] approveStoryBtn: currentStoryData.selected_story_id: ${currentStoryData.selected_story_id}, calculated storyIdForAudio: ${storyIdForAudio}`); // DEBUG LOG
        await generateAudio(currentStoryData.story_text, currentStoryData.story_title, currentStoryData.tone, storyIdForAudio);
    });

    // Edit story (for single story view)
    editStoryBtn.addEventListener('click', function() {
        if (!currentStoryData || !currentStoryData.story_text) {
             showError("No story selected to edit.");
            return;
        }
        // Ensure the main story title display is visible and has content
        storyTitleOutput.textContent = currentStoryData.story_title;
        storyTitleOutput.style.display = 'block'; // MAKE SURE THIS IS BLOCK

        // Hide the read-only story text display
        storyOutput.style.display = 'none';
        
        // Optionally hide validation status during edit for a cleaner interface
        // validationStatus.style.display = 'none'; 

        // Show the editor
        storyTextarea.value = currentStoryData.story_text;
        storyEditor.style.display = 'block';
        
        // Hide the story action buttons (Approve, Edit, Regenerate)
        storyControls.style.display = 'none';
    });

    // Save edited story and generate audio (for single story view)
    saveStoryEditBtn.addEventListener('click', async function() {
        const editedText = storyTextarea.value.trim();
        if (!editedText) {
            alert('Please enter story text');
            return;
        }

        if (!currentStoryData) {
            showError("Cannot save edit, story data is missing.");
            return;
        }

        currentStoryData.story_text = editedText; // Update story text in memory

        // Hide editor
        storyEditor.style.display = 'none';

        // Update and show the main story display elements
        storyTitleOutput.textContent = currentStoryData.story_title; // Title should be correct
        storyTitleOutput.style.display = 'block'; // Ensure title is visible
        storyOutput.textContent = currentStoryData.story_text; // Show edited text in read-only view
        storyOutput.style.display = 'block'; // Make read-only view visible
        
        // Re-display validation status. 
        // Note: Validation data is from the original generation and may not reflect edits.
        if (currentStoryData.validation) {
             validationStatus.innerHTML = generateValidationHTML(currentStoryData.validation, currentStoryData.story_title) + "<div class='info' style='margin-top:5px;'>Note: Validation data shown is for the story prior to this edit.</div>";
        } else {
            validationStatus.innerHTML = "<div class='info'>Story edited. Validation data may not reflect recent changes.</div>";
        }
        validationStatus.style.display = 'block';

        // Show story controls again
        storyControls.style.display = 'flex';
        
        // Proceed to generate audio for the edited story
        audioGenerationDiv.style.display = 'block'; // Show "Generating audio..."
        resultsDiv.style.display = 'none'; 

        const storyIdForAudio = currentStoryData.selected_story_id || (currentStoryData.stories && currentStoryData.stories.length > 0 ? currentStoryData.stories[0].id : "0");
        console.log(`[Debug AppJS] saveStoryEditBtn: currentStoryData.selected_story_id: ${currentStoryData.selected_story_id}, calculated storyIdForAudio: ${storyIdForAudio}`); // DEBUG LOG
        await generateAudio(editedText, currentStoryData.story_title, currentStoryData.tone, storyIdForAudio);
        // generateAudio will handle hiding audioGenerationDiv and showing resultsDiv.
        // The story display (title, text, validation, controls) will remain.
    });

    // Cancel editing
    cancelEditBtn.addEventListener('click', function() {
        storyEditor.style.display = 'none'; // Hide editor
        if (currentStoryData) { 
            // Restore the display of the story title, text, validation, and controls
            storyTitleOutput.textContent = currentStoryData.story_title; 
            storyTitleOutput.style.display = 'block'; // Ensure title is visible
            storyOutput.textContent = currentStoryData.story_text; // Show original/previous text
            storyOutput.style.display = 'block'; 
            
            // Re-show validation status for the current story
            if (currentStoryData.validation) {
                validationStatus.innerHTML = generateValidationHTML(currentStoryData.validation, currentStoryData.story_title);
            } else {
                validationStatus.innerHTML = ""; // Clear if no validation
            }
            validationStatus.style.display = 'block';
            storyControls.style.display = 'flex'; 
        } else {
            // Fallback if currentStoryData is somehow lost, though unlikely if edit was active
            resetUI(); 
        }
    });

    // Regenerate story (triggers form submission)
    regenerateStoryBtn.addEventListener('click', function() {
        storyForm.dispatchEvent(new Event('submit'));
    });

    // Generate audio from approved/edited story
    async function generateAudio(storyText, storyTitle, storyTone, storyId = "0") { // MODIFIED: Default to "0"
        console.log(`[Debug AppJS] generateAudio function called with storyId: ${storyId}`); // DEBUG LOG
        if (!currentStoryData) {
            showError("Cannot generate audio: No current story data available. Please select or generate a story first.");
            audioGenerationDiv.style.display = 'none';
            return;
        }

        // CRITICAL CHECK for language in currentStoryData
        if (!currentStoryData.language || currentStoryData.language.trim() === "") {
            console.error("CRITICAL: Language is missing from currentStoryData.", currentStoryData);
            showError("Cannot generate audio: Language information is missing from current story data. Please try regenerating the story.");
            audioGenerationDiv.style.display = 'none';
            resultsDiv.style.display = 'block'; // Show results div to display the error
            return;
        }

        // Ensure session_id (card_id) is present
        if (!currentStoryData.session_id) {
            console.error("CRITICAL: session_id (card_id) is missing from currentStoryData.", currentStoryData);
            showError("Cannot generate audio: Session ID is missing. Please try regenerating the story.");
            audioGenerationDiv.style.display = 'none';
            resultsDiv.style.display = 'block';
            return;
        }

        const voiceForAudio = document.getElementById('voice').value || currentStoryData.voice || null;

        try {
            const response = await fetch('/api/generate_audio_for_story', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    card_id: currentStoryData.session_id, // Use session_id which is the card_id
                    story_id: storyId, // This is the 0-indexed ID of the story within the card
                    voice: voiceForAudio, // Pass the selected voice
                    // Language is not directly sent here as backend derives it from session/card data
                }),
            });

            audioGenerationDiv.style.display = 'none';

            if (!response.ok) {
                let errorMsg = `Server error: ${response.status}`;
                try {
                    const errorData = await response.json();
                    errorMsg = errorData.error || errorMsg;
                } catch (e) { /* Ignore */ }
                throw new Error(errorMsg);
            }

            const result = await response.json();
            
            // Ensure the audio player is correctly updated and displayed
            const audioPlayer = document.getElementById('audioPlayer');
            const audioSource = document.getElementById('audioSource');
            
            audioSource.src = result.audio_web_url;
            audioPlayer.load(); // Important to load the new source
            audioPlayer.style.display = 'block';
            
            // Update the final story display area (if it exists and is used)
            // For now, we assume the story text is already displayed in storyOutput
            // and title in storyTitleOutput.
            
            // Ensure the main story title and text are still visible
            storyTitleOutput.textContent = currentStoryData.story_title;
            storyTitleOutput.style.display = 'block';
            storyOutput.textContent = currentStoryData.story_text;
            storyOutput.style.display = 'block';

            // Show the results area which contains the audio player
            resultsDiv.style.display = 'block';
            // Hide story controls if audio generation was successful and we are in a "final" state for this story
            // storyControls.style.display = 'none'; 
            // Re-show story controls to allow further actions like re-editing or creating card file
            storyControls.style.display = 'flex';
            cardCreationControls.style.display = 'block'; // Also show card creation controls


        } catch (error) {
            showError(`Error generating audio: ${error.message}`);
            resultsDiv.style.display = 'block'; // Ensure results div is shown for error message
        }
    }

    // Create Card File
    createCardFileBtn.addEventListener('click', async function() {
        let dataForCardFileCreation;

        if (allGeneratedStoriesData && allGeneratedStoriesData.session_id) {
            dataForCardFileCreation = {
                session_id: allGeneratedStoriesData.session_id, // This is the card_id
            };
        } else if (currentStoryData && currentStoryData.session_id) { 
             dataForCardFileCreation = {
                session_id: currentStoryData.session_id, // This is the card_id
            };
        } else {
            showError("No stories generated or session ID is missing. Cannot create card file.");
            return;
        }

        loadingDiv.innerHTML = '<p>Creating card file...</p><div class="spinner"></div>';
        loadingDiv.style.display = 'block';
        cardCreationControls.style.display = 'none';

        try {
            const response = await fetch('/api/create_card_file', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(dataForCardFileCreation), // Contains session_id which is card_id
            });

            loadingDiv.style.display = 'none';
            loadingDiv.innerHTML = '<p>Generating story, please wait...</p><div class="spinner"></div>'; // Reset loading message

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `Server error: ${response.status}`);
            }

            const result = await response.json();
            // Show success message,
            validationStatus.innerHTML += `<div class="success-message" style="margin-top:15px; padding:10px; background-color:#e6ffed; border:1px solid #34c759;">✓ Card file created successfully: ${result.card_file_path}</div>`;

        } catch (error) {
            showError(`Error creating card file: ${error.message}`);
            cardCreationControls.style.display = 'block'; 
        }
    });
});
