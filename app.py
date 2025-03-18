import os
import uuid
import streamlit as st
import speech_recognition as sr
from groq import Groq
from streamlit_chat import message
import tempfile

# Initialize Groq API client
client = Groq(
    api_key='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',
)

ACTION_WORDS = {"boil", "chop", "stir", "mix", "add", "serve", "bake", "fry", "blend", "simmer", "pour"}

def calculate_attention_weight(step):
    """
    Calculates self-attention scores for each step based on the number of action words.
    """
    words = step.lower().split()
    attention_weight = sum(1 for word in words if word in ACTION_WORDS)
    return attention_weight / len(words) if words else 0  # Normalize weight

def apply_attention_mechanism(recipe_text):
    """
    Highlights important steps based on self-attention scores.
    """
    step_lines = recipe_text.split("\n")
    attention_scores = [calculate_attention_weight(step) for step in step_lines]
    
    # Normalize scores to a 0-1 range
    max_score = max(attention_scores) if attention_scores else 1
    normalized_scores = [score / max_score for score in attention_scores]
    
    highlighted_steps = []
    for step, score in zip(step_lines, normalized_scores):
        if score >= 0.7:  # High attention
            formatted_step = f"🔥 {step.upper()}"  # Emphasize with uppercase
        elif score >= 0.3:  # Medium attention
            formatted_step = f"⭐ {step}"  # Highlight with a star
        else:  # Low attention
            formatted_step = step
        highlighted_steps.append(formatted_step)
    
    return "\n".join(highlighted_steps)


# Language selection dropdown with additional languages
languages = ["English", "தமிழ்", "Française", "മലയാളം", "తెలుగు", "ಕನ್ನಡ", "हिन्दी"]
language_option = st.selectbox(
    "Select Language / மொழியைத் தேர்ந்தெடுக்கவும் / Sélectionner la langue / ഭാഷ തിരഞ്ഞെടുക്കുക / భాషను ఎంచుకోండి / ಭಾಷೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ / भाषा चुनें:",
    languages,
    index=0,
)

# --- TTS audio functions removed ---

def get_recipe(recipe_name):
    if language_option == "தமிழ்":
        prompt_template = f"""
        நீங்கள் ஒரு தொழில்முறை சமையல்காரர் மற்றும் சமையல் உதவியாளர். உங்கள் பணி, தெளிவான வழிமுறைகள், வகைப்படுத்தப்பட்ட படிகள் மற்றும் மதிப்பிடப்பட்ட கால அளவுகளுடன் ஒரு கட்டமைக்கப்பட்ட, படிப்படியான செய்முறை வழிகாட்டியை வழங்குவதாகும்.

        செய்முறை பெயர்: {recipe_name}

        உள்ளீட்டு பணி: ஒரு கப் தேநீர் தயாரிக்கவும்
        வெளியீடு: வழிமுறைகளின் வரிசை:
        
        1. வழிமுறை 1: ஒரு தேநீர் பையையும் ஒரு கப்பையும் எடுத்துக் கொள்ளுங்கள்.
           • வகை: எளிய வழிமுறை
           காலம்: 30 வினாடிகள்
        2. வழிமுறை 2: தேநீர் தயாரிக்கும் நோக்கத்துடன் தண்ணீரை கொதிக்க வைக்கவும்.
           • வகை: நோக்கம் கொண்ட வழிமுறை
           காலம்: 2 நிமிடங்கள்
        3. வழிமுறை 3: கொதிக்கும் தண்ணீரை தேநீர் பையுடன் கப்பில் ஊற்றவும்.
           • வகை: வரிசை கொண்ட வழிமுறை
           காலம்: 30 வினாடிகள்
        4. வழிமுறை 4: விருப்பமாக, தேநீரில் சர்க்கரை அல்லது பால் சேர்க்கவும்.
           • வகை: விருப்ப வழிமுறை
           காலம்: 1 நிமிடம் (விருப்பமானது)
        5. வழிமுறை 5: பின்னர், தேநீரை பரிமாறவும்.
           • வகை: வரிசை கொண்ட வழிமுறை
           காலம்: 30 வினாடிகள்
        மொத்த நேர கணக்கீடு:
           • சர்க்கரை அல்லது பால் சேர்த்தல் இல்லாமல்: 3 நிமிடங்கள் 30 வினாடிகள்
           • சர்க்கரை அல்லது பால் சேர்த்தால்: 4 நிமிடங்கள் 30 வினாடிகள்

        இப்போது, *{recipe_name}*க்கான படிப்படியான வழிமுறைகளை மேலே உள்ள கட்டமைப்பைப் பின்பற்றி உருவாக்கவும்.
        """
    elif language_option == "Français":
        prompt_template = f"""
        Vous êtes un chef professionnel et assistant culinaire. Votre tâche consiste à fournir un guide de recette structuré, étape par étape, avec des instructions claires, des étapes catégorisées et des durées estimées.

        Nom de la recette: {recipe_name}

        Tâche D'ENTRÉE: Préparer une tasse de thé
        RÉSULTAT: Séquence d'instructions:
        
        1. Instruction 1: Prenez un sachet de thé et une tasse.
           • Type: INSTRUCTION SIMPLE
           Durée: 30 secondes
        2. Instruction 2: Faites bouillir de l'eau avec l'intention de faire du thé.
           • Type: INSTRUCTION AVEC OBJECTIF
           Durée: 2 minutes
        3. Instruction 3: Versez l'eau bouillie dans la tasse avec le sachet de thé.
           • Type: INSTRUCTION AVEC SÉQUENCE
           Durée: 30 secondes
        4. Instruction 4: Optionnellement, ajoutez du sucre ou du lait au thé.
           • Type: INSTRUCTION EXCLUSIVE
           Durée: 1 minute (facultatif)
        5. Instruction 5: Ensuite, servez le thé.
           • Type: INSTRUCTION AVEC SÉQUENCE
           Durée: 30 secondes
        Calcul du temps total:
           • Sans ajouter de sucre ou de lait: 3 minutes 30 secondes
           • Avec ajout de sucre ou de lait: 4 minutes 30 secondes

        Maintenant, générez les instructions étape par étape pour {recipe_name} en suivant le format structuré ci-dessus.
        """
    elif language_option == "മലയാളം":
        prompt_template = f"""
        നിങ്ങൾ ഒരു പ്രൊഫഷണൽ ഷെഫ് ആയും പാചക സഹായിയുമായാണ് പ്രവർത്തിക്കുന്നത്. നിങ്ങളുടെ ദൗത്യമാണ്, വ്യക്തമായ നിർദ്ദേശങ്ങൾ, വിഭാഗീകരിച്ച ഘട്ടങ്ങൾ, സമയക്രമീകരണങ്ങൾ എന്നിവയോടെയുള്ള ഒരു ക്രമീകരിച്ച പാചക മാർഗരേഖ നൽകുക.

        റെസിപ്പി പേര്: {recipe_name}

        ഇൻപുട്ട് ദൗത്യം: ഒരു കപ്പ് ചായ ഒരുക്കുക
        ഔട്ട്പുട്ട്: ഘട്ടങ്ങളിലെ നിർദ്ദേശങ്ങളുടെ ക്രമം:
        
        1. ഘട്ടം 1: ഒരു ടീ ബാഗും ഒരു കപ്പും എടുക്കുക.
           • തരം: ലളിത നിർദ്ദേശം
           ദൈർഘ്യം: 30 സെക്കൻഡ്
        2. ഘട്ടം 2: ചായ ഉണ്ടാക്കാൻ ഉദ്ദേശത്തോടെ വെള്ളം കുതിരിക്കുക.
           • തരം: ലക്ഷ്യ സഹിതം നിർദ്ദേശം
           ദൈർഘ്യം: 2 മിനിറ്റ്
        3. ഘട്ടം 3: ചൂടാക്കിയ വെള്ളം, ടി ബാഗുള്ള കപ്പിലേക്ക് ഒഴിക്കുക.
           • തരം: ക്രമ നിർദ്ദേശം
           ദൈർഘ്യം: 30 സെക്കൻഡ്
        4. ഘട്ടം 4: ഐച്ഛികമായി, ചായയിൽ പഞ്ചസാരയോ പാലിനോ ചേർക്കുക.
           • തരം: ഐച്ഛിക നിർദ്ദേശം
           ദൈർഘ്യം: 1 മിനിറ്റ്
        5. ഘട്ടം 5: ശേഷം, ചായ പരിവഹിക്കുക.
           • തരം: ക്രമ നിർദ്ദേശം
           ദൈർഘ്യം: 30 സെക്കൻഡ്
        മൊത്തം സമയം:
           • പഞ്ചസാര/പാലില്ലാതെ: 3 മിനിറ്റ് 30 സെക്കൻഡ്
           • പഞ്ചസാര/പാലോടുകൂടി: 4 മിനിറ്റ് 30 സെക്കൻഡ്

        ഇനി, {recipe_name} എന്നതിനുത്തരം ക്രമീകരിച്ച പാചക മാർഗരേഖ തയ്യാറാക്കുക.
        """
    elif language_option == "తెలుగు":
        prompt_template = f"""
        మీరు ఒక ప్రొఫెషనల్ చెఫ్ మరియు వంట సహాయకుడిగా వ్యవహరిస్తున్నారు. మీ పని, స్పష్టమైన సూచనలతో, విభాగాలుగా వర్గీకరించిన దశలతో మరియు గణించబడిన సమయాలతో సహా ఒక సుసంపన్నమైన వంటకాల గైడ్‌ని అందించడం.

        వంటకపు పేరు: {recipe_name}

        ఇన్పుట్ టాస్క్: ఒక కప్పు టీ ను తయారుచేయండి
        ఔట్‌పుట్: దశలవారీ సూచనల శ్రేణి:
        
        1. దశ 1: ఒక టీ బ్యాగ్ మరియు ఒక కప్పును తీసుకోండి.
           • తరగతి: సులభమైన సూచన
           వ్యవధి: 30 సెకన్లు
        2. దశ 2: టీ తయారుచేయడానికి నీటిని మరిగించండి.
           • తరగతి: ఉద్దేశ్యంతో కూడిన సూచన
           వ్యవధి: 2 నిమిషాలు
        3. దశ 3: మరిగిన నీటిని టీ బ్యాగ్ ఉన్న కప్పులో పోయండి.
           • తరగతి: అనుక్రమ సూచన
           వ్యవధి: 30 సెకన్లు
        4. దశ 4: ఐచ్చికంగా, చక్కెర లేదా పాలను జోడించండి.
           • తరగతి: ఐచ్చిక సూచన
           వ్యవధి: 1 నిమిషం
        5. దశ 5: తరువాత, టీని సర్వ్ చేయండి.
           • తరగతి: అనుక్రమ సూచన
           వ్యవధి: 30 సెకన్లు
        మొత్తం సమయం:
           • చక్కెర/పాలు లేకుండా: 3 నిమిషాలు 30 సెకన్లు
           • చక్కెర/పాలు ఉంటే: 4 నిమిషాలు 30 సెకన్లు

        ఇప్పుడు, {recipe_name} కోసం పై నిర్మిత నమూనా ప్రకారం దశలవారీ సూచనలను రూపొందించండి.
        """
    elif language_option == "ಕನ್ನಡ":
        prompt_template = f"""
        ನೀವೊಂದು ಪ್ರೊಫೆಷನಲ್ ಶೆಫ್ ಮತ್ತು ಅಡುಗೆ ಸಹಾಯಕರಾಗಿ ಕಾರ್ಯನಿರ್ವಹಿಸುತ್ತೀರಿ. ನಿಮ್ಮ ಕರ್ತವ್ಯವೆಂದರೆ, ಸ್ಪಷ್ಟ ಸೂಚನೆಗಳು, ವಿಭಾಗೀಕರಿಸಿದ ಹಂತಗಳು ಮತ್ತು ಅಂದಾಜು ಕಾಲಾವಧಿಗಳೊಂದಿಗೆ ಪರಿಚಯಿತವಾದ ಪಾಕವಿಧಾನ ಮಾರ್ಗದರ್ಶನವನ್ನು ಒದಗಿಸುವುದು.

        ರೆಸಿಪಿಯ ಹೆಸರು: {recipe_name}

        ಇನ್ಪುಟ್ ಕೆಲಸ: ಒಂದು ಕಪ್ ಚಹಾ ತಯಾರಿಸಿ
        ಔಟ್‌ಪುಟ್: ಹಂತ ಹಂತದ ಸೂಚನೆಗಳು:
        
        1. ಹಂತ 1: ಒಂದು ಟೀಸ್ ಬ್ಯಾಗ್ ಮತ್ತು ಒಂದು ಕಪ್ ಅನ್ನು ತೆಗೆದುಕೊಳ್ಳಿ.
           • ಪ್ರಕಾರ: ಸರಳ ಸೂಚನೆ
           ಅವಧಿ: 30 ಸೆಕೆಂಡು
        2. ಹಂತ 2: ಚಹಾ ಮಾಡಲು ನೀರನ್ನು ಕುದಿಸಿ.
           • ಪ್ರಕಾರ: ಉದ್ದೇಶ ಸೂಚನೆ
           ಅವಧಿ: 2 ನಿಮಿಷ
        3. ಹಂತ 3: ಕುದಿದ ನೀರನ್ನು ಟೀಸ್ ಬ್ಯಾಗ್ ಇರುವ ಕಪ್‌ಗೆ ಹಾಕಿ.
           • ಪ್ರಕಾರ: ಕ್ರಮ ಸೂಚನೆ
           ಅವಧಿ: 30 ಸೆಕೆಂಡು
        4. ಹಂತ 4: ಆಯ್ಕೆಯಂತೆ, ಚಹೆಗೆ ಸಕ್ಕರೆ ಅಥವಾ ಹಾಲು ಸೇರಿಸಿ.
           • ಪ್ರಕಾರ: ಐಚ್ಛಿಕ ಸೂಚನೆ
           ಅವಧಿ: 1 ನಿಮಿಷ
        5. ಹಂತ 5: ನಂತರ, ಚಹಾವನ್ನು ಸರ್ವ್ ಮಾಡಿ.
           • ಪ್ರಕಾರ: ಕ್ರಮ ಸೂಚನೆ
           ಅವಧಿ: 30 ಸೆಕೆಂಡು
        ಒಟ್ಟು ಸಮಯ ಲೆಕ್ಕ:
           • ಸಕ್ಕರೆ/ಹಾಲಿಲ್ಲದೆ: 3 ನಿಮಿಷ 30 ಸೆಕೆಂಡು
           • ಸಕ್ಕರೆ/ಹಾಲು ಸೇರಿಸಿದರೆ: 4 ನಿಮಿಷ 30 ಸೆಕೆಂಡು

        ಈಗ, {recipe_name} ಗೆ ಸಂಬಂಧಿಸಿದ ಹಂತ ಹಂತದ ಪಾಕವಿಧಾನ ಸೂಚನೆಗಳನ್ನು ರಚಿಸಿ.
        """
    elif language_option == "हिन्दी":
        prompt_template = f"""
        आप एक पेशेवर शेफ और कुकिंग असिस्टेंट हैं। आपका कार्य स्पष्ट निर्देशों, क्रमबद्ध चरणों और अनुमानित समय के साथ एक संरचित रेसिपी गाइड प्रदान करना है।

        रेसिपी का नाम: {recipe_name}

        इनपुट कार्य: एक कप चाय तैयार करें
        आउटपुट: चरण-दर-चरण निर्देश:
        
        1. चरण 1: एक टी बैग और एक कप लें।
           • प्रकार: साधारण निर्देश
           अवधि: 30 सेकंड
        2. चरण 2: चाय बनाने के लिए पानी को उबालें।
           • प्रकार: उद्देश्य निर्देश
           अवधि: 2 मिनट
        3. चरण 3: उबले हुए पानी को टी बैग वाले कप में डालें।
           • प्रकार: क्रम निर्देश
           अवधि: 30 सेकंड
        4. चरण 4: वैकल्पिक रूप से, चाय में चीनी या दूध मिलाएं।
           • प्रकार: वैकल्पिक निर्देश
           अवधि: 1 मिनट
        5. चरण 5: फिर, चाय परोसें।
           • प्रकार: क्रम निर्देश
           अवधि: 30 सेकंड
        कुल समय:
           • बिना चीनी/दूध के: 3 मिनट 30 सेकंड
           • चीनी/दूध के साथ: 4 मिनट 30 सेकंड

        अब, {recipe_name} के लिए ऊपर दिए गए संरचित प्रारूप का पालन करते हुए चरण-दर-चरण निर्देश तैयार करें।
        """
    else:
        prompt_template = f"""
        You are a professional chef and cooking assistant. Your task is to provide a structured, step-by-step recipe guide with clear instructions, categorized steps, and estimated durations.

        Recipe Name: {recipe_name}

        INPUT Task: Prepare a Cup of Tea
        OUTPUT: Sequence of Instructions:
        
        1. Instruction 1: Take a tea bag and a cup.
           • Type: SIMPLE INSTRUCTION
           Duration: 30 seconds
        2. Instruction 2: Boil water with the intention of making tea.
           • Type: INSTRUCTION WITH PURPOSE
           Duration: 2 minutes
        3. Instruction 3: Pour the boiled water into the cup with the tea bag.
           • Type: INSTRUCTION WITH SEQUENCE
           Duration: 30 seconds
        4. Instruction 4: Optionally, add sugar or milk to the tea.
           Type: EXCLUSIVE INSTRUCTION
           Duration: 1 minute (optional)
        5. Instruction 5: Then, serve the tea.
           • Type: INSTRUCTION WITH SEQUENCE
           Duration: 30 seconds
        Total Time Calculation:
           • Without adding sugar or milk: 3 minutes 30 seconds
           • With adding sugar or milk: 4 minutes 30 seconds

        Now, generate the step-by-step instructions for {recipe_name} following the above structured format.
        """
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a professional chef and cooking assistant."},
            {"role": "user", "content": prompt_template}
        ],
        model="llama-3.3-70b-versatile",
    )
    return chat_completion.choices[0].message.content

def speech_to_text():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        if language_option == "English":
            st.write("🎤 Speak the recipe name...")
            recog_lang = "en-US"
        elif language_option == "தமிழ்":
            st.write("🎤 செய்முறை பெயரைப் பேசுங்கள்...")
            recog_lang = "ta-IN"
        elif language_option == "Français":
            st.write("🎤 Dites le nom de la recette...")
            recog_lang = "fr-FR"
        elif language_option == "മലയാളം":
            st.write("🎤 റെസിപ്പിയുടെ പേര് പറഞ്ഞുക...")
            recog_lang = "ml-IN"
        elif language_option == "తెలుగు":
            st.write("🎤 వంటకం పేరును పలికండి...")
            recog_lang = "te-IN"
        elif language_option == "ಕನ್ನಡ":
            st.write("🎤 ರೆಸಿಪಿಯ ಹೆಸರನ್ನು ಹೇಳಿ...")
            recog_lang = "kn-IN"
        elif language_option == "हिन्दी":
            st.write("🎤 रेसिपी का नाम बोलें...")
            recog_lang = "hi-IN"
        else:
            st.write("🎤 Speak the recipe name...")
            recog_lang = "en-US"
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio, language=recog_lang)
            return text
        except sr.UnknownValueError:
            if language_option == "English":
                st.write("❌ Sorry, I couldn't understand the speech.")
            elif language_option == "தமிழ்":
                st.write("❌ மன்னிக்கவும், நான் பேச்சைப் புரிந்து கொள்ளவில்லை.")
            elif language_option == "Français":
                st.write("❌ Désolé, je n'ai pas compris le discours.")
            elif language_option == "മലയാളം":
                st.write("❌ ക്ഷമിക്കണം, ഞാൻ സംസാരത്തെ മനസിലാക്കാനായില്ല.")
            elif language_option == "తెలుగు":
                st.write("❌ క్షమించండి, నేను మాటలు తెలుసుకోలేకపోయాను.")
            elif language_option == "ಕನ್ನಡ":
                st.write("❌ ಕ್ಷಮಿಸಿ, ನಾನು ಮಾತನ್ನು ಅರ್ಥಮಾಡಿಕೊಳ್ಳಲಿಲ್ಲ.")
            elif language_option == "हिन्दी":
                st.write("❌ क्षमा करें, मैं बोलचाल समझ नहीं पाया।")
            return None
        except sr.RequestError:
            if language_option == "English":
                st.write("❌ Could not request results, check your internet connection.")
            elif language_option == "தமிழ்":
                st.write("❌ முடிவுகளைக் கோர முடியவில்லை, உங்கள் இணைய இணைப்பைச் சரிபார்க்கவும்.")
            elif language_option == "Français":
                st.write("❌ Impossible de demander les résultats, vérifiez votre connexion Internet.")
            elif language_option == "മലയാളം":
                st.write("❌ ഫലങ്ങൾ ലഭിച്ചില്ല, ദയവായി ഇന്റർനെറ്റ് ബന്ധം പരിശോധിക്കുക.")
            elif language_option == "తెలుగు":
                st.write("❌ ఫలితాలను కోరడం సాధ్యపడలేదు, దయచేసి మీ ఇంటర్నెట్ కనెక్షన్ తనిఖీ చేయండి.")
            elif language_option == "ಕನ್ನಡ":
                st.write("❌ ಫಲಿತಾಂಶಗಳನ್ನು ಕೇಳಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ, ದಯವಿಟ್ಟು ನಿಮ್ಮ ಇಂಟರ್ನೆಟ್ ಸಂಪರ್ಕವನ್ನು ಪರಿಶೀಲಿಸಿ.")
            elif language_option == "हिन्दी":
                st.write("❌ परिणामों का अनुरोध नहीं कर सका, कृपया अपने इंटरनेट कनेक्शन की जांच करें।")
            return None

# --- Streamlit UI Setup ---
if language_option == "English":
    title_text = "🍽 Cooking Assistant - Get Your Recipes!"
    instruction_text = "Type the name of the recipe or use voice input to get step-by-step instructions."
elif language_option == "தமிழ்":
    title_text = "🍽 சமையல் உதவியாளர் - உங்கள் செய்முறைகளைக் பெறுங்கள்!"
    instruction_text = "செய்முறை பெயரை தட்டச்சு செய்யவும் அல்லது குரல் உள்ளீட்டைப் பயன்படுத்தி படிப்படியான வழிமுறைகளைப் பெறவும்."
elif language_option == "Français":
    title_text = "🍽 Assistant de Cuisine - Obtenez Vos Recettes!"
    instruction_text = "Tapez le nom de la recette ou utilisez l'entrée vocale pour obtenir des instructions étape par étape."
elif language_option == "മലയാളം":
    title_text = "🍽 വിഭക്ഷ്യ സഹായി - നിങ്ങളുടെ റെസിപ്പികള്‍ ലഭിക്കുക!"
    instruction_text = "റെസിപ്പിയുടെ പേര് ടൈപ്പ് ചെയ്യുക അല്ലെങ്കിൽ വോയ്സ് ഇൻപുട്ട് ഉപയോഗിച്ച് ഘട്ടം ഘട്ടമായി നിർദ്ദേശങ്ങൾ നേടുക."
elif language_option == "తెలుగు":
    title_text = "🍽 వంట సహాయకుడు - మీ వంటకాలు పొందండి!"
    instruction_text = "వంటకం పేరును టైప్ చేయండి లేదా వాయిస్ ఇన్పుట్ ద్వారా దశల వారీగా సూచనలు పొందండి."
elif language_option == "ಕನ್ನಡ":
    title_text = "🍽 ಅಡುಗೆ ಸಹಾಯಕ - ನಿಮ್ಮ ಪಾಕವಿಧಾನಗಳನ್ನು ಪಡೆಯಿರಿ!"
    instruction_text = "ಪಾಕವಿಧಾನದ ಹೆಸರನ್ನು ಟೈಪ್ ಮಾಡಿ ಅಥವಾ ಧ್ವನಿ ಇನ್ಪುಟ್ ಬಳಸಿ ಹಂತ ಹಂತದ ಸೂಚನೆಗಳನ್ನು ಪಡೆಯಿರಿ."
elif language_option == "हिन्दी":
    title_text = "🍽 खाना सहायक - अपनी रेसिपी प्राप्त करें!"
    instruction_text = "रेसिपी का नाम टाइप करें या वॉइस इनपुट का उपयोग करके चरण-दर-चरण निर्देश प्राप्त करें।"
else:
    title_text = "🍽 Cooking Assistant"
    instruction_text = "Enter the recipe name or use voice input."

st.title(title_text)
st.write(instruction_text)

# Initialize session states for messages and recipe_name
if "messages" not in st.session_state:
    st.session_state.messages = []
if "recipe_name" not in st.session_state:
    st.session_state.recipe_name = ""

# Display chat history
for i, msg in enumerate(st.session_state.messages):
    if msg["role"] == "user":
        message(msg['content'], is_user=True, key=f'user_{i}', avatar_style="miniavs")
    else:
        message(msg['content'], is_user=False, key=f'assistant_{i}', avatar_style="icons")

# --- Voice Input Button ---
if language_option == "English":
    voice_button_label = "🎤 Use Voice Input"
elif language_option == "தமிழ்":
    voice_button_label = "🎤 குரல் உள்ளீட்டைப் பயன்படுத்தவும்"
elif language_option == "Français":
    voice_button_label = "🎤 Utiliser l'entrée vocale"
elif language_option == "മലയാളം":
    voice_button_label = "🎤 വോയ്സ് ഇൻപുട്ട് ഉപയോഗിക്കുക"
elif language_option == "తెలుగు":
    voice_button_label = "🎤 వాయిస్ ఇన్పుట్ ఉపయోగించండి"
elif language_option == "ಕನ್ನಡ":
    voice_button_label = "🎤 ಧ್ವನಿ ಇನ್ಪುಟ್ ಬಳಸಿ"
elif language_option == "हिन्दी":
    voice_button_label = "🎤 वॉइस इनपुट उपयोग करें"
else:
    voice_button_label = "🎤 Use Voice Input"

if st.button(voice_button_label):
    recipe_name_input = speech_to_text()
    if recipe_name_input:
        st.session_state.recipe_name = recipe_name_input
        st.session_state.messages.append({"role": "user", "content": recipe_name_input})
        if language_option == "English":
            st.write("Fetching the recipe...")
        elif language_option == "தமிழ்":
            st.write("செய்முறை பெறப்படுகிறது...")
        elif language_option == "Français":
            st.write("Récupération de la recette...")
        elif language_option == "മലയാളം":
            st.write("റെസിപ്പി ലഭിക്കുന്നു...")
        elif language_option == "తెలుగు":
            st.write("వంటకం పొందుతున్నాం...")
        elif language_option == "ಕನ್ನಡ":
            st.write("ಪಾಕವಿಧಾನವನ್ನು ಪಡೆಯುತ್ತಿದೆ...")
        elif language_option == "हिन्दी":
            st.write("रेसिपी प्राप्त की जा रही है...")
        recipe_instructions = get_recipe(st.session_state.recipe_name)
        st.session_state.messages.append({"role": "assistant", "content": recipe_instructions})
        st.rerun()

# --- Text Input Field ---
if language_option == "English":
    text_input_label = "Enter Recipe Name:"
elif language_option == "தமிழ்":
    text_input_label = "செய்முறை பெயரை உள்ளிடவும்:"
elif language_option == "Français":
    text_input_label = "Entrez le nom de la recette:"
elif language_option == "മലയാളം":
    text_input_label = "റെസിപ്പിയുടെ പേര് നൽകുക:"
elif language_option == "తెలుగు":
    text_input_label = "వంటకం పేరును నమోదు చేయండి:"
elif language_option == "ಕನ್ನಡ":
    text_input_label = "ಪಾಕವಿಧಾನದ ಹೆಸರನ್ನು ನಮೂದಿಸಿ:"
elif language_option == "हिन्दी":
    text_input_label = "रेसिपी का नाम दर्ज करें:"
else:
    text_input_label = "Enter Recipe Name:"

recipe_name_input = st.text_input(text_input_label, value=st.session_state.recipe_name)
if recipe_name_input and recipe_name_input != st.session_state.recipe_name:
    st.session_state.recipe_name = recipe_name_input
    st.session_state.messages.append({"role": "user", "content": recipe_name_input})
    if language_option == "English":
        st.write("Fetching the recipe...")
    elif language_option == "தமிழ்":
        st.write("செய்முறை பெறப்படுகிறது...")
    elif language_option == "Français":
        st.write("Récupération de la recette...")
    elif language_option == "മലയാളം":
        st.write("റെസിപ്പി ലഭിക്കുന്നു...")
    elif language_option == "తెలుగు":
        st.write("వంటకం పొందుతున్నాం...")
    elif language_option == "ಕನ್ನಡ":
        st.write("ಪಾಕವಿಧಾನವನ್ನು ಪಡೆಯುತ್ತಿದೆ...")
    elif language_option == "हिन्दी":
        st.write("रेसिपी प्राप्त की जा रही है...")
    recipe_instructions = get_recipe(st.session_state.recipe_name)
    st.session_state.messages.append({"role": "assistant", "content": recipe_instructions})
    st.rerun()

# --- Audio control section removed ---
