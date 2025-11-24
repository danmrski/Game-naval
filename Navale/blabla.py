import pygame
from pygame.locals import *
import random

# Initialisation
pygame.init()
TAILLE_PLATEAU = 10
fenetre = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Bataille Navale - Backstory")

# Bateaux
BATEAUX = [
    ("Porte-avions", 5),
    ("Croiseur", 4),
    ("Contre-torpilleur", 3),
    ("Torpilleur 1", 2),
    ("Torpilleur 2", 2)
]

# Images
fond = pygame.image.load("C:/Users/danam/Downloads/Navale/fond1.png").convert()
fond_plateau = pygame.image.load("C:/Users/danam/Downloads/Navale/fondbateau1.png").convert()
bateau_case = pygame.image.load("C:/Users/danam/Downloads/Navale/bateauc.png").convert()
bateaudebut_case = pygame.image.load("C:/Users/danam/Downloads/Navale/casebateaudebut.png").convert()
bateau_casecroix = pygame.image.load("C:/Users/danam/Downloads/Navale/casebateaucroix.png").convert()
bateaudebut_casecroix = pygame.image.load("C:/Users/danam/Downloads/Navale/casebateaudebutcroix.png").convert()

backstory_images = [
    pygame.image.load("C:/Users/danam/Downloads/Navale/scene1.png").convert(),
    pygame.image.load("C:/Users/danam/Downloads/Navale/scene2.png").convert(),
    pygame.image.load("C:/Users/danam/Downloads/Navale/scene3.png").convert(),
    pygame.image.load("C:/Users/danam/Downloads/Navale/lettred1.png").convert(),
    pygame.image.load("C:/Users/danam/Downloads/Navale/lettred2.png").convert(),
    pygame.image.load("C:/Users/danam/Downloads/Navale/lettred3.png").convert(),
]

# Sons
pygame.mixer.init()
sound = pygame.mixer.Sound('hallomusic.mp3')
soundstory = pygame.mixer.Sound('piratebackstory.mp3')
soundbateau1 = pygame.mixer.Sound('piratebateau.mp3')
soundstory.stop()
sound.play()

# État du jeu
backstory_active = False
current_backstory_index = 0
bateaux_places = False
plateau = None

# Plateau
def creer_plateau(taille):
    return [[{"type": "eau", "touche": False, "est_poupe": False} for _ in range(taille)] for _ in range(taille)]

def peut_placer(plateau, ligne, colonne, taille, horizontal):
    if horizontal:
        if colonne + taille > TAILLE_PLATEAU:
            return False
        for i in range(taille):
            if plateau[ligne][colonne + i]["type"] != "eau":
                return False
    else:
        if ligne + taille > TAILLE_PLATEAU:
            return False
        for i in range(taille):
            if plateau[ligne + i][colonne]["type"] != "eau":
                return False
    return True

def placer_bateau(plateau, ligne, colonne, taille, horizontal, nom):
    for i in range(taille):
        est_poupe = i == taille - 1
        if horizontal:
            plateau[ligne][colonne + i] = {"type": "bateau", "touche": False, "est_poupe": est_poupe}
        else:
            plateau[ligne + i][colonne] = {"type": "bateau", "touche": False, "est_poupe": est_poupe}

def generer_bateaux(plateau, bateaux):
    for nom, taille in bateaux:
        horizontal = random.choice([True, False])
        while True:
            ligne = random.randint(0, TAILLE_PLATEAU - 1)
            colonne = random.randint(0, TAILLE_PLATEAU - 1)
            if peut_placer(plateau, ligne, colonne, taille, horizontal):
                placer_bateau(plateau, ligne, colonne, taille, horizontal, nom)
                break

def dessiner_plateau(fenetre, plateau):
    case_taille = 40
    for i in range(TAILLE_PLATEAU):
        for j in range(TAILLE_PLATEAU):
            x = j * case_taille + 200
            y = i * case_taille + 100
            case = plateau[i][j]

            if case["type"] == "eau":
                pygame.draw.rect(fenetre, (255, 255, 255), (x, y, case_taille, case_taille))
                pygame.draw.rect(fenetre, (255, 165, 0), (x, y, case_taille, case_taille), 2)
            elif case["type"] == "bateau":
                if case["touche"]:
                    image = bateaudebut_casecroix if case["est_poupe"] else bateau_casecroix
                else:
                    image = bateaudebut_case if case["est_poupe"] else bateau_case
                fenetre.blit(image, (x, y))

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
            fenetre.blit(fond_plateau, (0, 0))
            dessiner_plateau(fenetre, plateau)
        else:
            fenetre.blit(fond, (0, 0))
    pygame.display.update()

pygame.quit()
