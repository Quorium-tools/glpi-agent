import { cookies } from "next/headers";
import Link from "next/link";
import Typewriter from "./Typewriter";

type GlpiUserCookie = {
  name?: string;
  username?: string;
  email?: string;
};

export default async function Home() {
  const cookieStore = await cookies();
  const accessToken = cookieStore.get("glpi_access_token")?.value;
  const userCookieRaw = cookieStore.get("glpi_user_info")?.value;
  const scope = cookieStore.get("glpi_oauth_scope")?.value;

  let userInfo: GlpiUserCookie | null = null;
  if (userCookieRaw) {
    try {
      userInfo = JSON.parse(userCookieRaw) as GlpiUserCookie;
    } catch {
      userInfo = null;
    }
  }

  const displayName =
    userInfo?.name?.trim() || userInfo?.username?.trim() || userInfo?.email?.trim() || "Compte GLPI";

  return (
    <main className="home-shell">
      <div className="home-auth-corner">
        {!accessToken ? (
          <a className="home-auth-login" href="/api/auth/glpi/start">
            Se connecter
          </a>
        ) : (
          <div className="home-auth-user">
            <strong>{displayName}</strong>
            {userInfo?.email ? <span>{userInfo.email}</span> : null}
            {scope ? <span>Scope: {scope}</span> : null}
            <form action="/api/auth/glpi/logout" method="post">
              <button type="submit">Se déconnecter</button>
            </form>
          </div>
        )}
      </div>

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
          <Link href="/help-desk-agent" className="cta-primary">
            Ouvrir l'agent Help Desk
          </Link>
          <Link href="/departments-support-agent" className="cta-secondary">
            Ouvrir l'agent Départements
          </Link>
        </div>

        {/* Stats strip */}
        <div className="stats-strip">
          <div className="stat-item">
            <strong>2</strong>
            <span>Agents spécialisés</span>
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
        <h2 className="features-heading">Deux agents, un seul espace</h2>
        <div className="agent-explain-grid">

          <div className="agent-explain-card">
            <div className="agent-explain-icon help-bg">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
              </svg>
            </div>
            <h3>Help Desk Agent</h3>
            <p className="agent-explain-desc">Votre copilote de support en première ligne. Posez vos questions sur les tickets ouverts, l'historique utilisateur ou les priorités, et obtenez des réponses claires en quelques secondes.</p>
            <ul className="agent-explain-list">
              <li>
                <span className="agent-explain-bullet help-bullet">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
                </span>
                Rechercher et résumer l'historique des tickets en quelques secondes
              </li>
              <li>
                <span className="agent-explain-bullet help-bullet">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
                </span>
                Rédiger des réponses claires et actionnables pour les utilisateurs
              </li>
              <li>
                <span className="agent-explain-bullet help-bullet">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
                </span>
                Suivre les priorités et changements de statut au même endroit
              </li>
            </ul>
          </div>

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
