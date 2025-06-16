import os
import openai
import random

# Ensure the OpenAI API key is set
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set.")
openai.api_key = api_key

# Story variation system (plot_seed might be overridden by title directive)
STORY_VARIATIONS = {
    "it": [
        {
            "plot_seed": "un problema da risolvere con creatività",
            "opening_style": "Inizia la storia mentre il personaggio sta già affrontando una situazione interessante",
            "narrative_approach": "Usa un tono vivace e diretto, come se stessi raccontando a un amico"
        },
        {
            "plot_seed": "un nuovo amico inaspettato da incontrare", 
            "opening_style": "Inizia con il personaggio che fa qualcosa di normale, poi succede qualcosa di inaspettato",
            "narrative_approach": "Usa molte domande retoriche per coinvolgere il lettore"
        },
        {
            "plot_seed": "una sfida da superare con coraggio",
            "opening_style": "Inizia con una descrizione del luogo, poi presenta il personaggio",
            "narrative_approach": "Concentrati sulle emozioni e sui pensieri del personaggio"
        },
        {
            "plot_seed": "un mistero da scoprire",
            "opening_style": "Inizia con un dialogo o un suono misterioso",
            "narrative_approach": "Crea suspense con dettagli curiosi e domande senza risposta immediate"
        },
        {
            "plot_seed": "un'avventura divertente e inaspettata",
            "opening_style": "Inizia con il personaggio che si sveglia o arriva in un posto nuovo",
            "narrative_approach": "Usa molto umorismo e situazioni buffe"
        },
        {
            "plot_seed": "una lezione importante da imparare",
            "opening_style": "Inizia mostrando il personaggio che commette un piccolo errore",
            "narrative_approach": "Racconta la storia come una favola con una morale chiara"
        },
        {
            "plot_seed": "un momento di aiutare qualcun altro",
            "opening_style": "Inizia con il personaggio che sente o vede qualcuno in difficoltà",
            "narrative_approach": "Enfatizza i sentimenti di gentilezza e empatia"
        },
        {
            "plot_seed": "una scoperta sorprendente da fare",
            "opening_style": "Inizia con il personaggio che esplora o cerca qualcosa",
            "narrative_approach": "Usa molte descrizioni sensoriali (vista, udito, olfatto)"
        },
        {
            "plot_seed": "un ostacolo da superare insieme agli altri",
            "opening_style": "Inizia presentando il personaggio insieme ad altri personaggi",
            "narrative_approach": "Concentrati sul lavoro di squadra e la collaborazione"
        },
        {
            "plot_seed": "una celebrazione o festa speciale",
            "opening_style": "Inizia con preparativi per qualcosa di speciale o festoso",
            "narrative_approach": "Usa un tono gioioso e celebrativo con molti colori e suoni"
        }
    ],
    "en": [
        {
            "plot_seed": "a problem to solve creatively",
            "opening_style": "Start the story while the character is already facing an interesting situation",
            "narrative_approach": "Use a lively and direct tone, as if telling a friend"
        },
        {
            "plot_seed": "an unexpected new friend to meet",
            "opening_style": "Start with the character doing something normal, then something unexpected happens",
            "narrative_approach": "Use many rhetorical questions to engage the reader"
        },
        {
            "plot_seed": "a challenge to overcome with courage", 
            "opening_style": "Start with a description of the place, then introduce the character",
            "narrative_approach": "Focus on the character's emotions and thoughts"
        },
        {
            "plot_seed": "a mystery to discover",
            "opening_style": "Start with a dialogue or mysterious sound",
            "narrative_approach": "Create suspense with curious details and unanswered questions"
        },
        {
            "plot_seed": "a fun and unexpected adventure",
            "opening_style": "Start with the character waking up or arriving somewhere new",
            "narrative_approach": "Use lots of humor and funny situations"
        },
        {
            "plot_seed": "an important lesson to learn",
            "opening_style": "Start by showing the character making a small mistake",
            "narrative_approach": "Tell the story like a fable with a clear moral"
        },
        {
            "plot_seed": "a moment of helping someone else",
            "opening_style": "Start with the character hearing or seeing someone in trouble",
            "narrative_approach": "Emphasize feelings of kindness and empathy"
        },
        {
            "plot_seed": "a surprising discovery to make",
            "opening_style": "Start with the character exploring or searching for something",
            "narrative_approach": "Use many sensory descriptions (sight, hearing, smell)"
        },
        {
            "plot_seed": "an obstacle to overcome together with others",
            "opening_style": "Start by introducing the character along with other characters",
            "narrative_approach": "Focus on teamwork and collaboration"
        },
        {
            "plot_seed": "a special celebration or party",
            "opening_style": "Start with preparations for something special or festive",
            "narrative_approach": "Use a joyful and celebratory tone with many colors and sounds"
        }
    ]
}

# Define available tones
STORY_TONES = ["calmo", "avventuroso", "divertente", "misterioso", "tenero"]

def get_random_tone():
    return random.choice(STORY_TONES)

def get_story_variation(language, story_number):
    """Get a variation for story diversity based on language and story number."""
    lang_code = language.split('-')[0].lower()
    variations = STORY_VARIATIONS.get(lang_code, STORY_VARIATIONS["en"])
    
    # Use story number to ensure different variations for each story
    variation_index = (story_number - 1) % len(variations)
    return variations[variation_index]


def generate_story_titles_from_llm(age: int, character_idea: str, context_location_idea: str, language: str, num_titles: int) -> list[str]:
    """
    Generates a list of diverse story titles using the LLM.
    """
    lang_code_short = language.split('-')[0]
    language_instruction = f"The story titles must be in {language} (e.g., for '{lang_code_short}')."
    
    avoid_themes_instruction_it = "Evita temi ESTREMAMENTE COMUNI o CLICHÉ."
    avoid_themes_instruction_en = "Avoid EXTREMELY COMMON or CLICHÉ themes."

    if lang_code_short == "it":
        title_gen_prompt = f"Sei un autore di storie per bambini CREATIVO. Per un bambino di {age} anni, devi generare {num_titles} titoli di storie COMPLETAMENTE DIVERSI l'uno dall'altro, ORIGINALI e CONCISI. Ogni titolo deve suggerire UNA SINGOLA, CHIARA avventura o situazione. {avoid_themes_instruction_it} Non combinare più idee di trama in un unico titolo. Le storie avranno come protagonista un personaggio descritto come '{character_idea}' che si trova in un ambiente simile a '{context_location_idea}'. Concentrati sulla massima diversità e unicità delle premesse narrative. Elenca solo i titoli, uno per riga, senza numeri o virgolette."
    else: # Default to English
        title_gen_prompt = f"You are a CREATIVE children's story writer. For a {age}-year-old child, you must generate {num_titles} COMPLETELY DIFFERENT, ORIGINAL, and CONCISE story titles. Each title must suggest A SINGLE, CLEAR adventure or situation. {avoid_themes_instruction_en} Do not combine multiple plot ideas into a single title. The stories will feature a character described as '{character_idea}' in a setting like '{context_location_idea}'. Focus on maximum diversity and uniqueness of narrative premises. List only the titles, one per line, without numbers or quotes."

    system_message = "You are an assistant that generates exceptionally creative, concise, and diverse story titles for children based on provided themes, avoiding clichés and compound ideas. Output only the titles, each on a new line."

    try:
        print(f"[OpenAI Title Gen] Generating {num_titles} titles. Prompt: {title_gen_prompt[:100]}...")
        completion = openai.chat.completions.create(
            model="gpt-3.5-turbo", 
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": title_gen_prompt}
            ],
            max_tokens=num_titles * 25,  # Increased slightly, e.g., 10-15 words per title
            temperature=0.9, # Slightly higher temperature for more creative/diverse titles
            n=1 # We want one set of num_titles
        )
        content = completion.choices[0].message.content.strip()
        titles = [title.strip() for title in content.split('\n') if title.strip() and len(title.strip()) > 3] # Ensure titles are not just empty or very short
        
        if not titles:
            print(f"[OpenAI Title Gen] Warning: No valid titles generated. LLM response: {content}")
            # Fallback: Create more descriptive fallback titles
            return [f"Avventura {i+1} per {character_idea[:20]}" if lang_code_short == "it" else f"Adventure {i+1} for {character_idea[:20]}" for i in range(num_titles)]

        # If fewer titles than requested, pad with more descriptive fallbacks
        if len(titles) < num_titles:
            print(f"[OpenAI Title Gen] Warning: Generated {len(titles)} titles, but {num_titles} were requested. Padding with descriptive fallbacks.")
            missing_count = num_titles - len(titles)
            for i in range(missing_count):
                fallback_title_text = f"Avventura Extra {i+1} per {character_idea[:20]}" if lang_code_short == "it" else f"Extra Adventure {i+1} for {character_idea[:20]}"
                titles.append(fallback_title_text)
        
        print(f"[OpenAI Title Gen] Generated titles: {titles[:num_titles]}")
        return titles[:num_titles] # Return the requested number of titles

    except Exception as e:
        print(f"[OpenAI Title Gen] Error generating story titles: {e}")
        # Fallback: Create more descriptive fallback titles in case of exception
        return [f"Titolo di Riserva {i+1} ({character_idea[:15]}) (Errore: {type(e).__name__})" if lang_code_short == "it" else f"Fallback Title {i+1} ({character_idea[:15]}) (Error: {type(e).__name__})" for i in range(num_titles)]


def _perform_basic_validation(story_text: str, target_num_words: int, tone: str, story_title: str = None) -> dict:
    """Performs basic validation checks on the generated story text."""
    if story_text.startswith("Error:"): # If story generation itself failed
        return {
            "word_count": 0,
            "target_word_count": target_num_words,
            "word_count_ok": False,
            "ends_properly": False,
            "min_length_ok": False,
            "tone": tone,
            "error_message": story_text 
        }

    word_count = len(story_text.split())
    # Word count: within 20% of target, or at least 10 words if target is very small
    min_acceptable_words = max(10, int(target_num_words * 0.6)) # Adjusted: more lenient lower bound
    max_acceptable_words = max(target_num_words + 75, int(target_num_words * 3.0)) # Adjusted: significantly more lenient upper bound
    
    word_count_ok = min_acceptable_words <= word_count <= max_acceptable_words
    
    # Ends properly (with a punctuation mark)
    ends_properly = story_text.endswith(('.', '!', '?'))
    
    # Minimum length (e.g., at least 50% of target, or a fixed minimum like 15 words)
    min_length_ok = word_count >= max(15, int(target_num_words * 0.4))

    return {
        "word_count": word_count,
        "target_word_count": target_num_words,
        "word_count_ok": word_count_ok,
        "ends_properly": ends_properly,
        "min_length_ok": min_length_ok,
        "tone": tone,
        "story_title": story_title, # Include the title in the validation data
        "error_message": None
    }

def generate_story_from_llm(age: int, character_idea: str, context_location_idea: str, num_words: int, language: str, tone: str = None, variation: dict = None, story_number: int = 1, story_title_directive: str = None):
    """
    Generates a single story using OpenAI, optionally driven by a specific title.
    Returns: story_content (str), actual_tone (str), validation_results (dict), final_story_title (str)
    """
    actual_tone = tone if tone and tone.lower() != "random" else get_random_tone()
    lang_code_short = language.split('-')[0]

    # Determine the final title early. If no directive, create a descriptive one.
    # This final_story_title will be used for prompts and returned.
    final_story_title = story_title_directive
    is_fallback_title_scenario = False # Flag to indicate if we are using a less-than-ideal title

    if not final_story_title or any(fb_part in final_story_title for fb_part in ["Fallback Title", "Titolo di Riserva", "Avventura", "Adventure"]):
        is_fallback_title_scenario = True
        # If the directive itself is a fallback, or no title, generate a more descriptive placeholder for the prompt
        # but the `final_story_title` will still be this fallback/placeholder if it came as a directive.
        # If no directive at all, create one.
        if not final_story_title:
            final_story_title = f"Una storia su {character_idea[:25]} ({actual_tone})" if lang_code_short == "it" else f"A story about {character_idea[:25]} ({actual_tone})"
    
    language_instruction = f"The story must be in {language} (e.g., for '{lang_code_short}')."
    if lang_code_short == "it":
        system_message = "Sei un narratore di storie per bambini esperto e MOLTO creativo. Scrivi storie coinvolgenti, adatte all'età, e che seguano ATTENTAMENTE le istruzioni sul tono e sulla trama, evitando cliché narrativi."
    else: # Default to English
        system_message = "You are an expert and VERY creative children's storyteller. Write engaging, age-appropriate stories that CAREFULLY follow instructions on tone and plot, avoiding narrative clichés."

    title_prompt_segment = ""
    special_instructions = ""

    # Construct special instructions based on the quality/nature of final_story_title
    if is_fallback_title_scenario:
        # This means the title from generate_story_titles_from_llm was a fallback, or no title was provided.
        # The prompt should encourage extreme creativity because the title itself isn't a strong creative seed.
        if lang_code_short == "it":
            special_instructions = f"NOTA SPECIALE (TITOLO GENERICO/DI RISERVA: '{final_story_title}'): Poiché il titolo fornito è generico, inventa una trama PARTICOLARMENTE ORIGINALE, SORPRENDENTE e COMPLETAMENTE INASPETTATA. EVITA ASSOLUTAMENTE scenari eccessivamente comuni o infantili (come il primo giorno di scuola, una semplice festa, la perdita di un giocattolo, sogni di viaggi sulla luna, o animali parlanti che aiutano in modo prevedibile) a meno che il personaggio '{character_idea}' o il contesto '{context_location_idea}' non lo suggeriscano in modo MOLTO specifico e originale. Sii AUDACE e CORAGGIOSO con la premessa. La storia deve essere UNICA e NON deve sembrare basata su un titolo generico."
        else:
            special_instructions = f"SPECIAL NOTE (GENERIC/FALLBACK TITLE: '{final_story_title}'): Because the provided title is generic, invent a PARTICULARLY ORIGINAL, SURPRISING, and COMPLETELY UNEXPECTED plot. ABSOLUTELY AVOID overly common or childish scenarios (like the first day of school, a simple party, losing a toy, dreams of moon trips, or predictably helpful talking animals) unless the character '{character_idea}' or context '{context_location_idea}' VERY specifically and originally suggest it. Be BOLD and BRAVE with the premise. The story must be UNIQUE and NOT feel like it's based on a generic title."
    else: # A specific, presumably creative, title was provided
        if lang_code_short == "it":
            special_instructions = f"REQUISITO FONDAMENTALE DELLA TRAMA: La storia deve concentrarsi ESCLUSIVAMENTE sugli eventi e le implicazioni del titolo fornito: '{final_story_title}'. NON introdurre scenari comuni non correlati (come il primo giorno di scuola, ecc.) a meno che il titolo stesso NON lo implichi ESPLICITAMENTE e DIRETTAMENTE. La trama deve essere un'interpretazione DIRETTA e IMMAGINATIVA di questo titolo UNICO."
        else:
            special_instructions = f"CRUCIAL PLOT REQUIREMENT: The story must focus EXCLUSIVELY on the events and implications of the provided title: '{final_story_title}'. Do NOT introduce unrelated common scenarios (like a first day of school, etc.) unless the title ITSELF EXPLICITLY and DIRECTLY implies such a scenario. The plot must be a DIRECT and IMAGINATIVE interpretation of this UNIQUE title."
    
    title_prompt_segment = special_instructions

    # Variation prompt (style guidance) - remains the same
    if variation:
        variation_prompt_segment = (
            f"STORY STYLE REQUIREMENTS (da applicare alla trama sopra definita):\\n"
            f"- OPENING STYLE: {variation['opening_style']}\\n"
            f"- NARRATIVE APPROACH: {variation['narrative_approach']}\\n"
            f"- AVOID starting with traditional phrases like 'C\'era una volta' or 'Once upon a time' unless the opening style specifically dictates it. Instead, follow the specific opening style above.\\n"
        )

    tone_instruction = f"The story MUST have a '{actual_tone}' tone. This means it should evoke feelings associated with '{actual_tone}'."

    user_prompt = (
        f"{language_instruction}\n\n"
        f"TARGET AUDIENCE: A {age}-year-old child.\n\n"
        f"CHARACTER IDEA: {character_idea}\n\n"
        f"CONTEXT/LOCATION IDEA: {context_location_idea}\n\n"
        f"IMPORTANT: The character and location descriptions above are for your reference only. Do NOT repeat or rephrase these descriptions verbatim in the story. Assume the reader already knows these details. Only mention character or location traits if they are relevant to the plot or action. Focus on new events, actions, and dialogue.\n\n"
        f"{title_prompt_segment}\n\n"
        f"{variation_prompt_segment}\n\n"
        f"{tone_instruction}\n\n"
        f"STORY LENGTH: Approximately {num_words} words. Focus on a complete, coherent, and imaginative narrative that fully develops the premise of the given title, rather than exact word count.\n\n"
        f"Please write the story now."
    )

    print(f"[OpenAI Story Gen {story_number}] Tone: {actual_tone}. Final Title for Prompt: '{final_story_title}'. Prompt: {user_prompt[:200]}...")

    try:
        completion = openai.chat.completions.create(
            model="gpt-3.5-turbo", 
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=max(500, int(num_words * 6)), 
            temperature=0.75,
        )
        story_content = completion.choices[0].message.content.strip()
        
        # final_story_title was determined earlier and is what was used in the prompt if it was a good one.
        # It's also what we return.
        validation_results = _perform_basic_validation(story_content, num_words, actual_tone, final_story_title)

        if validation_results["error_message"]:
            # If story_content itself is an error message from a previous step (though less likely now)
            # or if validation failed critically (e.g. empty story from LLM)
            return validation_results["error_message"], actual_tone, validation_results, final_story_title

        return story_content, actual_tone, validation_results, final_story_title
    except openai.APIError as e:
        print(f"[OpenAI] OpenAI API Error: {e}")
        error_message = f"Error: OpenAI API returned an error: {e}. Please check your connection or API status."
        validation_results = _perform_basic_validation(error_message, num_words, actual_tone, final_story_title)
        return error_message, actual_tone, validation_results, final_story_title
    except openai.AuthenticationError as e:
        print(f"[OpenAI] OpenAI Authentication Error: {e}")
        error_message = f"Error: OpenAI authentication failed: {e}. Please check your API key."
        validation_results = _perform_basic_validation(error_message, num_words, actual_tone, final_story_title)
        return error_message, actual_tone, validation_results, final_story_title
    except openai.RateLimitError as e:
        print(f"[OpenAI] OpenAI Rate Limit Error: {e}")
        error_message = f"Error: OpenAI rate limit exceeded: {e}. Please wait and try again or check your plan."
        validation_results = _perform_basic_validation(error_message, num_words, actual_tone, final_story_title)
        return error_message, actual_tone, validation_results, final_story_title
    except Exception as e:
        print(f"[OpenAI] Generic error during story generation: {e}")
        error_message = f"Error generating story with OpenAI: An unexpected error occurred ({type(e).__name__}: {e})."
        validation_results = _perform_basic_validation(error_message, num_words, actual_tone, final_story_title)
        return error_message, actual_tone, validation_results, final_story_title


def generate_multiple_stories(age: int, character_idea: str, context_location_idea: str, num_words: int, language: str, num_stories: int = 3, tones_list: list = None) -> list:
    stories_data = []
    lang_code_short = language.split('-')[0]
    
    if tones_list is None:
        tones_list = []

    # Step 1: Generate diverse titles
    print(f"[Story Multi-Gen] Generating {num_stories} titles first...")
    # generated_titles will now be a list of actual creative titles or more descriptive fallbacks
    generated_titles = generate_story_titles_from_llm(age, character_idea, context_location_idea, language, num_stories)

    # No need to further check/pad generated_titles here as generate_story_titles_from_llm handles it.

    for i in range(num_stories):
        # story_title_directive will be the actual (hopefully creative) title from the list
        story_title_directive = generated_titles[i]
        
        variation = get_story_variation(language, i + 1)
        
        current_tone = None
        if i < len(tones_list) and tones_list[i] and tones_list[i].lower() != "random":
            current_tone = tones_list[i]
        if not current_tone:
            current_tone = get_random_tone()

        print(f"[Story Multi-Gen {i+1}/{num_stories}] Generating story for title directive: '{story_title_directive}', Tone: {current_tone}")
        
        # generate_story_from_llm will use story_title_directive. 
        # The `final_title` returned by it will be this directive.
        story_text, used_tone, validation_data, final_story_title_from_generation = generate_story_from_llm(
            age, character_idea, context_location_idea, num_words, language, 
            tone=current_tone, 
            variation=variation, 
            story_number=i + 1,
            story_title_directive=story_title_directive 
        )
        
        # Ensure validation_data has the title used/generated
        if "story_title" not in validation_data or not validation_data["story_title"]:
            validation_data["story_title"] = final_story_title_from_generation

        if story_text.startswith("Error:") and validation_data.get("error_message") is None:
            validation_data["error_message"] = story_text
            validation_data["word_count_ok"] = False 
            validation_data["min_length_ok"] = False
            validation_data["ends_properly"] = False

        stories_data.append({
            "id": str(i + 1), 
            "story_number": i + 1,
            "title": final_story_title_from_generation, # This is the key change: use the title from generation step
            "text": story_text,
            "tone": used_tone, 
            "variation_details_debug": { 
                "opening_style": variation.get('opening_style') if variation else None,
                "narrative_approach": variation.get('narrative_approach') if variation else None,
                "original_plot_seed_debug": variation.get('plot_seed') if variation else None,
            },
            "validation": validation_data, 
            "word_count": len(story_text.split()) if not story_text.startswith("Error:") else 0 
        })
    
    return stories_data

def generate_story_from_title(title: str, age: int, character_idea: str, context_location_idea: str, language: str, tone: str, target_word_count: int) -> str:
    """
    Generates a story based on a given title, ensuring minimal repetition of prompt details.
    """
    lang_code_short = language.split('-')[0]
    language_instruction = f"The story must be in {language} (e.g., for '{lang_code_short}')."

    avoid_repetition_instruction_it = "Non ripetere dettagli esatti forniti nel prompt, come il colore dei capelli o descrizioni dell'ambiente."
    avoid_repetition_instruction_en = "Do not repeat exact details provided in the prompt, such as hair color or setting descriptions."

    if lang_code_short == "it":
        story_gen_prompt = (
            f"Sei un autore di storie per bambini CREATIVO. Scrivi una storia per un bambino di {age} anni basata sul titolo: '{title}'. "
            f"La storia deve essere COMPLETAMENTE ORIGINALE e seguire un tono '{tone}'. {avoid_repetition_instruction_it} "
            f"Usa il titolo come guida per creare una narrazione unica e interessante. La storia deve avere circa {target_word_count} parole."
        )
    else:  # Default to English
        story_gen_prompt = (
            f"You are a CREATIVE children's story writer. Write a story for a {age}-year-old child based on the title: '{title}'. "
            f"The story must be COMPLETELY ORIGINAL and follow a '{tone}' tone. {avoid_repetition_instruction_en} "
            f"Use the title as a guide to create a unique and engaging narrative. The story should be around {target_word_count} words."
        )

    system_message = (
        "You are an assistant that generates exceptionally creative, concise, and diverse children's stories based on provided titles. "
        "Avoid repeating details from the prompt verbatim and focus on creating engaging and original narratives."
    )

    try:
        print(f"[OpenAI Story Gen] Generating story for title: {title[:50]}...")
        completion = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": story_gen_prompt}
            ],
            max_tokens=target_word_count * 2,  # Allow for flexibility in word count
            temperature=0.8  # Balance creativity and coherence
        )
        story = completion.choices[0].message.content.strip()

        if len(story.split()) < target_word_count * 0.8:  # Ensure story length is reasonable
            print(f"[OpenAI Story Gen] Warning: Generated story is shorter than expected. Length: {len(story.split())} words.")

        return story

    except Exception as e:
        print(f"[OpenAI Story Gen] Error generating story: {e}")
        return f"Error: Unable to generate story for title '{title}' due to {type(e).__name__}."

# Example usage of the chunked generation strategy
def generate_stories_with_titles(age: int, character_idea: str, context_location_idea: str, language: str, tone: str, target_word_count: int, num_stories: int):
    """
    Generates multiple stories by first creating titles and then generating stories for each title.
    """
    titles = generate_story_titles_from_llm(age, character_idea, context_location_idea, language, num_stories)
    stories = []

    for i, title in enumerate(titles):
        story = generate_story_from_title(title, age, character_idea, context_location_idea, language, tone, target_word_count)
        stories.append({
            "title": title,
            "story": story
        })

    return stories

# Example usage (for testing this module directly):
if __name__ == '__main__':
    # Ensure you have OPENAI_API_KEY set in your environment to test this
    if not openai.api_key:
        print("Skipping direct test: OPENAI_API_KEY not set.")
    else:
        print("\n--- Sample Generated Story with Tone (OpenAI) ---")
        sample_story_text, sample_tone = generate_story_from_llm(
            age=5,
            character_idea="Leo il leone coraggioso",
            context_idea="la giungla misteriosa",
            num_words=150,
            language="it-IT",
            tone="avventuroso"
        )
        print(f"Tone: {sample_tone}")
        print(sample_story_text)

        print("\n--- Sample Generated Story with Random Tone (OpenAI - English) ---")
        sample_story_en_text, sample_en_tone = generate_story_from_llm(
            age=7,
            character_idea="Squeaky the curious squirrel",
            context_idea="a magical forest",
            num_words=200,
            language="en-US",
            tone="random" # or None
        )
        print(f"Tone: {sample_en_tone}")
        print(sample_story_en_text)

        # Test multiple story generation with specific tones
        print("\n--- Sample Generated Stories (Multiple Variations with Specific Tones) ---")
        requested_tones = ["calmo", "divertente", "misterioso"]
        multiple_stories_result = generate_multiple_stories(
            age=6,
            character_idea="Pippo il pinguino avventuroso",
            context_idea="l'Antartide incantata",
            num_words=100,
            language="it-IT",
            num_stories=3,
            tones=requested_tones
        )
        for story_data in multiple_stories_result:
            print(f"\nStory {story_data['story_number']} (Plot: {story_data['variation']['plot_seed']}, Tone: {story_data['tone']}):")
            print(story_data['text'])

        # Test multiple story generation with mixed and random tones
        print("\n--- Sample Generated Stories (Mixed/Random Tones) ---")
        mixed_tones = ["tenero", "random"] # Request 2 stories, one tenero, one random
        multiple_stories_mixed = generate_multiple_stories(
            age=4,
            character_idea="Un coniglietto timido",
            context_idea="un prato fiorito",
            num_words=80,
            language="it-IT",
            num_stories=2,
            tones=mixed_tones
        )
        for story_data in multiple_stories_mixed:
            print(f"\nStory {story_data['story_number']} (Plot: {story_data['variation']['plot_seed']}, Tone: {story_data['tone']}):")
            print(story_data['text'])

        # Test story generation from title
        print("\n--- Sample Generated Story from Title ---")
        title_based_story = generate_story_from_title(
            title="Il viaggio straordinario di Leo il leone",
            age=5,
            character_idea="Leo il leone coraggioso",
            context_location_idea="la giungla misteriosa",
            language="it-IT",
            tone="avventuroso",
            target_word_count=150
        )
        print(title_based_story)

        # Test chunked story generation strategy
        print("\n--- Sample Generated Stories with Chunked Strategy ---")
        chunked_stories_result = generate_stories_with_titles(
            age=6,
            character_idea="Pippo il pinguino avventuroso",
            context_location_idea="l'Antartide incantata",
            language="it-IT",
            tone="divertente",
            target_word_count=100,
            num_stories=3
        )
        for story_data in chunked_stories_result:
            print(f"\nTitle: {story_data['title']}")
            print(story_data['story'])
