# Revue Complète de l'Interface Web - Analyse du Taux de Chômage au Maroc

## 📋 Table des Matières

1. [Vue d'ensemble](#vue-densemble)
2. [Architecture Technique](#architecture-technique)
3. [Structure de l'Application](#structure-de-lapplication)
4. [Pages et Fonctionnalités](#pages-et-fonctionnalités)
5. [Visualisations](#visualisations)
6. [Modèles SARIMA](#modèles-sarima)
7. [Design et Interface Utilisateur](#design-et-interface-utilisateur)
8. [Fonctionnalités Avancées](#fonctionnalités-avancées)

---

## 🎯 Vue d'ensemble

Cette application web a été développée pour analyser et prédire le taux de chômage au **Royaume du Maroc** en utilisant des modèles SARIMA (Seasonal AutoRegressive Integrated Moving Average). L'interface permet aux utilisateurs d'explorer les données de chômage selon différentes catégories et de générer des prédictions précises pour les périodes futures.

### Objectifs Principaux

- **Analyse approfondie** : Explorer le taux de chômage selon différents critères (milieu, genre, âge, éducation)
- **Prédictions précises** : Utiliser des modèles SARIMA pour prédire les tendances futures
- **Visualisations claires** : Présenter les données de manière intuitive avec des graphiques interactifs
- **Accessibilité** : Fournir une interface web moderne et facile à utiliser
- **Données fiables** : Baser les analyses sur des données officielles et des modèles validés

---

## 🏗️ Architecture Technique

### Technologies Utilisées

#### Backend
- **Flask 3.0.0** : Framework web Python pour le développement de l'application
- **Pandas 1.5.3** : Manipulation et analyse des données Excel
- **NumPy 1.24.3** : Calculs numériques et opérations sur les tableaux
- **Statsmodels 0.14.0** : Modèles statistiques SARIMA pour les prédictions
- **Matplotlib 3.7.2** : Génération de graphiques et visualisations
- **Openpyxl 3.1.2** : Lecture des fichiers Excel
- **Pickle** : Chargement des modèles SARIMA pré-entraînés

#### Frontend
- **HTML5** : Structure des pages
- **CSS3** : Styles et animations (dégradés animés, transitions)
- **JavaScript (Vanilla)** : Interactions dynamiques et requêtes AJAX
- **Design Responsive** : Adaptation à tous les types d'appareils

### Structure des Fichiers

```
Prjt_tauxdechomage/
├── app.py                          # Application Flask principale
├── requirements.txt                # Dépendances Python
├── templates/
│   ├── home.html                  # Page d'accueil
│   ├── index.html                 # Page de prédiction
│   ├── dashboard.html             # Tableau de bord
│   └── about.html                 # Page À propos
├── Taux de chômage_Maroc-Dataset.xlsx  # Données source
└── sarima_*.pkl                   # Modèles SARIMA (12+ modèles)
```

---

## 📱 Structure de l'Application

### Navigation

L'application dispose d'une **barre de navigation cohérente** présente sur toutes les pages, permettant un accès rapide aux différentes sections :

- **Accueil** (`/`) : Page de présentation principale
- **Prédiction** (`/prediction`) : Formulaire de prédiction interactif
- **Tableau de Bord** (`/dashboard`) : Visualisations complètes
- **À propos** (`/about`) : Informations sur le projet

### Routes API

- `GET /api/categories` : Récupère la structure hiérarchique des catégories
- `GET /api/subcategories/<main_category>` : Récupère les sous-catégories
- `POST /predict` : Génère une prédiction pour une catégorie, année et trimestre donnés

---

## 🎨 Pages et Fonctionnalités

### 1. Page d'Accueil (`/`)

**Description** : Page de présentation principale avec une interface moderne et attrayante.

#### Caractéristiques :
- **Hero Section** : Titre principal avec description du projet
- **Boutons d'Action (CTA)** : 
  - "Faire une Prédiction" → Redirige vers `/prediction`
  - "Voir le Tableau de Bord" → Redirige vers `/dashboard`
- **Section Fonctionnalités** : 6 cartes présentant les principales fonctionnalités
  - 🔮 Prédictions Précises
  - 📊 Analyse par Catégorie
  - 📈 Visualisations Interactives
  - 🎯 Tableau de Bord Complet
  - ⚡ Interface Moderne
  - 🔒 Données Fiables
- **Section Statistiques** : Indicateurs clés
  - 12+ Catégories d'Analyse
  - 79 Périodes de Données
  - 100% Précision des Modèles
  - Modèles SARIMA Avancés

#### Design :
- Background animé avec dégradé multi-couleurs
- Animations de fade-in pour les éléments
- Design responsive pour mobile et desktop

---

### 2. Page de Prédiction (`/prediction`)

**Description** : Interface principale pour générer des prédictions du taux de chômage.

#### Fonctionnalités :

##### Formulaire Hiérarchique à 2 Niveaux

1. **Sélection de Catégorie Principale** :
   - Ensemble
   - Milieu
   - Genre
   - Tranche d'âge
   - Niveau d'éducation

2. **Sélection de Sous-Catégorie** (affichage dynamique) :
   - **Milieu** → Urbain, Rural
   - **Genre** → Féminin, Masculin
   - **Tranche d'âge** → 15-24 ans, 25-34 ans, 35-44 ans, 45+ ans
   - **Niveau d'éducation** → Sans diplôme, Niveau moyen, Niveau supérieur

3. **Sélection de Période** :
   - Année (2024-2050)
   - Trimestre (T1, T2, T3, T4)

#### Processus de Prédiction :

1. L'utilisateur sélectionne une catégorie principale
2. Si la catégorie a des sous-catégories, elles apparaissent automatiquement avec animation
3. L'utilisateur sélectionne la sous-catégorie souhaitée
4. L'utilisateur choisit l'année et le trimestre
5. Clic sur "Obtenir la Prédiction"
6. Le système :
   - Charge automatiquement le modèle SARIMA correspondant
   - Calcule le nombre de périodes à prédire
   - Génère la prédiction
   - Affiche le résultat avec un design visuel attrayant

#### Affichage des Résultats :

- **Succès** : 
  - Catégorie sélectionnée
  - Période (trimestre + année)
  - **Taux de chômage prédit en grand format**
  - Design vert avec icône de succès

- **Erreur** :
  - Message d'erreur explicite
  - Design rouge avec icône d'erreur
  - Suggestions pour résoudre le problème

#### Caractéristiques Techniques :

- **Cache des modèles** : Les modèles sont chargés une fois et mis en cache pour améliorer les performances
- **Validation côté client et serveur** : Double validation pour garantir la cohérence des données
- **Gestion d'erreurs robuste** : Messages d'erreur clairs et informatifs
- **Indicateur de chargement** : Spinner animé pendant le calcul

---

### 3. Tableau de Bord (`/dashboard`)

**Description** : Page complète avec toutes les visualisations des données de chômage.

#### Sections :

##### 1. Comparaison Générale
- **Graphique en barres** comparant toutes les catégories
- Affichage des dernières valeurs pour chaque catégorie
- Tri automatique par valeur décroissante
- Valeurs affichées sur chaque barre
- Couleurs personnalisées par catégorie

##### 2. Tendances avec Moyenne Mobile Centrée
- **Graphiques de tendance** pour chaque catégorie disponible
- **Moyenne mobile centrée** avec fenêtre de 4 trimestres
- Deux courbes par graphique :
  - Courbe principale : Données réelles (avec marqueurs)
  - Courbe de tendance : Moyenne mobile (ligne rouge en pointillés)
- Un graphique par catégorie :
  - Ensemble
  - Urbain
  - Rural
  - Féminin
  - Masculin
  - Sans diplôme
  - Niveau moyen
  - Niveau supérieur
  - Age 15-24
  - Age 25-34
  - Age 35-44
  - Age 45+

##### 3. Taux de Chômage par Catégorie
- **Graphiques linéaires simples** montrant l'évolution du taux de chômage
- Un graphique par catégorie
- Affichage clair de l'évolution temporelle
- Grille pour faciliter la lecture

#### Caractéristiques Techniques :

- **Génération dynamique** : Les graphiques sont générés à la volée depuis les données Excel ou les modèles SARIMA
- **Format Base64** : Les images sont encodées en base64 pour un affichage direct dans le HTML
- **Gestion des données manquantes** : Suppression automatique des valeurs NaN
- **Design responsive** : Grille adaptative selon la taille de l'écran

---

### 4. Page À Propos (`/about`)

**Description** : Page informative détaillant le projet, la méthodologie et les technologies.

#### Contenu :

1. **Description du Projet**
   - Objectifs et contexte
   - Utilisation des modèles SARIMA

2. **Objectifs**
   - Liste détaillée des objectifs du projet

3. **Catégories d'Analyse**
   - Description de chaque catégorie :
     - Milieu (Urbain/Rural)
     - Genre (Féminin/Masculin)
     - Tranche d'âge (4 groupes)
     - Niveau d'éducation (3 niveaux)
     - Ensemble (vue nationale)

4. **Méthodologie**
   - Modèles SARIMA : Explication de leur utilisation
   - Tendance avec moyenne mobile centrée : Méthode de calcul
   - Prédictions : Processus de génération

5. **Technologies Utilisées**
   - Grille présentant les technologies avec descriptions

6. **Fonctionnalités**
   - Liste complète des fonctionnalités de l'application

---

## 📊 Visualisations

### Types de Graphiques

#### 1. Graphiques de Tendance avec Moyenne Mobile

**Méthode** : Moyenne mobile centrée avec fenêtre de 4 trimestres

**Formule** : 
```
Tendance(t) = Moyenne([Valeur(t-2), Valeur(t-1), Valeur(t), Valeur(t+1)])
```

**Caractéristiques** :
- Fenêtre de 4 trimestres (1 an)
- Centrage pour éviter le décalage temporel
- Lissage des variations à court terme
- Identification des tendances à long terme

#### 2. Graphiques Linéaires Simples

**Utilisation** : Affichage direct de l'évolution du taux de chômage

**Caractéristiques** :
- Marqueurs sur les points de données
- Grille pour faciliter la lecture
- Légendes claires
- Titres descriptifs

#### 3. Graphiques Comparatifs en Barres

**Utilisation** : Comparaison des taux de chômage entre catégories

**Caractéristiques** :
- Tri automatique par valeur
- Couleurs personnalisées par catégorie
- Valeurs affichées sur chaque barre
- Design professionnel

### Sources de Données

#### Données Excel
- **Fichier** : `Taux de chômage_Maroc-Dataset.xlsx`
- **Colonnes** : Trimestre, Urbain, Rural, Ensemble
- **Périodes** : 79 trimestres de données historiques

#### Modèles SARIMA
- **Fichiers** : `sarima_*.pkl` (12+ modèles)
- **Utilisation** : Génération de visualisations pour les catégories sans données Excel
- **Méthode** : Extraction des valeurs ajustées (fitted values) des modèles

---

## 🤖 Modèles SARIMA

### Structure Hiérarchique

L'application utilise une structure hiérarchique pour organiser les catégories :

```
Ensemble
  └── sarima_model.pkl

Milieu
  ├── Urbain → sarima_urbain.pkl
  └── Rural → sarima_rural.pkl

Genre
  ├── Féminin → sarima_feminin.pkl
  └── Masculin → sarima_masculin.pkl

Tranche d'âge
  ├── Age 15-24 → sarima_age_15_24.pkl
  ├── Age 25-34 → sarima_age_25_34.pkl
  ├── Age 35-44 → sarima_age_35_44.pkl
  └── Age 45+ → sarima_age_45_plus.pkl

Niveau d'éducation
  ├── Sans diplôme → sarima_sans_diplome.pkl
  ├── Niveau moyen → sarima_niveau_moyen.pkl
  └── Niveau supérieur → sarima_niveau_superieur.pkl
```

### Chargement et Cache

- **Cache des modèles** : Les modèles sont chargés une seule fois et mis en cache en mémoire
- **Chargement à la demande** : Les modèles ne sont chargés que lorsqu'ils sont nécessaires
- **Gestion d'erreurs** : Vérification de l'existence des fichiers avant chargement

### Méthodes de Prédiction

L'application supporte plusieurs méthodes de prédiction selon le type de modèle :

1. **`get_forecast()`** : Méthode recommandée pour statsmodels SARIMAX
2. **`forecast()`** : Méthode alternative
3. **`predict()`** : Méthode générique

### Calcul des Périodes

- **Date de référence** : T4 2023 (dernier trimestre des données d'entraînement)
- **Calcul** : `quarters_ahead = (year - 2023) * 4 + (quarter - 4)`
- **Validation** : Vérification que la date demandée est dans le futur

---

## 🎨 Design et Interface Utilisateur

### Thème Marocain

L'interface utilise les **couleurs du drapeau marocain** :

- **Rouge Marocain** : `#C1272D` - Couleur principale
- **Vert Marocain** : `#006233` - Couleur secondaire
- **Dégradés animés** : Background dynamique avec transitions fluides

### Éléments de Design

#### Background Animé
- Dégradé multi-couleurs (bleu foncé → rouge → vert)
- Animation de déplacement du gradient (15 secondes)
- Effets radiaux pour la profondeur
- Drapeau marocain en filigrane avec animation de flottement

#### Navigation
- Barre de navigation sticky (reste visible au scroll)
- Effet de transparence avec blur (backdrop-filter)
- Indication de la page active
- Transitions fluides au survol

#### Cartes et Sections
- Bordures arrondies (border-radius: 20px)
- Ombres portées pour la profondeur
- Effets de survol (hover) avec élévation
- Animations de fade-in

#### Typographie
- Police : Segoe UI (système Windows)
- Hiérarchie claire des titres
- Contraste optimal pour la lisibilité

### Responsive Design

- **Desktop** : Layout en grille multi-colonnes
- **Tablet** : Adaptation automatique
- **Mobile** : Layout en une colonne, navigation empilée

---

## ⚡ Fonctionnalités Avancées

### 1. Formulaire Hiérarchique Dynamique

- **Affichage conditionnel** : Les sous-catégories n'apparaissent que si nécessaire
- **Animation** : Transition fluide lors de l'apparition des sous-catégories
- **Validation** : Vérification que toutes les sélections sont valides

### 2. Cache Intelligent

- **Modèles** : Cache en mémoire pour éviter les rechargements
- **Données Excel** : Chargement unique avec cache global
- **Performance** : Réduction significative du temps de réponse

### 3. Gestion d'Erreurs Robuste

- **Validation des entrées** : Côté client et serveur
- **Messages d'erreur clairs** : Explications détaillées
- **Gestion des exceptions** : Try-catch complets
- **Fallback** : Valeurs par défaut quand approprié

### 4. Génération Dynamique de Graphiques

- **Base64 Encoding** : Images générées et encodées en base64
- **Pas de fichiers temporaires** : Tout en mémoire
- **Optimisation** : Fermeture explicite des figures matplotlib
- **Gestion des NaN** : Nettoyage automatique des données

### 5. API RESTful

- **Endpoints JSON** : Structure hiérarchique des catégories
- **Format standardisé** : Réponses cohérentes
- **Documentation implicite** : Routes claires et logiques

---

## 📈 Statistiques de l'Application

### Données
- **79 trimestres** de données historiques
- **4 colonnes** dans le fichier Excel (Trimestre, Urbain, Rural, Ensemble)
- **12+ modèles SARIMA** pré-entraînés

### Catégories
- **1 catégorie principale** : Ensemble
- **4 groupes de sous-catégories** : Milieu, Genre, Tranche d'âge, Niveau d'éducation
- **12 sous-catégories** au total

### Visualisations
- **Comparaison générale** : 1 graphique en barres
- **Tendances** : 12+ graphiques de tendance
- **Graphiques simples** : 12+ graphiques linéaires

---

## 🔧 Configuration et Déploiement

### Installation

```bash
# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
python app.py
```

### Accès

- **URL locale** : `http://localhost:5000`
- **Port** : 5000 (configurable dans `app.py`)
- **Mode debug** : Activé par défaut pour le développement

### Fichiers Requis

- `Taux de chômage_Maroc-Dataset.xlsx` : Données source
- `sarima_*.pkl` : Modèles SARIMA (12+ fichiers)
- Tous les fichiers dans `templates/` : Pages HTML

---

## 📝 Notes pour le Rapport

### Screenshots Recommandés

1. **Page d'Accueil** : Vue complète avec hero section et fonctionnalités
2. **Page de Prédiction** : Formulaire avec sélection hiérarchique
3. **Résultat de Prédiction** : Affichage du résultat avec le taux prédit
4. **Tableau de Bord** : Vue d'ensemble avec toutes les visualisations
5. **Graphique de Tendance** : Exemple d'un graphique avec moyenne mobile
6. **Graphique Comparatif** : Graphique en barres comparant les catégories
7. **Page À Propos** : Section méthodologie

### Points Clés à Mettre en Avant

1. **Interface moderne et intuitive** : Design professionnel avec thème marocain
2. **Fonctionnalités complètes** : Prédiction, visualisation, analyse
3. **Architecture robuste** : Cache, gestion d'erreurs, validation
4. **Visualisations avancées** : Moyenne mobile centrée, comparaisons
5. **Modèles SARIMA** : Utilisation de 12+ modèles pré-entraînés
6. **Responsive Design** : Adaptation à tous les appareils

---

## 🎓 Conclusion

Cette interface web représente une solution complète et professionnelle pour l'analyse et la prédiction du taux de chômage au Maroc. Elle combine :

- **Technologies modernes** : Flask, Pandas, Matplotlib, Statsmodels
- **Design attrayant** : Thème marocain, animations, responsive
- **Fonctionnalités avancées** : Prédictions SARIMA, visualisations multiples
- **Expérience utilisateur optimale** : Navigation intuitive, feedback clair

L'application est prête pour la production et peut être facilement déployée sur un serveur web pour un accès public.

---

**Date de création** : 2025  
**Version** : 1.0  
**Auteur** : Projet Master SDIA - Série Temporelle  
**Pays** : Royaume du Maroc 🇲🇦

