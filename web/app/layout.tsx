import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "GLPI Agent",
  description: "A modern chat web UI for the OpenRouter-powered GLPI agent",
  icons: { icon: "/icon.svg" },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body suppressHydrationWarning>{children}</body>
    </html>
  );
}
