import Link from "next/link";

export default function Home() {
  return (
    <main style={{ padding: "2rem", display: "grid", gap: "1rem", maxWidth: 420 }}>
      <h1>Choose an Agent</h1>
      <Link href="/help-desk-agent">
        <button type="button">Help Desk Agent</button>
      </Link>
      <Link href="/departments-support-agent">
        <button type="button">Departments Support Agent</button>
      </Link>
    </main>
  );
}
