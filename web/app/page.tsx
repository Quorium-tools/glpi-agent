import Link from "next/link";
import Typewriter from "./Typewriter";

export default function Home() {
  return (
    <main className="home-shell">
      {/* ── Hero ── */}
      <section className="landing-hero" aria-label="Introduction">
        <p className="eyebrow">Espace IA GLPI</p>
        <h1 className="landing-h1">
          Support assisté par IA,<br />
          <Typewriter />
        </h1>
        <p className="landing-lead">
          Arrêtez de naviguer entre les onglets et de fouiller les files de tickets.
          Deux agents IA spécialisés gèrent tout, des recherches rapides
          de tickets aux workflows inter-départements, pour que votre équipe
          reste concentrée sur l'essentiel.
        </p>
        <div className="hero-ctas">
          <Link href="/departments-support-agent" className="cta-primary">
            Ouvrir l'agent Départements
          </Link>
        </div>

        <div className="stats-strip">
          <div className="stat-item">
            <strong>1</strong>
            <span>Agent disponible</span>
          </div>
          <div className="stat-divider" aria-hidden />
          <div className="stat-item">
            <strong>GLPI</strong>
            <span>Intégration native</span>
          </div>
          <div className="stat-divider" aria-hidden />
          <div className="stat-item">
            <strong>Temps réel</strong>
            <span>Opérations ticket</span>
          </div>
        </div>
      </section>

      {/* ── Agent overview ── */}
      <section className="agent-overview" id="agents" aria-label="Agents disponibles">
        <p className="eyebrow" style={{ textAlign: "center" }}>Découvrez les agents</p>
        <h2 className="features-heading">Un agent, un seul espace</h2>
        <div className="agent-explain-grid">
          <div className="agent-explain-card">
            <div className="agent-explain-icon dept-bg">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <rect x="2" y="7" width="20" height="14" rx="2"/>
                <path d="M16 7V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v2"/>
                <line x1="12" y1="12" x2="12" y2="16"/>
                <line x1="10" y1="14" x2="14" y2="14"/>
              </svg>
            </div>
            <h3>Agent Support Départements</h3>
            <p className="agent-explain-desc">Gère les demandes internes structurées entre équipes. Chaque soumission est complète, correctement routée et prête à traiter, sans allers-retours inutiles.</p>
            <ul className="agent-explain-list">
              <li>
                <span className="agent-explain-bullet dept-bullet">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
                </span>
                Créer des demandes complètes avec tous les champs requis
              </li>
              <li>
                <span className="agent-explain-bullet dept-bullet">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
                </span>
                Coordonner les workflows entre plusieurs équipes internes
              </li>
              <li>
                <span className="agent-explain-bullet dept-bullet">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
                </span>
                Améliorer la qualité des transferts et des informations de suivi
              </li>
            </ul>
          </div>
        </div>
      </section>
    </main>
  );
}
