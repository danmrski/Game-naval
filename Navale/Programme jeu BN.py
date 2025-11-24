import pygame
from pygame.locals import *
import random
# Initialisation de Pygame
pygame.init()
# Taille du plateau
TAILLE_PLATEAU = 10
# Liste des bateaux (nom, taille)
BATEAUX = [
    ("Porte-avions", 5),
    ("Croiseur", 4),
    ("Contre-torpilleur", 3),
    ("Torpilleur 1", 2),
    ("Torpilleur 2", 2)
]
# Création de la fenêtre
fenetre = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Bataille Navale - Backstory")
# Chargement du fond
fond = pygame.image.load("C:/Users/danam/Downloads/Navale/fond1.png").convert()
fond_plateau = pygame.image.load("C:/Users/danam/Downloads/Navale/fondbateau1.png").convert()


#bateau_case = pygame.image.load("C:/Users/danam/Downloads/Navale/casebateau.png").convert()
#bateaudebut_case = pygame.image.load("C:/Users/danam/Downloads/Navale/casebateaudebut.png").convert()
#bateau_casecroix = pygame.image.load("C:/Users/danam/Downloads/Navale/casebateaucroix.png").convert()
#bateaudebut_casecroix = pygame.image.load("C:/Users/danam/Downloads/Navale/casebateaudebutcroix.png").convert()

backstory_images = [
    pygame.image.load("C:/Users/danam/Downloads/Navale/scene1.png").convert(),
    pygame.image.load("C:/Users/danam/Downloads/Navale/scene2.png").convert(),
    pygame.image.load("C:/Users/danam/Downloads/Navale/scene3.png").convert(),
    pygame.image.load("C:/Users/danam/Downloads/Navale/lettred1.png").convert(),
    pygame.image.load("C:/Users/danam/Downloads/Navale/lettred2.png").convert(),
    pygame.image.load("C:/Users/danam/Downloads/Navale/lettred3.png").convert(),
]
# Initialisation du son
pygame.mixer.init()
sound = pygame.mixer.Sound('hallomusic.mp3')
soundstory = pygame.mixer.Sound('piratebackstory.mp3')
soundbateau1 = pygame.mixer.Sound('piratebateau.mp3')
soundstory.stop()
sound.play()

# Variables pour gérer l'état du jeu
backstory_active = False
current_backstory_index = 0
bateaux_places = False
plateau = None

# Créer un plateau vide
def creer_plateau(taille):
    return [["O" for _ in range(taille)] for _ in range(taille)]
# Vérifier si un bateau peut être placé
def peut_placer(plateau, ligne, colonne, taille, horizontal):
    if horizontal:
        if colonne + taille > TAILLE_PLATEAU:
            return False
        for i in range(taille):
            if plateau[ligne][colonne + i] != "O":
                return False
    else:
        if ligne + taille > TAILLE_PLATEAU:
            return False
        for i in range(taille):
            if plateau[ligne + i][colonne] != "O":
                return False
    return True

# Placer un bateau sur le plateau et le creer
def placer_bateau(plateau, ligne, colonne, taille, horizontal, nom):
    if horizontal:
        for i in range(taille):
            plateau[ligne][colonne + i] = nom[0]
    else:
        for i in range(taille):
            plateau[ligne + i][colonne] = nom[0]
            
# Générer aléatoirement les bateaux sur le plateau
def generer_bateaux(plateau, bateaux):
    for nom, taille in bateaux:
        horizontal = random.choice([True, False])
        while True:
            ligne = random.randint(0, TAILLE_PLATEAU - 1)
            colonne = random.randint(0, TAILLE_PLATEAU - 1)
            if peut_placer(plateau, ligne, colonne, taille, horizontal):
                placer_bateau(plateau, ligne, colonne, taille, horizontal, nom)
                break
# Dessiner le plateau
def dessiner_plateau(fenetre, plateau):
    case_taille = 40
    for i in range(TAILLE_PLATEAU):
        for j in range(TAILLE_PLATEAU):
            pygame.draw.rect(fenetre, (255, 255, 255),
                             (j * case_taille + 200, i * case_taille + 100, case_taille, case_taille))
            pygame.draw.rect(fenetre, (255, 165, 0),
                             (j * case_taille + 200, i * case_taille + 100, case_taille, case_taille), 2)
            if plateau[i][j] != "O":
                font = pygame.font.SysFont(None, 30)
                text = font.render(plateau[i][j], True, (255, 0, 0))
                fenetre.blit(text, (j * case_taille + 210, i * case_taille + 105))
# Boucle principale
continuer = True
while continuer:
    for event in pygame.event.get():
        if event.type == QUIT:
            continuer = False
        elif event.type == KEYDOWN:
            if event.key == K_SPACE and not backstory_active:
                backstory_active = True
                sound.stop()
                soundstory.play()
                current_backstory_index = 0
            elif event.key == K_e and backstory_active:
                current_backstory_index += 1
                if current_backstory_index >= len(backstory_images):
                    backstory_active = False
                    # Générer les bateaux une seule fois
                    if not bateaux_places:
                        plateau = creer_plateau(TAILLE_PLATEAU)
                        generer_bateaux(plateau, BATEAUX)
                        bateaux_places = True
                        
    # Affichage
    if backstory_active:
        fenetre.blit(backstory_images[current_backstory_index], (0, 0))
    else:
        if bateaux_places:
            soundstory.stop()
            soundbateau1.play()
            fenetre.blit(fond_plateau, (0, 0))  # Affiche le fond du plateau
            dessiner_plateau(fenetre, plateau)  # Dessine le plateau par-dessus
        else:
            fenetre.blit(fond, (0, 0))  # Affiche le fond principal si les bateaux ne sont pas encore placés
    pygame.display.update()
pygame.quit()