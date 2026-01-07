# Robotcup2025-2026

Pin de la raspberry pi

<img src="Assets/pingpio.jfif" alt="pingpio" width="400"/>

## Développement

Pour éviter les erreurs avec logging, veuillez créer un fichier logs/ !

Avant de commit sur le github bien lancer cette commande :
`bash commit_verification.sh`

Et vérifier qu'il n'y a pas d'erreurs ni dans le formatage ni dans le code (le dossier [examples](./examples/) ne compte pas dans la vérification de format).

## LED

Branchement + sur pin 7 et - sur une GND de base. Penser à rajouter une résistance 220Ω.

## Motor

Branchement + sur une 5V et - sur une GND et la troisième sur pin 12

## Potentiometre grove

Il faut le brancher sur les port A0,A2,A4,A6.
On recupère les données sur le pin avec le même numero que le port. (voir test_potentiometre.py)
