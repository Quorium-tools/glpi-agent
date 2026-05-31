# ARDIA — From-Scratch Implementation Plan

> Place this file inside: `user-flow/ARDIA_FROM_SCRATCH_IMPLEMENTATION_PLAN.md`  
> Repository: `glpi-agent`  
> Current state: the previous `web/` folder was removed. We are starting the frontend from zero.  
> Source of truth: everything inside `user-flow/` must be read and followed before implementation.  
> Goal: build a full demo-ready ARDIA IT Support Agent with a strong “wow effect”.

---

## 1. Current Context

The repository currently contains the `user-flow/` folder with all functional and visual references.

Expected files inside `user-flow/`:

```txt
user-flow/
├── Agent_IA_Support_IT_Parcours_Utilisateur_Detaille.pdf
├── agent-logo.png
├── ARDIA_BEST_ARCHITECTURE_AND_DEMO_PLAN.md
├── instruction.txt
├── WhatsApp Image 2026-05-30 at 14.40.12.jpeg
├── WhatsApp Image 2026-05-30 at 15.11.55.jpeg
└── .dockerignore
```

Important:

```txt
The web app no longer exists.
Create a brand-new `web/` folder from scratch.
Do not assume old frontend code exists.
```

---

## 2. Product Vision

ARDIA is not a simple GLPI chatbot.

ARDIA is an **Intelligent IT Support Copilot** that:

```txt
- welcomes the user with the ARDIA robot branding
- understands natural language IT problems
- asks clarification questions one by one
- searches procedures and known incidents
- proposes safe level-1 fixes
- creates a complete GLPI ticket only if the issue is not solved
- asks explicit confirmation before ticket creation
- lets the user follow tickets
- lets the user add comments and attachments
- gives the helpdesk a rich ticket with context, urgency, impact, and actions already tried
```

The demo must visually follow the screenshots in `user-flow/`:

```txt
- blue / white / clean enterprise style
- ARDIA robot identity
- chat-window cards
- numbered journey steps
- status badges
- confirmation buttons
- satisfaction rating
- ticket timeline
- helpdesk routing / GLPI ticket creation visual
```

---

## 3. Final Architecture

No Redis. No caching layer. Fast delivery.

```txt
New Next.js web app
  ↓
FastAPI agent-api
  ↓
LangGraph agent workflow
  ↓
OpenRouter model
  ↓
MongoDB + Neo4j + GLPI API
```

Final Docker services:

```txt
arida-web
arida-agent-api
arida-mongodb
arida-neo4j
```

External Docker network:

```txt
gen-ai-network
```

Caddy:

```txt
Already exists in a separate repo.
Do not add Caddy to this repo.
Caddy should reverse proxy to arida-web:3000.
```

---

## 4. Main Technology Choices

### Frontend

```txt
Next.js
TypeScript
Tailwind CSS
Shadcn UI
Lucide React icons
Framer Motion
React Flow
```

Use Next.js from scratch with a clean app router structure.

### Backend

```txt
FastAPI
LangGraph
OpenRouter direct API client
Pydantic
httpx
Motor / PyMongo
Neo4j Python driver
neo4j-graphrag
python-multipart
```

### Data

```txt
MongoDB:
- conversations
- agent states
- ticket drafts
- audit logs
- feedback
- demo events

Neo4j:
- procedures
- symptoms
- causes
- applications
- known incidents
- GLPI categories
- support groups
```

### GLPI

```txt
Use existing GLPI v2.3 OAuth configuration from .env.
All GLPI credentials stay server-side in agent-api.
Never expose GLPI tokens to web.
```

---

## 5. Repository Structure To Create

```txt
glpi-agent/
├── user-flow/
│   ├── Agent_IA_Support_IT_Parcours_Utilisateur_Detaille.pdf
│   ├── agent-logo.png
│   ├── ARDIA_BEST_ARCHITECTURE_AND_DEMO_PLAN.md
│   ├── instruction.txt
│   ├── WhatsApp Image 2026-05-30 at 14.40.12.jpeg
│   ├── WhatsApp Image 2026-05-30 at 15.11.55.jpeg
│   └── .dockerignore
│
├── web/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   ├── globals.css
│   │   ├── dashboard/
│   │   │   └── page.tsx
│   │   ├── helpdesk/
│   │   │   └── page.tsx
│   │   └── tickets/
│   │       └── page.tsx
│   │
│   ├── components/
│   │   ├── ardia/
│   │   │   ├── ArdiaShell.tsx
│   │   │   ├── ArdiaWelcome.tsx
│   │   │   ├── ArdiaChat.tsx
│   │   │   ├── ChatMessage.tsx
│   │   │   ├── QuickActions.tsx
│   │   │   ├── TicketPreviewCard.tsx
│   │   │   ├── ReasoningTimeline.tsx
│   │   │   ├── GraphRagVisualizer.tsx
│   │   │   ├── UserTicketTimeline.tsx
│   │   │   ├── HelpdeskCockpit.tsx
│   │   │   ├── SatisfactionRating.tsx
│   │   │   └── DemoMetrics.tsx
│   │   │
│   │   ├── layout/
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── PageContainer.tsx
│   │   │
│   │   └── ui/
│   │       └── shadcn components
│   │
│   ├── lib/
│   │   ├── api.ts
│   │   ├── types.ts
│   │   ├── demo-data.ts
│   │   └── utils.ts
│   │
│   ├── public/
│   │   └── assets/
│   │       ├── agent-logo.png
│   │       ├── flow-support-it.jpeg
│   │       └── flow-ardia.jpeg
│   │
│   ├── package.json
│   ├── next.config.ts
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   ├── postcss.config.mjs
│   ├── components.json
│   └── Dockerfile
│
├── agent-api/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── api/
│   │   │   ├── chat.py
│   │   │   ├── tickets.py
│   │   │   ├── attachments.py
│   │   │   ├── demo.py
│   │   │   └── health.py
│   │   ├── agent/
│   │   │   ├── graph.py
│   │   │   ├── state.py
│   │   │   ├── prompts.py
│   │   │   ├── schemas.py
│   │   │   └── nodes/
│   │   │       ├── load_user_context.py
│   │   │       ├── detect_intent.py
│   │   │       ├── qualify_problem.py
│   │   │       ├── retrieve_graph_knowledge.py
│   │   │       ├── diagnose.py
│   │   │       ├── propose_solution.py
│   │   │       ├── validate_resolution.py
│   │   │       ├── prepare_ticket_draft.py
│   │   │       ├── confirmation_gate.py
│   │   │       ├── create_glpi_ticket.py
│   │   │       ├── follow_ticket.py
│   │   │       └── ask_satisfaction.py
│   │   ├── clients/
│   │   │   ├── openrouter_client.py
│   │   │   ├── glpi_client.py
│   │   │   ├── mongodb_client.py
│   │   │   └── neo4j_client.py
│   │   ├── services/
│   │   │   ├── memory_service.py
│   │   │   ├── graphrag_service.py
│   │   │   ├── ticket_service.py
│   │   │   ├── audit_service.py
│   │   │   └── demo_service.py
│   │   └── seed/
│   │       ├── procedures.json
│   │       ├── incidents.json
│   │       ├── applications.json
│   │       └── neo4j_seed.cypher
│   ├── pyproject.toml
│   ├── uv.lock
│   └── Dockerfile
│
├── docker-compose-dev.yml
├── docker-compose-prod.yml
├── docker-compose-test.yml
├── docker.sh
├── .env
├── .env.example
└── README.md
```

---

## 6. Frontend UX Requirements

The frontend must be built from zero and must follow the uploaded images.

### 6.1 Main Page

Route:

```txt
/
```

Purpose:

```txt
Main ARDIA assistant experience.
```

Layout:

```txt
- Top header with ARDIA name and Département des Ardennes branding
- Left visual area with robot / welcome panel
- Main chat interface
- Right side panel with reasoning timeline and ticket preview
```

Hero text:

```txt
Bonjour, je suis ARDIA !
Votre assistant numérique du Département des Ardennes.
Décrivez simplement votre problème et je vous guiderai pas à pas.
```

Quick actions:

```txt
J’ai un problème informatique
Consulter mes tickets
Demander un accès
Rechercher une procédure
Contacter le support
```

### 6.2 Chat UI

Must support:

```txt
- assistant and user messages
- typing indicator
- streaming text if backend supports it
- quick-reply buttons
- ticket confirmation buttons
- attachment upload button
- status badges
```

Message style:

```txt
User bubble: blue
Agent bubble: light neutral / white
Success bubble: pale green
Warning / unresolved: pale orange or red
```

### 6.3 Journey Steps

Use a horizontal or vertical stepper inspired by the screenshots:

```txt
1. Accueil
2. Description du problème
3. Questions de clarification
4. Diagnostic
5. Résolution immédiate
6. Création automatique du ticket
7. Ticket créé avec succès
8. Suivi du ticket
9. Résolution par le support
10. Clôture & satisfaction
```

### 6.4 Reasoning Timeline

Component:

```txt
components/ardia/ReasoningTimeline.tsx
```

Show internal progress in user-safe terms:

```txt
✓ Intention détectée
✓ Utilisateur identifié
✓ Catégorie probable
✓ Recherche dans les procédures
✓ Incidents similaires trouvés
✓ Solution N1 proposée
✓ Ticket préparé
✓ Confirmation utilisateur
✓ Ticket transmis au Helpdesk
```

Do not expose hidden chain-of-thought.

Show only short operational steps.

### 6.5 Ticket Preview Card

Component:

```txt
components/ardia/TicketPreviewCard.tsx
```

Fields:

```txt
Titre
Catégorie
Impact
Urgence
Priorité
Description
Actions déjà réalisées
Contexte utilisateur
Groupe proposé
Pièces jointes
```

Buttons:

```txt
Modifier
Annuler
Créer le ticket
```

Critical rule:

```txt
The UI must never call ticket creation directly without the confirmation button.
```

### 6.6 GraphRAG Visualizer

Component:

```txt
components/ardia/GraphRagVisualizer.tsx
```

Use React Flow.

Display simplified graph:

```txt
Utilisateur
→ Direction
→ Application
→ Symptôme
→ Cause probable
→ Procédure
→ Catégorie GLPI
→ Groupe Support
```

Demo example:

```txt
Marie Dupont
→ Direction Finance
→ Grand Angle
→ Accès impossible
→ VPN / SSO
→ Procédure N1
→ Application métier > Grand Angle
→ Support Applicatif Finance
```

### 6.7 Helpdesk Cockpit

Route:

```txt
/helpdesk
```

Purpose:

```txt
Show the audience what the helpdesk receives.
```

Cards:

```txt
New enriched ticket
Priority
Suggested group
Similar incidents
Actions already tried
Confidence score
Business context
```

### 6.8 Ticket Tracking Page

Route:

```txt
/tickets
```

Features:

```txt
- list user tickets
- filter by status
- open ticket detail
- add comment
- attach file
- relance support
- close ticket if resolved
```

---

## 7. Visual Style Guide

Follow the images in `user-flow/`.

### Colors

```txt
Primary dark navy: #071A3D
Primary blue: #1E63FF
Light blue background: #EEF5FF
Success green: #16A34A
Soft green: #EAF8EF
Warning orange: #F97316
Soft orange: #FFF4E8
Danger red: #DC2626
Neutral text: #0F172A
Muted text: #64748B
Border: #E2E8F0
White: #FFFFFF
```

### Typography

```txt
Use clean enterprise typography.
Headlines: bold, large, clear.
Body: readable, not too small.
Buttons: strong labels, no ambiguity.
```

### UI Style

```txt
- rounded-2xl cards
- subtle shadows
- thin borders
- spacious layout
- clear icons
- animated transitions
- professional, public-sector friendly
```

### Icons

Use Lucide React:

```txt
Bot
User
Ticket
MessageSquare
ShieldCheck
Clock
CheckCircle
AlertTriangle
Paperclip
Send
Search
Database
Network
Activity
Headphones
```

---

## 8. Demo Scenario To Implement

This must be preloaded as a polished demo flow.

### User Persona

```txt
Name: Marie Dupont
Email: marie.dupont@ardennes.fr
Department: Direction Finance
Location: Télétravail
Application: Grand Angle
```

### Demo User Message

```txt
Bonjour ARDIA, je n’arrive plus à accéder à Grand Angle et j’ai une clôture budgétaire aujourd’hui.
```

### Expected Agent Flow

```txt
1. Detect intent: incident
2. Detect category: application métier
3. Detect application: Grand Angle
4. Detect business urgency: clôture budgétaire aujourd’hui
5. Ask one question: "Êtes-vous au bureau ou en télétravail ?"
6. User answers: "En télétravail"
7. Retrieve graph knowledge: VPN / SSO / Grand Angle
8. Show reasoning timeline
9. Show graph visualizer
10. Propose safe N1 solution
11. Ask if resolved
12. User says no
13. Prepare ticket draft
14. Show ticket preview
15. Ask confirmation
16. Create fake or real GLPI ticket depending on DEMO_MODE
17. Show ticket number
18. Show helpdesk cockpit update
19. Allow ticket follow-up
20. Ask satisfaction
```

### Expected Ticket Draft

```json
{
  "title": "Accès impossible à Grand Angle en télétravail",
  "category": "Application métier > Grand Angle",
  "impact": "Utilisateur bloqué",
  "urgency": "Élevée",
  "priority": "Élevée",
  "description": "L'utilisatrice ne parvient plus à accéder à Grand Angle en télétravail alors qu'une clôture budgétaire est prévue aujourd'hui.",
  "actions_tried": [
    "Vérification du contexte télétravail",
    "Reconnexion VPN proposée",
    "Relance de l'application proposée",
    "Vérification SSO suggérée"
  ],
  "support_group": "Support Applicatif Finance",
  "business_context": "Clôture budgétaire aujourd'hui",
  "user": {
    "name": "Marie Dupont",
    "email": "marie.dupont@ardennes.fr",
    "department": "Direction Finance",
    "location": "Télétravail"
  }
}
```

---

## 9. Backend Agent Requirements

### 9.1 LangGraph First

Use LangGraph as the workflow brain.

Do not build a loose one-prompt chatbot.

The workflow must be stateful:

```txt
load_user_context
detect_intent
qualify_problem
retrieve_graph_knowledge
diagnose
propose_solution
validate_resolution
prepare_ticket_draft
confirmation_gate
create_glpi_ticket
follow_ticket
ask_satisfaction
```

### 9.2 Use OpenRouter

Use the existing env:

```env
OPENROUTER_API_KEY=
OPENROUTER_MODEL=anthropic/claude-opus-4.7
```

The backend should call OpenRouter directly with `httpx`.

Structured outputs must be validated with Pydantic.

### 9.3 MongoDB

Store:

```txt
conversations
agent_states
ticket_drafts
audit_logs
feedback
demo_events
```

### 9.4 Neo4j GraphRAG

Create demo graph data from seed files.

Seed concepts:

```txt
Problem: Accès impossible application métier
Application: Grand Angle
Symptom: Authentification refusée
Cause: Session VPN ou SSO expirée
Procedure: Réinitialiser session VPN/SSO
GLPI Category: Application métier > Grand Angle
Support Group: Support Applicatif Finance
Known Incident: Problème VPN intermittent en télétravail
```

Relationships:

```txt
(:User)-[:BELONGS_TO]->(:Department)
(:Department)-[:USES_APPLICATION]->(:Application)
(:Application)-[:CAN_HAVE_PROBLEM]->(:Problem)
(:Problem)-[:HAS_SYMPTOM]->(:Symptom)
(:Symptom)-[:MAY_BE_CAUSED_BY]->(:Cause)
(:Cause)-[:RESOLVED_BY]->(:Procedure)
(:Problem)-[:MAPS_TO]->(:GLPICategory)
(:GLPICategory)-[:ROUTED_TO]->(:SupportGroup)
```

### 9.5 GLPI

Use custom Python service.

Do not let the LLM directly create tickets.

Allowed server-side operations:

```txt
create_ticket
get_user_tickets
get_ticket_details
add_followup
upload_attachment
update_ticket
```

Critical:

```txt
No confirmation = no GLPI write.
```

---

## 10. Environment Variables

Keep current env:

```env
NODE_ENV=development

OPENROUTER_API_KEY=
OPENROUTER_MODEL=anthropic/claude-opus-4.7

GLPI_BASE_URL=
GLPI_API_VERSION=v2.3

GLPI_OAUTH_CLIENT_ID=
GLPI_OAUTH_CLIENT_SECRET=
GLPI_OAUTH_SCOPE=api

GLPI_OAUTH_AUTHORIZE_URL=
GLPI_OAUTH_TOKEN_URL=

GLPI_OAUTH_REDIRECT_URI=
GLPI_USERNAME=
GLPI_PASSWORD=

NEXT_PUBLIC_APP_URL=
```

Add:

```env
NEXT_PUBLIC_AGENT_API_URL=http://arida-agent-api:8000

MONGODB_URI=mongodb://arida-mongodb:27017
MONGODB_DB=arida_agent

NEO4J_URI=bolt://arida-neo4j:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=change_me

AGENT_API_HOST=0.0.0.0
AGENT_API_PORT=8000

DEMO_MODE=hybrid

JWT_SECRET=change_me
CORS_ORIGINS=http://localhost:3003,${NEXT_PUBLIC_APP_URL}
```

---

## 11. Docker Requirements

Rules:

```txt
No Redis.
No Caddy in this repo.
Use external Docker network: gen-ai-network.
Every service must have container_name.
Every container name must start with arida-.
Every volume name must start with the related container name.
```

Services:

```txt
web:
  container_name: arida-web

agent-api:
  container_name: arida-agent-api

mongodb:
  container_name: arida-mongodb

neo4j:
  container_name: arida-neo4j
```

Volumes:

```txt
arida-mongodb-data
arida-mongodb-config
arida-neo4j-data
arida-neo4j-logs
arida-neo4j-import
arida-neo4j-plugins
```

---

## 12. `docker-compose-dev.yml`

```yaml
services:
  web:
    build:
      context: ./web
      dockerfile: Dockerfile
      target: dev
    container_name: arida-web
    restart: unless-stopped
    env_file:
      - .env
    environment:
      NODE_ENV: development
      NEXT_PUBLIC_AGENT_API_URL: http://localhost:8003
      WATCHPACK_POLLING: "true"
    ports:
      - "3003:3000"
    volumes:
      - ./web:/app
      - arida-web-node-modules:/app/node_modules
      - arida-web-next:/app/.next
    depends_on:
      - agent-api
    networks:
      - gen-ai-network

  agent-api:
    build:
      context: ./agent-api
      dockerfile: Dockerfile
      target: dev
    container_name: arida-agent-api
    restart: unless-stopped
    env_file:
      - .env
    environment:
      MONGODB_URI: mongodb://arida-mongodb:27017
      MONGODB_DB: arida_agent
      NEO4J_URI: bolt://arida-neo4j:7687
      NEO4J_USERNAME: neo4j
      NEO4J_PASSWORD: ${NEO4J_PASSWORD}
      AGENT_API_HOST: 0.0.0.0
      AGENT_API_PORT: 8000
    ports:
      - "8003:8000"
    volumes:
      - ./agent-api:/app
    depends_on:
      - mongodb
      - neo4j
    networks:
      - gen-ai-network

  mongodb:
    image: mongo:7
    container_name: arida-mongodb
    restart: unless-stopped
    volumes:
      - arida-mongodb-data:/data/db
      - arida-mongodb-config:/data/configdb
    ports:
      - "27018:27017"
    networks:
      - gen-ai-network

  neo4j:
    image: neo4j:5
    container_name: arida-neo4j
    restart: unless-stopped
    environment:
      NEO4J_AUTH: neo4j/${NEO4J_PASSWORD}
      NEO4J_PLUGINS: '["apoc"]'
      NEO4J_dbms_security_procedures_unrestricted: apoc.*
      NEO4J_dbms_security_procedures_allowlist: apoc.*
    volumes:
      - arida-neo4j-data:/data
      - arida-neo4j-logs:/logs
      - arida-neo4j-import:/var/lib/neo4j/import
      - arida-neo4j-plugins:/plugins
    ports:
      - "7475:7474"
      - "7688:7687"
    networks:
      - gen-ai-network

volumes:
  arida-web-node-modules:
  arida-web-next:
  arida-mongodb-data:
  arida-mongodb-config:
  arida-neo4j-data:
  arida-neo4j-logs:
  arida-neo4j-import:
  arida-neo4j-plugins:

networks:
  gen-ai-network:
    external: true
```

---

## 13. `docker-compose-prod.yml`

```yaml
services:
  web:
    build:
      context: ./web
      dockerfile: Dockerfile
      target: runner
    container_name: arida-web
    restart: unless-stopped
    env_file:
      - .env
    environment:
      NODE_ENV: production
      NEXT_PUBLIC_AGENT_API_URL: http://arida-agent-api:8000
    depends_on:
      - agent-api
    networks:
      - gen-ai-network

  agent-api:
    build:
      context: ./agent-api
      dockerfile: Dockerfile
      target: runner
    container_name: arida-agent-api
    restart: unless-stopped
    env_file:
      - .env
    environment:
      MONGODB_URI: mongodb://arida-mongodb:27017
      MONGODB_DB: arida_agent
      NEO4J_URI: bolt://arida-neo4j:7687
      NEO4J_USERNAME: neo4j
      NEO4J_PASSWORD: ${NEO4J_PASSWORD}
      AGENT_API_HOST: 0.0.0.0
      AGENT_API_PORT: 8000
    depends_on:
      - mongodb
      - neo4j
    networks:
      - gen-ai-network

  mongodb:
    image: mongo:7
    container_name: arida-mongodb
    restart: unless-stopped
    volumes:
      - arida-mongodb-data:/data/db
      - arida-mongodb-config:/data/configdb
    networks:
      - gen-ai-network

  neo4j:
    image: neo4j:5
    container_name: arida-neo4j
    restart: unless-stopped
    environment:
      NEO4J_AUTH: neo4j/${NEO4J_PASSWORD}
      NEO4J_PLUGINS: '["apoc"]'
      NEO4J_dbms_security_procedures_unrestricted: apoc.*
      NEO4J_dbms_security_procedures_allowlist: apoc.*
    volumes:
      - arida-neo4j-data:/data
      - arida-neo4j-logs:/logs
      - arida-neo4j-import:/var/lib/neo4j/import
      - arida-neo4j-plugins:/plugins
    networks:
      - gen-ai-network

volumes:
  arida-mongodb-data:
  arida-mongodb-config:
  arida-neo4j-data:
  arida-neo4j-logs:
  arida-neo4j-import:
  arida-neo4j-plugins:

networks:
  gen-ai-network:
    external: true
```

---

## 14. New `web/Dockerfile`

```dockerfile
FROM node:22-alpine AS base
WORKDIR /app

FROM base AS deps
COPY package.json package-lock.json* ./
RUN npm ci || npm install

FROM base AS dev
ENV NODE_ENV=development
COPY --from=deps /app/node_modules ./node_modules
COPY . .
EXPOSE 3000
CMD ["npm", "run", "dev", "--", "--hostname", "0.0.0.0", "--port", "3000"]

FROM base AS builder
ENV NODE_ENV=production
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM base AS runner
ENV NODE_ENV=production
ENV PORT=3000
ENV HOSTNAME=0.0.0.0

COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3000
CMD ["node", "server.js"]
```

---

## 15. New `web/next.config.ts`

```ts
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  images: {
    unoptimized: true,
  },
};

export default nextConfig;
```

---

## 16. New `agent-api/Dockerfile`

```dockerfile
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv

FROM base AS deps
COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-dev || uv sync --no-dev

FROM base AS dev
COPY --from=deps /app/.venv ./.venv
COPY . .
ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

FROM base AS runner
COPY --from=deps /app/.venv ./.venv
COPY app ./app
ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 17. New `agent-api/pyproject.toml`

```toml
[project]
name = "arida-agent-api"
version = "0.1.0"
description = "ARDIA intelligent IT support agent API"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.30.0",
    "pydantic>=2.8.0",
    "pydantic-settings>=2.4.0",
    "httpx>=0.27.0",
    "motor>=3.5.0",
    "pymongo>=4.8.0",
    "neo4j>=5.23.0",
    "neo4j-graphrag>=1.0.0",
    "langgraph>=0.2.0",
    "python-multipart>=0.0.9",
    "orjson>=3.10.0"
]

[tool.uv]
dev-dependencies = [
    "pytest>=8.3.0",
    "ruff>=0.6.0"
]
```

---

## 18. API Contract

### Chat

```http
POST /api/chat
```

Request:

```json
{
  "conversation_id": "conv_demo_001",
  "user_id": "demo_user_001",
  "message": "Bonjour ARDIA, je n’arrive plus à accéder à Grand Angle et j’ai une clôture budgétaire aujourd’hui.",
  "channel": "web"
}
```

Response:

```json
{
  "conversation_id": "conv_demo_001",
  "message": "Je vais vous aider. Êtes-vous au bureau ou en télétravail ?",
  "ui_events": [
    {
      "type": "reasoning_step",
      "label": "Intention détectée: Incident applicatif",
      "status": "completed"
    }
  ],
  "ticket_draft": null
}
```

### Confirm Ticket

```http
POST /api/tickets/drafts/{draft_id}/confirm
```

### List Tickets

```http
GET /api/tickets
```

### Ticket Details

```http
GET /api/tickets/{ticket_id}
```

### Add Comment

```http
POST /api/tickets/{ticket_id}/comments
```

### Upload Attachment

```http
POST /api/tickets/{ticket_id}/attachments
```

### Health

```http
GET /health
```

---

## 19. Frontend Pages

### `/`

Main demo:

```txt
ARDIA chat
Journey steps
Reasoning timeline
Ticket preview
Graph visualizer
```

### `/dashboard`

Demo value dashboard:

```txt
tickets avoided
average time saved
tickets enriched
satisfaction score
```

### `/helpdesk`

Helpdesk cockpit:

```txt
new enriched ticket
priority
context
similar incidents
suggested group
```

### `/tickets`

User ticket tracking:

```txt
ticket list
ticket detail
comment
attachment
status
```

---

## 20. Demo Metrics

Use these demo values:

```txt
38% tickets avoided by level-1 resolution
65% qualification time saved
52% fewer helpdesk back-and-forth messages
100% tickets enriched with structured context
4.6/5 satisfaction
```

Show these on `/dashboard`.

---

## 21. User-Flow Compliance Checklist

The final app must respect:

```txt
- agent welcomes user clearly
- user can type freely
- user can select quick actions
- agent identifies intent
- agent asks one question at a time
- agent consults knowledge base
- agent proposes safe level-1 solution
- agent asks if problem is resolved
- if resolved, no ticket is created
- if not resolved, agent prepares a ticket
- agent asks confirmation before GLPI creation
- ticket contains title, category, impact, urgency, priority, description, actions tried, history
- user can consult tickets
- user can add comment
- user can attach file
- user can relance support
- user can close if resolved
- satisfaction is collected
- interaction is logged
```

---

## 22. Caddy Integration

Caddy is outside this repo.

Expected Caddy route:

```caddyfile
ardia.example.com {
    reverse_proxy arida-web:3000
}
```

Optional API route:

```caddyfile
ardia-api.example.com {
    reverse_proxy arida-agent-api:8000
}
```

Recommended:

```txt
Expose only arida-web.
Keep arida-agent-api internal.
```

---

## 23. Commands

Create network:

```bash
docker network create gen-ai-network
```

Start dev:

```bash
docker compose -f docker-compose-dev.yml up -d --build
```

Logs:

```bash
docker logs -f arida-web
docker logs -f arida-agent-api
docker logs -f arida-mongodb
docker logs -f arida-neo4j
```

Stop:

```bash
docker compose -f docker-compose-dev.yml down
```

Reset:

```bash
docker compose -f docker-compose-dev.yml down -v
```

---

## 24. Build Order

Because the web folder is gone, implement in this order:

```txt
1. Create new web Next.js app
2. Add Shadcn UI / Tailwind / Lucide / Framer Motion / React Flow
3. Copy visual assets from user-flow into web/public/assets
4. Create ARDIA static UI first
5. Create agent-api FastAPI service
6. Add Docker Compose services
7. Connect web to agent-api
8. Add OpenRouter client
9. Add MongoDB persistence
10. Add basic LangGraph flow
11. Add demo ticket draft
12. Add confirmation gate
13. Add fake GLPI creation
14. Add Neo4j seed data
15. Add GraphRAG retrieval
16. Add helpdesk cockpit
17. Add real GLPI integration last
```

---

## 25. Codex Instruction

When using Codex, give this instruction:

```txt
Read the entire user-flow folder first. The web folder was deleted, so create a new Next.js web app from scratch. Follow the visual design in the screenshots and the functional flow in the PDF. Implement a Dockerized stack with arida-web, arida-agent-api, arida-mongodb, and arida-neo4j on the external gen-ai-network. Do not use Redis. Do not add Caddy. Caddy exists in another repo. Every container and volume must be prefixed with arida-. Build the ARDIA demo as a polished IT support copilot with chat, reasoning timeline, GraphRAG visualizer, ticket preview, ticket confirmation, helpdesk cockpit, and ticket tracking.
```

---

## 26. Final Decision

```txt
Start over clean.
Create a new web app from zero.
Keep the architecture simple:
web + agent-api + MongoDB + Neo4j + GLPI + OpenRouter.
No Redis.
No Caddy in this repo.
Use the user-flow folder as the single product reference.
```
