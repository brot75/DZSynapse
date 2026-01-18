# DZSynapse

Application de bureau locale sécurisée pour la gestion des patients et référentiel de procédures médicales.
Développé par **DevOpsSolutions**.

## Fonctionnalités
- **Gestion des Patients**: Création, Modification, Suppression, Recherche.
- **Sécurité**: Authentification par mot de passe haché (SHA-256) et gestion des rôles (Médecin/Opérateur).
- **Dossier Médical**: Suivi des interventions et stockage sécurisé des documents (Radios, Rapports, etc.).
- **Référentiel**: Base de connaissances des compétences standards (Collège Royal Canada).
- **Interface**: Moderne (Thème Dark Blue), entièrement en Français.

## Installation
1. Assurez-vous d'avoir Python 3.10+ installé.
2. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

## Lancement
Double-cliquez sur `run_app.bat` ou lancez via le terminal :
```bash
python main.py
```

## Identifiants par Défaut
| Rôle | Utilisateur | Mot de passe | Permissions |
|------|-------------|--------------|-------------|
| **Médecin (Admin)** | `doctor` | `admin123` | Accès complet (Écriture, Suppression) |
| **Opérateur** | `operator` | `user123` | Lecture seule (Consultation uniquement) |

## Structure des Dossiers
- `main.py`: Point d'entrée de l'application.
- `database.py`: Gestion de la base de données et authentification.
- `dzsynapse.db`: Fichier de base de données SQLite (créé au lancement).
- `patient_docs/`: Stockage local des documents importés par patient.

# DZSynapse
Application de gestion de chirurgie pédiatrique locale et sécurisée
