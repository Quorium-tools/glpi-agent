import type { NextConfig } from "next";

const DEFAULT_OPENROUTER_MODEL = "anthropic/claude-opus-4.7";

const nextConfig: NextConfig = {
  allowedDevOrigins: ["dev.glpi-agent.quorium.dev"],
  env: {
    NEXT_PUBLIC_OPENROUTER_MODEL:
      process.env.OPENROUTER_MODEL?.trim() || DEFAULT_OPENROUTER_MODEL,
  },
};

export default nextConfig;
