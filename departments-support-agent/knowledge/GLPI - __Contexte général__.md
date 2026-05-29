**Contexte général**

Le Conseil Départemental des Ardennes (CD08) utilise **GLPI** comme plateforme centrale de gestion des tickets et des tâches pour tous ses départements. L'objectif est de créer deux agents IA distincts avec des niveaux d'accès et des usages différents.

---

**Agent 1 — Help Desk IT**

Réservé exclusivement aux techniciens et super admins de la DSI. Il a un accès **complet** à l'API GLPI : création, modification, assignation, clôture et escalade de tickets, consultation de l'inventaire matériel, suivi des SLAs, et génération de rapports. C'est l'agent "puissant" — il manipule GLPI comme un technicien humain le ferait.

---

**Agent 2 — Départements (Finance, RH, Juridique, etc.)**

Destiné à tous les agents CD08 hors IT. Son fonctionnement est à deux niveaux :

- **En priorité** : il répond aux questions courantes en s'appuyant sur une base documentaire (comment réinitialiser un mot de passe, comment accéder au VPN, procédures de connexion…). L'utilisateur obtient sa réponse sans créer de ticket.
- **Si nécessaire** : il peut ouvrir un ticket GLPI en lecture/écriture basique (signalement d'incident), mais sans accès admin.
- **En urgence** : l'agent invite l'utilisateur à **appeler le Help Desk par téléphone** — c'est le fallback humain garanti pour les situations critiques.