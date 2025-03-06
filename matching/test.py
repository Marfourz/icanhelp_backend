from keybert import KeyBERT

# 🔹 Charger le modèle
kw_model = KeyBERT()

def extraire_competences_keybert(texte, top_n=5):
    """
    Utilise KeyBERT pour extraire les mots-clés les plus pertinents.
    """
    keywords = kw_model.extract_keywords(texte, keyphrase_ngram_range=(1, 2), stop_words="english")
    return [kw[0] for kw in keywords[:top_n]]

# 🔹 Exemple
phrase = "Je suis compétent en data science, développement en Python et intelligence artificielle."
competences = extraire_competences_keybert(phrase)

print("Compétences détectées :", competences)
