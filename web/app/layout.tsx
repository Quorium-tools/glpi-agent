import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "GLPI Agent",
  description: "Une interface de chat moderne pour l'agent GLPI propulsé par OpenRouter",
  icons: { icon: "/icon.svg" },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="fr">
      <body suppressHydrationWarning>{children}</body>
    </html>
  );
}
