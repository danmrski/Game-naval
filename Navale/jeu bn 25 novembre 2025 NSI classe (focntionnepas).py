import pygame
from pygame.locals import *
import random
import time

# Initialisation de Pygame
pygame.init()

# --- CONSTANTES DE JEU ---
TAILLE_PLATEAU = 10
CASE_TAILLE = 40 

# Marqueurs de la grille
MARQUEUR_EAU = 'O'
MARQUEUR_TOUCHE = 'X' 
MARQUEUR_MANQUE = 'M'

# Liste des bateaux (nom, taille)
BATEAUX = [
    ("Porte-avions", 5),
    ("Croiseur", 4),
    ("Contre-torpilleur", 3),
    ("Torpilleur 1", 2),
    ("Torpilleur 2", 2)
]

# --- ÉTATS SIMPLIFIÉS ---
ETAT_PLACEMENT = 0      # Le joueur place ses bateaux
ETAT_TOUR_JOUEUR = 1    # Le joueur clique sur la grille IA
ETAT_TOUR_IA = 2        # L'IA tire sur la grille du joueur

# Création de la fenêtre
FENETRE_LARGEUR = 800
FENETRE_HAUTEUR = 600
fenetre = pygame.display.set_mode((FENETRE_LARGEUR, FENETRE_HAUTEUR))
pygame.display.set_caption("Bataille Navale Simplifiée")

# --- PARAMÈTRES GRAPHIQUES ET CHEMINS (À AJUSTER) ---
BASE_PATH = "C:/Users/dmircevski/Downloads/Navale/"

# Chargement simplifié des images (Réutilisons les noms pour la clarté)
def charger_image(nom_fichier, taille, alpha=True):
    path = BASE_PATH + nom_fichier
    try:
        img = pygame.image.load(path)
        if alpha: img = img.convert_alpha()
        else: img = img.convert()
        return pygame.transform.scale(img, taille)
    except pygame.error:
        print(f"Erreur: Image {nom_fichier} manquante ou chemin incorrect. Utilisation d'un carré de couleur.")
        temp_surf = pygame.Surface(taille)
        temp_surf.fill((255, 0, 255) if alpha else (100, 100, 100))
        return temp_surf

def set_alpha_for_images(image_raw, alpha=100):
    image_copy = image_raw.copy()
    image_copy.set_alpha(alpha)
    return image_copy

# Images
fond_plateau = charger_image("fondbateau1.png", (800, 600), alpha=False)
bateau_case_raw = pygame.image.load(BASE_PATH + "casebateau.png").convert_alpha()
bateaudebut_case_raw = pygame.image.load(BASE_PATH + "casebateaudebut.png").convert_alpha()
bateau_case_resized = pygame.transform.scale(bateau_case_raw, (CASE_TAILLE, CASE_TAILLE))
bateaudebut_case_resized_default = pygame.transform.scale(bateaudebut_case_raw, (CASE_TAILLE, CASE_TAILLE))

# Fantômes (Placement)
bateau_case_fantome_resized = pygame.transform.scale(set_alpha_for_images(bateau_case_raw), (CASE_TAILLE, CASE_TAILLE))
bateaudebut_case_fantome_resized_default = pygame.transform.scale(set_alpha_for_images(bateaudebut_case_raw), (CASE_TAILLE, CASE_TAILLE))

case_combat_vide = charger_image("casefantome.png", (CASE_TAILLE, CASE_TAILLE))
case_combat_croix = charger_image("casefantomecroix.png", (CASE_TAILLE, CASE_TAILLE))
case_combat_rond = charger_image("casefantomemiss.png", (CASE_TAILLE, CASE_TAILLE))

# Polices
FONT = pygame.font.Font(None, 36)

# --- VARIABLES D'ÉTAT DU JEU ---
etat_du_jeu = ETAT_PLACEMENT 
bateaux_a_placer = list(BATEAUX) 
bateau_actuel_index = 0
bateau_horizontal = True 

# Plateaux
def creer_plateau(taille):
    return [[MARQUEUR_EAU for _ in range(taille)] for _ in range(taille)]

plateau_joueur = creer_plateau(TAILLE_PLATEAU)
plateau_ia = creer_plateau(TAILLE_PLATEAU)
plateau_tirs = creer_plateau(TAILLE_PLATEAU) # Tirs du joueur sur l'IA

# --- FONCTIONS DE BASE ---

def peut_placer(plateau, ligne, colonne, taille, horizontal):
    # Vérification des limites et des collisions
    if horizontal:
        if colonne + taille > TAILLE_PLATEAU: return False
        for i in range(taille):
            if plateau[ligne][colonne + i] != MARQUEUR_EAU: return False
    else:
        if ligne + taille > TAILLE_PLATEAU: return False
        for i in range(taille):
            if plateau[ligne + i][colonne] != MARQUEUR_EAU: return False
    return True

def placer_bateau(plateau, ligne, colonne, taille, horizontal, nom):
    marqueur_corps = nom[0]
    marqueur_debut = nom[0] + 'D'
    
    if horizontal:
        plateau[ligne][colonne] = marqueur_debut
        for i in range(1, taille):
            plateau[ligne][colonne + i] = marqueur_corps
    else:
        plateau[ligne][colonne] = marqueur_debut
        for i in range(1, taille):
            plateau[ligne + i][colonne] = marqueur_corps

def generer_bateaux(plateau, bateaux):
    # Placement des bateaux pour l'IA
    for nom, taille in bateaux:
        horizontal = random.choice([True, False])
        while True:
            ligne = random.randint(0, TAILLE_PLATEAU - 1)
            colonne = random.randint(0, TAILLE_PLATEAU - 1)
            if peut_placer(plateau, ligne, colonne, taille, horizontal):
                placer_bateau(plateau, ligne, colonne, taille, horizontal, nom)
                break
                
def tour_bot(plateau_cible):
    # Le bot tire aléatoirement sur le plateau du joueur
    while True:
        ligne = random.randint(0, TAILLE_PLATEAU - 1)
        colonne = random.randint(0, TAILLE_PLATEAU - 1)
        # S'assurer que l'IA ne tire pas deux fois sur la même case marquée
        if plateau_cible[ligne][colonne] not in (MARQUEUR_TOUCHE, MARQUEUR_MANQUE):
            break
            
    cible = plateau_cible[ligne][colonne]
    
    if cible == MARQUEUR_EAU:
        plateau_cible[ligne][colonne] = MARQUEUR_MANQUE
        return "À l'eau!", (ligne, colonne)
    else:
        # C'est une partie de bateau (marquée par lettre ou lettre + 'D')
        plateau_cible[ligne][colonne] = MARQUEUR_TOUCHE
        return "Touché!", (ligne, colonne)

# Plaçons les bateaux de l'IA immédiatement
generer_bateaux(plateau_ia, BATEAUX)

# --- FONCTION DESSINER_PLATEAU SIMPLIFIÉE ---
def dessiner_plateau(fenetre, plateau, x_offset, y_offset, mode="placement", fantome_data=None):
    """Dessine une grille de jeu à une position donnée."""
    
    for i in range(TAILLE_PLATEAU):
        for j in range(TAILLE_PLATEAU):
            x_pos = j * CASE_TAILLE + x_offset
            y_pos = i * CASE_TAILLE + y_offset
            
            # Dessiner le fond (Eau)
            pygame.draw.rect(fenetre, (255, 255, 255), (x_pos, y_pos, CASE_TAILLE, CASE_TAILLE))
            pygame.draw.rect(fenetre, (255, 165, 0), (x_pos, y_pos, CASE_TAILLE, CASE_TAILLE), 2)
            
            marqueur = plateau[i][j]
            
            # MODE COMBAT (Affichage des tirs uniquement sur grille masquée)
            if mode == "tir":
                if marqueur == MARQUEUR_EAU:
                    fenetre.blit(case_combat_vide, (x_pos, y_pos))
                elif marqueur == MARQUEUR_TOUCHE:
                    fenetre.blit(case_combat_croix, (x_pos, y_pos))
                elif marqueur == MARQUEUR_MANQUE:
                    fenetre.blit(case_combat_rond, (x_pos, y_pos))

            # MODE PLACEMENT & JOUEUR (Affichage des bateaux et des tirs adverses)
            elif mode in ("placement", "joueur"):
                # 1. Dessin des Bateaux
                if marqueur not in (MARQUEUR_EAU, MARQUEUR_TOUCHE, MARQUEUR_MANQUE):
                    
                    if marqueur.endswith('D'): # Début
                        is_vertical = (i + 1 < TAILLE_PLATEAU and plateau[i + 1][j] == marqueur[0])
                        rotation = 0 if is_vertical else 90 
                        image_a_afficher = pygame.transform.rotate(bateaudebut_case_resized_default, rotation)
                        fenetre.blit(image_a_afficher, (x_pos, y_pos))
                    else: # Corps
                        fenetre.blit(bateau_case_resized, (x_pos, y_pos))
                
                # 2. Dessin des Tirs (si l'IA a tiré sur ce plateau)
                if marqueur == MARQUEUR_TOUCHE:
                    fenetre.blit(croix_image, (x_pos, y_pos))
                elif marqueur == MARQUEUR_MANQUE:
                    fenetre.blit(rond_image, (x_pos, y_pos))
                    
    # Dessin du BATEAU FANTÔME (Uniquement en mode placement)
    if mode == "placement" and fantome_data:
        ligne_start, colonne_start, taille, horizontal = fantome_data
        rotation = 90 if horizontal else 0
        debut_fantome_image_rotatee = pygame.transform.rotate(bateaudebut_case_fantome_resized_default, rotation)
        
        for k in range(taille):
            i, j = (ligne_start, colonne_start + k) if horizontal else (ligne_start + k, colonne_start)
            
            if 0 <= i < TAILLE_PLATEAU and 0 <= j < TAILLE_PLATEAU:
                x_pos = j * CASE_TAILLE + x_offset
                y_pos = i * CASE_TAILLE + y_offset
                
                if k == 0:
                    fenetre.blit(debut_fantome_image_rotatee, (x_pos, y_pos))
                else:
                    fenetre.blit(bateau_case_fantome_resized, (x_pos, y_pos))


# --- BOUCLE PRINCIPALE ---
continuer = True
while continuer:
    
    # Paramètres de la grille (pour centrer)
    X_OFFSET = (FENETRE_LARGEUR - TAILLE_PLATEAU * CASE_TAILLE) // 2 
    Y_OFFSET = (FENETRE_HAUTEUR - TAILLE_PLATEAU * CASE_TAILLE) // 2 

    # Variables de détection de souris
    fantome_data = None
    colonne_cible, ligne_cible = -1, -1
    
    pos_souris = pygame.mouse.get_pos()
    x_souris, y_souris = pos_souris
    
    # Conversion de la position de la souris en coordonnées de grille
    if etat_du_jeu in (ETAT_PLACEMENT, ETAT_TOUR_JOUEUR):
        colonne_cible = (x_souris - X_OFFSET) // CASE_TAILLE
        ligne_cible = (y_souris - Y_OFFSET) // CASE_TAILLE
        
    # LOGIQUE DU FANTÔME DE PLACEMENT
    if etat_du_jeu == ETAT_PLACEMENT and bateau_actuel_index < len(bateaux_a_placer):
        nom, taille = bateaux_a_placer[bateau_actuel_index]
        if 0 <= ligne_cible < TAILLE_PLATEAU and 0 <= colonne_cible < TAILLE_PLATEAU:
            if peut_placer(plateau_joueur, ligne_cible, colonne_cible, taille, bateau_horizontal):
                fantome_data = (ligne_cible, colonne_cible, taille, bateau_horizontal)
            
    # --- GESTION DES ÉVÉNEMENTS ---
    for event in pygame.event.get():
        if event.type == QUIT:
            continuer = False
        
        elif event.type == KEYDOWN:
            if event.key == K_r and etat_du_jeu == ETAT_PLACEMENT:
                bateau_horizontal = not bateau_horizontal
            
        elif event.type == MOUSEBUTTONDOWN and event.button == 1: # Clic gauche
            
            # 1. PHASE DE PLACEMENT
            if etat_du_jeu == ETAT_PLACEMENT and fantome_data is not None:
                ligne_debut, colonne_debut, taille, horizontal = fantome_data
                nom, _ = bateaux_a_placer[bateau_actuel_index]
                
                placer_bateau(plateau_joueur, ligne_debut, colonne_debut, taille, horizontal, nom)
                bateau_actuel_index += 1
                
                if bateau_actuel_index >= len(bateaux_a_placer):
                    etat_du_jeu = ETAT_TOUR_JOUEUR # Placement terminé, on passe au combat!

            # 2. PHASE DE TIR DU JOUEUR
            elif etat_du_jeu == ETAT_TOUR_JOUEUR:
                if 0 <= ligne_cible < TAILLE_PLATEAU and 0 <= colonne_cible < TAILLE_PLATEAU:
                    if plateau_tirs[ligne_cible][colonne_cible] == MARQUEUR_EAU:
                        
                        cible = plateau_ia[ligne_cible][colonne_cible]
                        resultat = ""
                        
                        if cible != MARQUEUR_EAU and cible not in (MARQUEUR_TOUCHE, MARQUEUR_MANQUE):
                            # TOUCHÉ
                            plateau_tirs[ligne_cible][colonne_cible] = MARQUEUR_TOUCHE
                            plateau_ia[ligne_cible][colonne_cible] = MARQUEUR_TOUCHE
                            resultat = "Touché!"
                        else:
                            # MANQUÉ
                            plateau_tirs[ligne_cible][colonne_cible] = MARQUEUR_MANQUE
                            resultat = "À l'eau!"
                        
                        print(f"Joueur tire en ({ligne_cible},{colonne_cible}): {resultat}")
                        
                        # Affichage du résultat et passage au tour de le bot
                        etat_du_jeu = ETAT_TOUR_BOT # Passer au tour de le bot (après affichage)
                        
    # --- LOGIQUE DU JEU ---
    message_etat = ""
    
    if etat_du_jeu == ETAT_TOUR_BOT:
        # L'IA tire
        message_ia, coord_tir = tour_ia(plateau_joueur)
        message_etat = f"Le fantome a tiré en {coord_tir}: {message_ia}"
        
        # Pause pour laisser le temps de voir le tir de l'IA (IMPORTANT pour la visibilité)
        pygame.time.delay(1000) 
        
        etat_du_jeu = ETAT_TOUR_JOUEUR # Retour au tour du joueur

    elif etat_du_jeu == ETAT_PLACEMENT:
        message_etat = f"Placez le {bateaux_a_placer[bateau_actuel_index][0]} (Taille {bateaux_a_placer[bateau_actuel_index][1]}). Touche R pour tourner."
    
    elif etat_du_jeu == ETAT_TOUR_JOUEUR:
        message_etat = "Votre Tour : Cliquez sur une case pour tirer sur la flotte ennemie."
        
    # --- AFFICHAGE ---
    fenetre.blit(fond_plateau, (0, 0))

    # Dessin du plateau
    if etat_du_jeu == ETAT_PLACEMENT:
        dessiner_plateau(fenetre, plateau_joueur, X_OFFSET, Y_OFFSET, mode="placement", fantome_data=fantome_data)
    
    elif etat_du_jeu == ETAT_TOUR_JOUEUR:
        # Grille de tirs du Joueur (Plateau IA masqué)
        dessiner_plateau(fenetre, plateau_tirs, X_OFFSET - 200, Y_OFFSET, mode="tir")
        # Grille du Joueur (pour voir les tirs de l'IA)
        dessiner_plateau(fenetre, plateau_joueur, X_OFFSET + 200, Y_OFFSET, mode="joueur")

    elif etat_du_jeu == ETAT_TOUR_BOT:
        # Afficher la grille du joueur pour montrer le tir de l'IA
        dessiner_plateau(fenetre, plateau_joueur, X_OFFSET + 200, Y_OFFSET, mode="joueur")
        # Grille de tirs du Joueur (Plateau IA masqué)
        dessiner_plateau(fenetre, plateau_tirs, X_OFFSET - 200, Y_OFFSET, mode="tir")

    # Affichage du message d'état
    text_surface = FONT.render(message_etat, True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=(FENETRE_LARGEUR // 2, 50))
    fenetre.blit(text_surface, text_rect)

    pygame.display.update()

pygame.quit()