import Link from "next/link";
import Typewriter from "./Typewriter";

export default function Home() {
  return (
    <main className="home-shell">

      {/* ── Hero ── */}
      <section className="landing-hero" aria-label="Introduction">
        <p className="eyebrow">GLPI AI Workspace</p>
        <h1 className="landing-h1">
          AI-powered support,<br />
          <Typewriter />
        </h1>
        <p className="landing-lead">
          Stop switching between tabs and hunting through ticket queues.
          Two specialised AI agents handle everything from quick ticket lookups
          to cross-department request workflows — so your team stays focused
          on what actually matters.
        </p>
        <div className="hero-ctas">
          <Link href="/help-desk-agent" className="cta-primary">
            Open Help Desk Agent
          </Link>
          <Link href="/departments-support-agent" className="cta-secondary">
            Open Departments Agent
          </Link>
        </div>

        {/* Stats strip */}
        <div className="stats-strip">
          <div className="stat-item">
            <strong>2</strong>
            <span>Specialised agents</span>
          </div>
          <div className="stat-divider" aria-hidden />
          <div className="stat-item">
            <strong>GLPI</strong>
            <span>Native integration</span>
          </div>
          <div className="stat-divider" aria-hidden />
          <div className="stat-item">
            <strong>Real-time</strong>
            <span>Ticket operations</span>
          </div>
        </div>
      </section>

      {/* ── Agent overview ── */}
      <section className="agent-overview" id="agents" aria-label="Available agents">
        <p className="eyebrow" style={{ textAlign: "center" }}>Meet the agents</p>
        <h2 className="features-heading">Two agents, one workspace</h2>
        <div className="agent-explain-grid">

          <div className="agent-explain-card">
            <div className="agent-explain-icon help-bg">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
              </svg>
            </div>
            <h3>Help Desk Agent</h3>
            <p className="agent-explain-desc">Your front-line support companion. Ask anything about open tickets, user history, or priorities — and get clear, ready-to-send replies in seconds.</p>
            <ul className="agent-explain-list">
              <li>
                <span className="agent-explain-bullet help-bullet">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
                </span>
                Search and summarise ticket history in seconds
              </li>
              <li>
                <span className="agent-explain-bullet help-bullet">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
                </span>
                Draft clear, actionable responses for end-users
              </li>
              <li>
                <span className="agent-explain-bullet help-bullet">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
                </span>
                Track priorities and status changes in one place
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
            <h3>Departments Support Agent</h3>
            <p className="agent-explain-desc">Handles structured internal requests across teams. Ensures every submission is complete, properly routed, and ready for action — no back-and-forth.</p>
            <ul className="agent-explain-list">
              <li>
                <span className="agent-explain-bullet dept-bullet">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
                </span>
                Create complete requests with all required fields
              </li>
              <li>
                <span className="agent-explain-bullet dept-bullet">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
                </span>
                Coordinate workflows across multiple internal teams
              </li>
              <li>
                <span className="agent-explain-bullet dept-bullet">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
                </span>
                Improve quality of handoffs and follow-up information
              </li>
            </ul>
          </div>

        </div>
      </section>

    </main>
  );
}
