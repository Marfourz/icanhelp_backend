import csv
import random

# Définition des catégories avec leurs actions associées
categories = {
    "Sport": [
        "Faire du jogging", "Nager en piscine", "Jouer au tennis", "Faire du vélo", 
        "Pratiquer le yoga", "Courir un marathon", "Faire de la musculation", "Jouer au football",
        "Faire de l'escalade", "Pratiquer la boxe", "Faire du ski", "Jouer au basketball",
        "Faire de la randonnée", "Pratiquer le surf", "Faire de la danse", "Jouer au volleyball"
    ],
    
    "Cuisine": [
        "Préparer un gâteau", "Faire cuire des pâtes", "Éplucher des légumes", "Faire une omelette",
        "Préparer une salade", "Faire du pain", "Cuisiner un rôti", "Préparer une soupe",
        "Faire une tarte", "Cuisiner des légumes", "Préparer un dessert", "Faire une sauce",
        "Cuire du riz", "Préparer un smoothie", "Faire griller de la viande", "Préparer un plat"
    ],
    
    "Technologie": [
        "Programmer en Python", "Créer un site web", "Installer un logiciel", "Réparer un ordinateur",
        "Configurer un réseau", "Développer une application", "Analyser des données", "Créer une base de données",
        "Faire de la maintenance", "Optimiser un système", "Sécuriser un serveur", "Automatiser une tâche",
        "Créer un algorithme", "Tester un programme", "Déployer une application", "Monitorer un système"
    ],
    
    "Art_Musique": [
        "Peindre un tableau", "Jouer de la guitare", "Chanter une chanson", "Composer une mélodie",
        "Dessiner un portrait", "Jouer du piano", "Écrire une chanson", "Sculpter une statue",
        "Faire de la photographie", "Improviser au piano", "Créer une œuvre", "Jouer de la batterie",
        "Composer une chanson", "Peindre à l'aquarelle", "Jouer du violon", "Créer un dessin"
    ],
    
    "Education": [
        "Enseigner les mathématiques", "Donner un cours", "Corriger des copies", "Préparer une leçon",
        "Expliquer un concept", "Faire une présentation", "Animer un atelier", "Superviser des élèves",
        "Créer un cours", "Évaluer des étudiants", "Organiser une formation", "Donner des conseils",
        "Préparer un examen", "Faire du tutorat", "Animer une discussion", "Enseigner une langue"
    ],
    
    "Transport": [
        "Conduire une voiture", "Prendre le métro", "Faire du vélo", "Marcher en ville",
        "Prendre un bus", "Conduire un camion", "Utiliser un scooter", "Prendre l'avion",
        "Conduire une moto", "Utiliser un taxi", "Prendre le train", "Conduire une trottinette",
        "Faire de l'auto-stop", "Utiliser un vélo électrique", "Prendre un ferry", "Conduire un tracteur"
    ],
    
    "Communication": [
        "Passer un appel", "Envoyer un email", "Écrire un message", "Faire une présentation",
        "Animer une réunion", "Prendre la parole", "Rédiger un rapport", "Négocier un contrat",
        "Faire un discours", "Organiser une conférence", "Modérer un débat", "Interviewer quelqu'un",
        "Prendre la parole en public", "Rédiger une lettre", "Faire du networking", "Présenter un projet"
    ],
    
    "Maison_Jardin": [
        "Tondre la pelouse", "Arroser les plantes", "Nettoyer la maison", "Réparer une fuite",
        "Planter des fleurs", "Faire le ménage", "Peindre un mur", "Installer une étagère",
        "Tailler les arbres", "Faire la vaisselle", "Organiser un placard", "Réparer un meuble",
        "Entretenir le jardin", "Laver les vitres", "Ranger la maison", "Bricoler un objet"
    ],
    
    "Sante_Bien_etre": [
        "Faire de la méditation", "Consulter un médecin", "Prendre des vitamines", "Faire du stretching",
        "Aller chez le dentiste", "Faire un massage", "Pratiquer la relaxation", "Faire un bilan de santé",
        "Prendre soin de sa peau", "Faire de la physiothérapie", "Boire beaucoup d'eau", "Dormir suffisamment",
        "Faire de l'exercice", "Manger équilibré", "Gérer le stress", "Prendre l'air frais"
    ],
    
    "Shopping_Finance": [
        "Faire les courses", "Acheter des vêtements", "Gérer son budget", "Payer ses factures",
        "Comparer les prix", "Épargner de l'argent", "Investir en bourse", "Faire du shopping",
        "Négocier un prix", "Calculer ses dépenses", "Ouvrir un compte", "Demander un crédit",
        "Faire ses comptes", "Acheter en ligne", "Retourner un produit", "Gérer ses finances"
    ]
}

def generate_text1_pool():
    """Génère le pool de text1 avec récurrence de 1%"""
    all_actions = []
    for category_actions in categories.values():
        all_actions.extend(category_actions)
    
    # Pour 10000 lignes avec 1% de récurrence, on a besoin d'environ 100 textes uniques
    target_unique = int(10000 * 0.01)
    
    # Mélanger et prendre les premiers éléments
    random.shuffle(all_actions)
    text1_pool = all_actions[:target_unique]
    
    # S'assurer qu'on a assez d'éléments
    while len(text1_pool) < target_unique:
        text1_pool.extend(all_actions[:target_unique - len(text1_pool)])
    
    return text1_pool

def get_category_of_action(action):
    """Trouve la catégorie d'une action donnée"""
    for category, actions in categories.items():
        if action in actions:
            return category
    return None

def generate_text2_same_category(category):
    """Génère un text2 de la même catégorie"""
    return random.choice(categories[category])

def generate_text2_different_category(excluded_category):
    """Génère un text2 d'une catégorie différente"""
    other_categories = [cat for cat in categories.keys() if cat != excluded_category]
    chosen_category = random.choice(other_categories)
    return random.choice(categories[chosen_category])

def generate_dataset():
    """Génère le dataset complet"""
    text1_pool = generate_text1_pool()
    dataset = []
    
    for i in range(10000):
        # Choisir text1 du pool
        text1 = random.choice(text1_pool)
        
        # Trouver sa catégorie
        category1 = get_category_of_action(text1)
        
        # Décider du label (50% de chance pour chaque)
        label = random.choice([0, 1])
        
        if label == 1:
            # Même catégorie
            text2 = generate_text2_same_category(category1)
            # S'assurer que text2 est différent de text1
            while text2 == text1:
                text2 = generate_text2_same_category(category1)
        else:
            # Catégorie différente
            text2 = generate_text2_different_category(category1)
        
        dataset.append([text1, text2, label])
    
    return dataset

def save_dataset_to_csv(dataset, filename='dataset_10000.csv'):
    """Sauvegarde le dataset dans un fichier CSV"""
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Écrire l'en-tête
        writer.writerow(['text1', 'text2', 'label'])
        
        # Écrire les données
        writer.writerows(dataset)

def analyze_dataset(dataset):
    """Analyse le dataset généré"""
    text1_list = [row[0] for row in dataset]
    text1_unique = set(text1_list)
    
    label_distribution = {}
    for row in dataset:
        label = row[2]
        label_distribution[label] = label_distribution.get(label, 0) + 1
    
    print(f"Dataset généré avec succès !")
    print(f"Nombre total de lignes: {len(dataset)}")
    print(f"Nombre de text1 uniques: {len(text1_unique)}")
    print(f"Taux de récurrence réel: {len(text1_unique) / len(dataset) * 100:.1f}%")
    print(f"Distribution des labels: {label_distribution}")
    print(f"Pourcentage label 1: {label_distribution.get(1, 0) / len(dataset) * 100:.1f}%")
    print(f"Pourcentage label 0: {label_distribution.get(0, 0) / len(dataset) * 100:.1f}%")
    
    print(f"\nNombre de catégories: {len(categories)}")
    print("Catégories disponibles:")
    for i, category in enumerate(categories.keys(), 1):
        print(f"{i}. {category.replace('_', ' ')}")

def show_examples(dataset, n=10):
    """Affiche quelques exemples du dataset"""
    print(f"\n{n} premiers exemples:")
    for i in range(min(n, len(dataset))):
        text1, text2, label = dataset[i]
        cat1 = get_category_of_action(text1)
        cat2 = get_category_of_action(text2)
        same_cat = "✓" if cat1 == cat2 else "✗"
        print(f"{i+1:2d}. '{text1}' | '{text2}' | {label} | {same_cat} ({cat1} / {cat2})")

# Génération du dataset
print("Génération du dataset en cours...")
dataset = generate_dataset()

# Sauvegarde
save_dataset_to_csv(dataset)

# Analyse
analyze_dataset(dataset)

# Exemples
show_examples(dataset, 15)

print(f"\nFichier 'dataset_10000.csv' créé avec succès !")