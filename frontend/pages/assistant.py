# frontend/pages/assistant.py
import random
import re

INTENTS = {
    "greet": {
        "keywords": ["hello", "hi", "hey", "namaste", "नमस्ते", "greetings", "good morning", "good afternoon", "good evening", "howdy"],
        "response_en": "Hello! 👋 I'm your AI assistant. How can I help you today?",
        "response_hi": "नमस्ते! 👋 मैं आपका AI सहायक हूं। आज मैं आपकी कैसे मदद कर सकता हूं?"
    },
    "file_complaint": {
        "keywords": ["file complaint", "register complaint", "new complaint", "submit complaint", "शिकायत दर्ज", "नई शिकायत", "how to file", "how do i file", "raise complaint"],
        "response_en": "📢 **To file a complaint:**\n\n1. Go to **File Complaint** from the sidebar.\n2. Describe your issue (text or voice).\n3. Share your location (auto‑detected).\n4. Click **Submit**.\n\nOur AI will route it to the right department automatically.",
        "response_hi": "📢 **शिकायत दर्ज करने के लिए:**\n\n1. साइडबार से **शिकायत दर्ज करें** पर जाएं।\n2. अपनी समस्या लिखें या बोलें।\n3. अपना स्थान साझा करें।\n4. **जमा करें** क्लिक करें।\n\nAI सही विभाग को भेज देगा।"
    },
    "track_complaint": {
        "keywords": ["track complaint", "complaint status", "where is my complaint", "status update", "शिकायत ट्रैक", "स्थिति", "कहां है शिकायत", "track my complaint", "check status"],
        "response_en": "🔍 **Track your complaint:**\n\n• Go to **Track Complaint** from the sidebar and enter your complaint ID (e.g., GR1A2B3C4D).\n• Or go to your **Dashboard** and click on any complaint to see its timeline.\n\nYour complaint ID was sent to you via notification when you filed it.",
        "response_hi": "🔍 **अपनी शिकायत ट्रैक करें:**\n\n• साइडबार से **शिकायत ट्रैक करें** पर जाएं और अपना शिकायत ID डालें (जैसे GR1A2B3C4D)।\n• या **डैशबोर्ड** पर जाकर किसी भी शिकायत पर क्लिक करें।\n\nशिकायत ID आपको सूचना में मिली थी।"
    },
    "schemes": {
        "keywords": ["scheme", "government scheme", "yojana", "सरकारी योजना", "plan", "benefit", "pm awas", "jal jeevan", "ujjwala", "schemes", "yojna"],
        "response_en": "📜 **Government Schemes:**\n\nYou can view all schemes in the **Govt Schemes** section. Currently available:\n• PM Awas Yojana (housing)\n• Jal Jeevan Mission (water)\n• Ujjwala Yojana (LPG)\n\nEach scheme has details in English and Hindi, and you can listen to them too!",
        "response_hi": "📜 **सरकारी योजनाएं:**\n\nसभी योजनाएं **सरकारी योजनाएं** सेक्शन में देख सकते हैं। वर्तमान योजनाएं:\n• पीएम आवास योजना (आवास)\n• जल जीवन मिशन (पानी)\n• उज्ज्वला योजना (LPG)\n\nप्रत्येक योजना का विवरण हिंदी और अंग्रेजी में है।"
    },
    "departments": {
        "keywords": ["department", "which department", "who handles", "water department", "electricity department", "road department", "health department", "विभाग", "contact department"],
        "response_en": "🏢 **Department assignment by category:**\n\n• 💧 Water → Water Supply Department\n• ⚡ Electricity → Electricity Department\n• 🛣️ Road → Public Works Department\n• 🗑️ Waste → Municipal Corporation\n• 🌊 Drainage → Drainage Department\n• 🏥 Health → Health Department\n• 📋 Other → General Administration",
        "response_hi": "🏢 **श्रेणी के अनुसार विभाग आवंटन:**\n\n• 💧 पानी → जल आपूर्ति विभाग\n• ⚡ बिजली → विद्युत विभाग\n• 🛣️ सड़क → लोक निर्माण विभाग\n• 🗑️ कचरा → नगर निगम\n• 🌊 नाला → जल निकासी विभाग\n• 🏥 स्वास्थ्य → स्वास्थ्य विभाग\n• 📋 अन्य → सामान्य प्रशासन"
    },
    "sla": {
        "keywords": ["sla", "deadline", "time limit", "resolution time", "how long", "कितने दिन", "समय सीमा", "service level agreement", "what is sla", "sla breach"],
        "response_en": "⏱️ **SLA (Service Level Agreement) targets:**\n\n• 💧 Water / ⚡ Electricity → **24 hours**\n• 🏥 Health → **36 hours**\n• 🗑️ Waste / 🌊 Drainage → **48 hours**\n• 🛣️ Road / 📋 Other → **72 hours**\n\nHigh‑priority complaints get **30% faster** resolution. You can see the SLA deadline on your complaint card.",
        "response_hi": "⏱️ **SLA (सेवा स्तर समझौता) लक्ष्य:**\n\n• 💧 पानी / ⚡ बिजली → **24 घंटे**\n• 🏥 स्वास्थ्य → **36 घंटे**\n• 🗑️ कचरा / 🌊 नाला → **48 घंटे**\n• 🛣️ सड़क / 📋 अन्य → **72 घंटे**\n\nउच्च प्राथमिकता वाली शिकायतें **30% तेजी से** हल होती हैं। आप अपने शिकायत कार्ड पर SLA समय सीमा देख सकते हैं।"
    },
    "rating": {
        "keywords": ["rating", "rate", "feedback", "stars", "रिव्यू", "रेटिंग", "स्टार", "how to rate", "rate official"],
        "response_en": "⭐ **Ratings:**\n\nAfter a complaint is resolved and you confirm satisfaction, you can rate the official from 1 to 5 stars. Your feedback helps improve service quality and is used for the official leaderboard.",
        "response_hi": "⭐ **रेटिंग:**\n\nशिकायत हल होने और आपके संतुष्ट होने की पुष्टि के बाद, आप अधिकारी को 1 से 5 स्टार रेटिंग दे सकते हैं। आपका फीडबैक सेवा सुधारने में मदद करता है।"
    },
    "contact": {
        "keywords": ["contact", "helpline", "support", "phone", "email", "call", "toll free", "संपर्क", "हेल्पलाइन", "customer care", "complaint number"],
        "response_en": "📞 **Contact support:**\n\n• Toll‑free Helpline: **1800‑XXX‑XXXX**\n• Email: **support@janseva.gov.in**\n• Working hours: Mon‑Sat, 9 AM – 6 PM",
        "response_hi": "📞 **सहायता से संपर्क करें:**\n\n• टॉल‑फ्री हेल्पलाइन: **1800‑XXX‑XXXX**\n• ईमेल: **support@janseva.gov.in**\n• कार्य घंटे: सोम‑शनि, सुबह 9 – शाम 6"
    }
}

def get_bot_response(user_msg: str, lang: str = "en") -> str:
    msg = user_msg.lower()
    msg = re.sub(r'[^\w\s]', '', msg)
    scores = {}
    for intent, data in INTENTS.items():
        score = 0
        for kw in data["keywords"]:
            if kw in msg:
                score += len(kw.split()) + 1
        if score > 0:
            scores[intent] = score
    if scores:
        best = max(scores, key=scores.get)
        return INTENTS[best][f"response_{lang}"]

    fallbacks_en = [
        "I'm still learning! 😊 You can ask me about:\n• How to file a complaint\n• Tracking your complaint status\n• Government schemes\n• Department assignments\n• SLA timelines\n• Ratings and feedback\n\nWhat would you like to know?",
        "Hmm, I didn't quite understand. Try asking:\n• 'How to file a complaint?'\n• 'Track my complaint'\n• 'Government schemes'\n• 'What is SLA?'",
        "I can help with complaints, schemes, departments, and SLA deadlines. Could you rephrase your question?"
    ]
    fallbacks_hi = [
        "मैं अभी सीख रहा हूं! 😊 आप पूछ सकते हैं:\n• शिकायत कैसे दर्ज करें\n• शिकायत की स्थिति ट्रैक करें\n• सरकारी योजनाएं\n• विभाग आवंटन\n• SLA समय सीमा\n• रेटिंग और फीडबैक\n\nआप क्या जानना चाहेंगे?",
        "क्षमा करें, मैं समझ नहीं पाया। कृपया पूछें:\n• 'शिकायत कैसे दर्ज करें?'\n• 'मेरी शिकायत ट्रैक करें'\n• 'सरकारी योजनाएं'\n• 'SLA क्या है?'",
        "मैं शिकायतों, योजनाओं, विभागों और SLA समय सीमा में मदद कर सकता हूं। कृपया अपना प्रश्न दोहराएं।"
    ]
    return random.choice(fallbacks_en if lang == "en" else fallbacks_hi)