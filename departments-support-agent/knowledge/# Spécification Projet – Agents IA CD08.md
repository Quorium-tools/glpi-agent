# Spécification Projet – Agents IA CD08

**Conseil Départemental des Ardennes**

Version 1.0 — Mai 2026
---

  

## Table des matières

  

1. [Contexte et objectifs](#1-contexte-et-objectifs)

2. [Plateforme commune : GLPI](#2-plateforme-commune--glpi)

3. [Architecture générale](#3-architecture-générale)

4. [Agent 1 – Help Desk IT](#4-agent-1--help-desk-it)

5. [Agent 2 – Départements](#5-agent-2--départements)

6. [Base documentaire – Exemples](#6-base-documentaire--exemples)

7. [Interface chat web](#7-interface-chat-web)

8. [Sécurité et contrôle d'accès](#8-sécurité-et-contrôle-daccès)

9. [Roadmap de déploiement](#9-roadmap-de-déploiement)

  

---

  

## 1. Contexte et objectifs

  

Le Conseil Départemental des Ardennes (CD08) regroupe plusieurs départements fonctionnels qui utilisent quotidiennement des outils informatiques partagés. La gestion des incidents, des demandes et des tâches est centralisée via **GLPI**.

  

### Problème actuel

  

- Les agents des départements non-IT (Finance, RH, Juridique…) contactent le Help Desk pour des questions simples et récurrentes (réinitialisation de mot de passe, accès VPN, problème d'impression).

- Le Help Desk est surchargé de tickets de faible complexité.

- Pas de self-service documentaire structuré.

  

### Objectif du projet

  

Déployer **deux agents IA conversationnels** accessibles via une interface chat web :

  

| Agent | Cible | Rôle |

|---|---|---|

| **Agent 1 – Help Desk IT** | Techniciens DSI / super admins | Manipulation complète de l'API GLPI |

| **Agent 2 – Départements** | Tous les agents CD08 non-IT | Réponses documentaires + GLPI basique + escalade téléphonique |

  

---

  

## 2. Plateforme commune : GLPI

  

GLPI est la plateforme centrale de ticketing et de gestion des actifs IT du CD08.

  

### Fonctionnalités GLPI utilisées 

- **Tickets** : création, modification, assignation, clôture, commentaires

- **Inventaire** : matériel, logiciels, utilisateurs

- **SLA** : suivi des délais de résolution

- **Base de connaissances** : articles de support internes

- **Statistiques** : charge par technicien, délais moyens, taux de résolution

### API GLPI

  

L'API REST GLPI sera utilisée par les deux agents. Les droits diffèrent selon l'agent :


```

Agent 1 → Session token super admin (lecture + écriture complète)

Agent 2 → Session token utilisateur (création ticket + lecture statut)

```
  
## 3. Architecture générale

```

┌────────────────────────────────────────────────────────┐

│ Interface Chat Web │

│ (deux URL distinctes selon le rôle) │

└──────────────────┬─────────────────┬───────────────────┘

│ │

┌────────▼──────┐ ┌───────▼────────┐

│ Agent 1 │ │ Agent 2 │

│ Help Desk IT │ │ Départements │

└────────┬──────┘ └───────┬────────┘

│ │

┌────────▼──────┐ ┌───────▼────────┐

│ API GLPI │ │ Base docs RAG │

│ (full admin) │ │ + API GLPI │

└───────────────┘ │ (standard) │

└───────┬────────┘

│ Urgence

📞 Téléphone

Help Desk IT

```  

## 4. Agent 1 – Help Desk IT

### 4.1 Utilisateurs cibles  

- Techniciens de la DSI

- Super administrateurs GLPI

- Responsable Help Desk

### 4.2 Capacités  

#### Gestion des tickets

- Créer un nouveau ticket (incident ou demande)

- Modifier un ticket existant (statut, priorité, technicien assigné)

- Ajouter un suivi ou commentaire

- Clôturer ou relancer un ticket

- Fusionner des tickets en doublon

  

#### Consultation et recherche

- Rechercher un ticket par numéro, utilisateur, mot-clé

- Lister les tickets ouverts par département, par technicien, par priorité

- Consulter les SLA en cours et les tickets en retard

#### Inventaire

- Consulter la fiche d'un équipement (PC, imprimante, serveur)

- Associer un ticket à un actif inventorié

- Vérifier le statut d'une licence logicielle
#### Rapports

- Résumé quotidien / hebdomadaire des tickets

- Charge par technicien

- Taux de résolution et délais moyens

### 4.3 Exemples de prompts utilisateur

```

"Quels tickets sont ouverts depuis plus de 5 jours ?"

"Assigne le ticket #4821 à Marie Dupont."

"Crée un ticket urgent pour la panne du serveur de fichiers."

"Montre-moi la charge de ticket de chaque technicien cette semaine."

"Clôture tous les tickets résolus depuis hier."

```

### 4.4 Droits API GLPI

```json

{

"profil": "Super Admin",

"droits": ["ticket.create", "ticket.update", "ticket.delete",

"ticket.read", "computer.read", "user.read",

"stat.read", "knowbase.read", "knowbase.write"]

}

```

  

---

  

## 5. Agent 2 – Départements

  

### 5.1 Utilisateurs cibles

  

| Département | Exemples de profils |

|---|---|

| **Finance & Comptabilité** | Comptables, responsables budgétaires |

| **Ressources Humaines** | Gestionnaires RH, chargés de recrutement |

| **Juridique / Marchés publics** | Juristes, acheteurs publics |

| **Direction générale** | Assistantes de direction, directeurs |

| **Services techniques** | Gestionnaires de patrimoine, techniciens voirie |

| **Action sociale** | Travailleurs sociaux, référents insertion |

| **Éducation / Collèges** | Personnels administratifs des collèges |

  

### 5.2 Logique de réponse (priorité)

  

```

1. L'utilisateur pose une question

↓

2. L'agent cherche dans la base documentaire (RAG)

↓

3a. Réponse trouvée → Réponse guidée étape par étape

↓

3b. Pas de réponse → Proposition d'ouvrir un ticket GLPI

↓

4. Si urgence déclarée → "Appelez le Help Desk : 📞 03 XX XX XX XX"

```

  

### 5.3 Capacités

  

- **Réponses documentaires** : procédures pas-à-pas depuis la base de connaissances

- **Ouverture de ticket GLPI** : création simple (titre, description, catégorie)

- **Suivi de ticket** : consulter l'état d'un ticket ouvert par l'utilisateur

- **Escalade téléphonique** : afficher le numéro du Help Desk en cas d'urgence

  

### 5.4 Droits API GLPI

  

```json

{

"profil": "Utilisateur standard",

"droits": ["ticket.create", "ticket.read_own"]

}

```

  

### 5.5 Exemples de prompts utilisateur

  

```

"Comment je réinitialise mon mot de passe ?"

"Je n'arrive pas à me connecter au VPN depuis hier."

"Mon imprimante ne fonctionne plus, que faire ?"

"Comment accéder à ma messagerie depuis chez moi ?"

"Je veux déclarer un problème avec mon PC."

"C'est urgent, mon accès est bloqué depuis ce matin."

```

  

---

  

## 6. Base documentaire – Exemples

  

> Ces fiches constituent la base RAG de l'Agent 2. Chaque fiche est un document Markdown indexé.

  

---

  

### FICHE-001 — Réinitialisation de mot de passe ![1780073854802](image/#SpécificationProjet–AgentsIACD08/1780073854802.png)ows

  

**Catégorie** : Authentification

**Niveau** : Tous utilisateurs

**Dernière mise à jour** : Mai 2026

  

#### Symptôme

Vous ne pouvez plus vous connecter à votre session Windows avec votre mot de passe habituel.

  

#### Procédure – Réinitialisation via le portail self-service

  

1. Ouvrez un navigateur depuis un autre poste ou votre téléphone.

2. Rendez-vous sur : `https://selfservice.cd08.fr`

3. Cliquez sur **"Mot de passe oublié"**.

4. Saisissez votre identifiant (format : `prenom.nom`).

5. Choisissez la méthode de vérification : SMS ou email de récupération.

6. Entrez le code reçu.

7. Choisissez un nouveau mot de passe (12 caractères minimum, majuscule + chiffre + symbole).

8. Validez. Votre session sera débloquée dans les **2 minutes**.

  

#### Règles mot de passe CD08

- Longueur minimale : **12 caractères**

- Doit contenir : majuscule, minuscule, chiffre, symbole (`!@#$%`)

- Ne peut pas reprendre les **5 derniers** mots de passe

- Expiration tous les **90 jours**

  

#### Si le self-service ne fonctionne pas

Appelez le Help Desk : **📞 03 24 XX XX XX**

Ou ouvrez un ticket via l'agent.

  

---

  

### FICHE-002 — Connexion au VPN (Cisco AnyConnect)

  

**Catégorie** : Accès distant

**Niveau** : Tous utilisateurs

**Dernière mise à jour** : Mai 2026

  

#### Prérequis

- Le logiciel **Cisco AnyConnect** doit être installé sur votre poste ou ordinateur personnel.

- Vous devez disposer de vos identifiants Active Directory.

  

#### Procédure de connexion

  

1. Ouvrez **Cisco AnyConnect** (icône dans la barre des tâches ou menu Démarrer).

2. Dans le champ "Se connecter à", entrez : `vpn.cd08.fr`

3. Cliquez sur **Connecter**.

4. Entrez votre identifiant (format : `prenom.nom`) et votre mot de passe Windows.

5. Si une authentification double facteur est demandée, entrez le code reçu par SMS.

6. Cliquez sur **OK**. La connexion s'établit en 15–30 secondes.

  

#### Erreurs fréquentes

  

| Message d'erreur | Cause probable | Solution |

|---|---|---|

| `Credentials rejected` | Mauvais mot de passe | Réinitialisez votre mot de passe (voir Fiche-001) |

| `Cannot connect to server` | VPN non accessible | Vérifiez votre connexion internet |

| `Certificate error` | Certificat expiré | Contactez le Help Desk |

| `License expired` | Licence AnyConnect | Contactez le Help Desk |

  

#### Déconnexion

Cliquez sur l'icône AnyConnect → **Déconnecter** avant d'éteindre votre ordinateur.

  

---

  

### FICHE-003 — Accès à la messagerie Outlook depuis l'extérieur

  

**Catégorie** : Messagerie

**Niveau** : Tous utilisateurs

**Dernière mise à jour** : Mai 2026

  

#### Option 1 — Via Outlook Web App (sans VPN)

  

1. Ouvrez votre navigateur (Chrome, Firefox, Edge).

2. Rendez-vous sur : `https://mail.cd08.fr`

3. Entrez votre adresse email complète : `prenom.nom@cd08.fr`

4. Entrez votre mot de passe Windows.

5. Vous accédez à votre messagerie dans le navigateur.

  

#### Option 2 — Via l'application Outlook (avec VPN)

  

1. Connectez-vous au VPN (voir Fiche-002).

2. Ouvrez l'application **Outlook** sur votre poste.

3. La synchronisation démarre automatiquement.

  

#### Paramètres de configuration manuelle (si nécessaire)

  

```

Serveur entrant (IMAP) : mail.cd08.fr Port : 993 SSL : Oui

Serveur sortant (SMTP) : smtp.cd08.fr Port : 587 TLS : Oui

```

  

---

  

### FICHE-004 — Problème d'impression réseau

  

**Catégorie** : Périphériques

**Niveau** : Tous utilisateurs

**Dernière mise à jour** : Mai 2026

  

#### Diagnostic rapide

  

Avant d'appeler le Help Desk, vérifiez les points suivants :

  

- [ ] L'imprimante est allumée (voyant vert).

- [ ] Le câble réseau est branché (ou Wi-Fi actif).

- [ ] Il y a du papier dans le bac.

- [ ] Aucun bourrage papier n'est signalé sur l'écran de l'imprimante.

- [ ] Votre PC est bien connecté au réseau (VPN si télétravail).

  

#### Procédure – Réinstaller une imprimante réseau

  

1. Allez dans **Paramètres → Imprimantes et scanners**.

2. Cliquez sur **Ajouter une imprimante ou un scanner**.

3. Si l'imprimante n'apparaît pas automatiquement, cliquez sur **"L'imprimante que je veux n'est pas répertoriée"**.

4. Sélectionnez **"Sélectionner une imprimante partagée par nom"**.

5. Entrez le chemin réseau : `\\print.cd08.fr\NOM_IMPRIMANTE`

*(Le nom de votre imprimante est affiché sur une étiquette sur l'appareil)*

6. Cliquez sur **Suivant** et laissez Windows installer le pilote.

  

#### Si l'impression reste bloquée en file d'attente

  

1. Ouvrez **Services** (Win + R → `services.msc`).

2. Trouvez **Print Spooler**, faites un clic droit → **Redémarrer**.

3. Relancez votre impression.

  

---

  

### FICHE-005 — Demande de création de compte utilisateur

  

**Catégorie** : Administration

**Niveau** : Responsables / RH

**Dernière mise à jour** : Mai 2026

  

> ⚠️ Cette procédure est réservée aux responsables de service et aux gestionnaires RH.

  

#### Quand l'utiliser ?

- Arrivée d'un nouvel agent ou stagiaire

- Changement de poste nécessitant de nouveaux accès

- Prestataire externe ayant besoin d'un accès temporaire

  

#### Procédure

  

1. Ouvrez un ticket GLPI via l'agent ou le portail : `https://glpi.cd08.fr`

2. Catégorie : **Demande → Gestion des comptes → Création**

3. Renseignez les informations obligatoires :

- Nom, prénom de l'agent

- Date d'arrivée prévue

- Département et service

- Responsable hiérarchique

- Applications nécessaires (Outlook, SEDIT, e-Bourgogne…)

- Durée si accès temporaire

4. Joignez si possible la **fiche de poste** ou le **contrat**.

5. Le Help Desk traitera la demande sous **48h ouvrées**.

  

#### Accès standards créés automatiquement

- Compte Active Directory (session Windows)

- Messagerie Outlook (`prenom.nom@cd08.fr`)

- Accès intranet CD08

- Accès VPN (sur demande explicite)

  

---

  

### FICHE-006 — Accès à SEDIT (logiciel finances)

  

**Catégorie** : Applications métier

**Niveau** : Département Finance

**Dernière mise à jour** : Mai 2026

  

#### Qu'est-ce que SEDIT ?

SEDIT est le logiciel de gestion financière et comptable utilisé par le département Finance du CD08 (engagement, mandatement, suivi budgétaire).

  

#### Connexion

  

1. Connectez-vous au VPN (voir Fiche-002).

2. Ouvrez votre navigateur et accédez à : `https://sedit.cd08.fr`

3. Utilisez vos identifiants SEDIT (différents de votre mot de passe Windows).

*(Fournis lors de votre arrivée par le responsable du service Finance)*

  

#### Mot de passe SEDIT oublié

  

Le mot de passe SEDIT est géré indépendamment. En cas d'oubli :

- Contactez votre **référent SEDIT** au sein du service Finance.

- Ou ouvrez un ticket GLPI (catégorie : **Applications métier → SEDIT → Mot de passe**).

  

#### Problèmes fréquents

  

| Problème | Solution |

|---|---|

| Page blanche au chargement | Vider le cache navigateur (Ctrl+Shift+Del) |

| Session expirée | Reconnectez-vous, la session expire après 30 min d'inactivité |

| Erreur de droits | Contactez le Help Desk (accès non configuré) |

  

---

  

### FICHE-007 — Signaler un incident de sécurité

  

**Catégorie** : Sécurité

**Niveau** : Tous utilisateurs

**Dernière mise à jour** : Mai 2026

  

> 🔴 **En cas de doute, signalez toujours. Il vaut mieux un faux positif qu'un incident non déclaré.**

  

#### Exemples d'incidents à signaler

  

- Email suspect contenant une pièce jointe ou un lien inattendu (phishing)

- Votre compte a été utilisé sans votre autorisation

- Votre poste affiche des messages inhabituels ou est anormalement lent

- Vous avez cliqué sur un lien suspect

- Perte ou vol d'un équipement professionnel (PC, téléphone, clé USB)

  

#### Procédure d'urgence (incident actif)

  

**📞 Appelez immédiatement le Help Desk : 03 24 XX XX XX**

Ne pas attendre. Ne pas éteindre le poste. Ne pas déconnecter le câble réseau.

  

#### Procédure standard (incident non urgent)

  

1. Ouvrez un ticket via l'agent ou le portail GLPI.

2. Catégorie : **Incident → Sécurité**

3. Décrivez ce que vous avez observé (heure, action effectuée, message affiché).

4. Si vous avez reçu un email suspect, **transférez-le** en pièce jointe au ticket.

5. Le Help Desk répondra en priorité (SLA : **2h** pour les incidents sécurité).

  

---

  

## 7. Interface chat web

  

### 7.1 Deux interfaces distinctes

  

| | Agent 1 – Help Desk IT | Agent 2 – Départements |

|---|---|---|

| **URL** | `https://agent-it.cd08.fr` | `https://agent.cd08.fr` |

| **Auth** | SSO Active Directory (groupe IT) | SSO Active Directory (tous agents) |

| **Couleur** | Violet / tons DSI | Bleu / charte CD08 |

| **Langue** | Français | Français |

  

### 7.2 Fonctionnalités communes

  

- Authentification SSO via Active Directory

- Historique de conversation (session uniquement)

- Bouton "Ouvrir un ticket" contextuel

- Affichage du numéro d'urgence si détection de mots-clés critiques

- Interface responsive (desktop + mobile)

  

### 7.3 Comportement en cas d'urgence (Agent 2)

  

Si l'utilisateur utilise des mots-clés comme *"urgent"*, *"bloqué"*, *"ne fonctionne plus depuis ce matin"*, l'agent affiche systématiquement :

  

```

⚠️ Situation urgente détectée.

Pour une assistance immédiate, contactez le Help Desk par téléphone :

📞 03 24 XX XX XX (lundi–vendredi, 8h–18h)

  

Je peux également ouvrir un ticket prioritaire pour vous.

Voulez-vous que je le fasse maintenant ?

```

  

---

  

## 8. Sécurité et contrôle d'accès

  

### 8.1 Authentification

  

- Authentification unique via **Active Directory** (SSO)

- Groupes AD utilisés pour le contrôle d'accès :

- `GRP_DSI_HELPDESK` → accès Agent 1

- `GRP_AGENTS_CD08` → accès Agent 2

  

### 8.2 Cloisonnement des agents

  

- Les deux agents fonctionnent sur des tokens GLPI distincts.

- L'Agent 2 ne peut ni modifier ni supprimer de ticket.

- Les conversations ne sont pas partagées entre les deux agents.

- Aucune donnée personnelle n'est stockée au-delà de la session.

  

### 8.3 Journalisation

  

- Toutes les interactions avec l'API GLPI sont journalisées.

- Les logs de conversation sont conservés 30 jours (conformité RGPD).

- Un tableau de bord de supervision est accessible au responsable DSI.

  

---

  

## 9. Roadmap de déploiement

  

```

Phase 1 – Semaines 1–2 : Configuration API GLPI + tokens

Phase 2 – Semaines 3–4 : Construction base documentaire (fiches 001–020)

Phase 3 – Semaines 5–6 : Développement Agent 1 (Help Desk IT)

Phase 4 – Semaines 7–8 : Développement Agent 2 + RAG documentaire

Phase 5 – Semaine 9 : Tests internes DSI

Phase 6 – Semaine 10 : Pilote 1 département (Finance)

Phase 7 – Semaines 11–12 : Déploiement général + formation utilisateurs

```

  

### Critères de succès

  

- Réduction de **30%** des tickets de niveau 1 (mots de passe, VPN, impression)

- Taux de satisfaction utilisateur **≥ 80%** après 1 mois

- Temps de réponse moyen de l'agent **< 5 secondes**

- Zéro incident de sécurité lié aux agents IA

  

---

  

*Document rédigé pour le projet agents IA CD08 — Conseil Départemental des Ardennes*

*Version 1.0 — Mai 2026*