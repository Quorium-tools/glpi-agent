import crypto from "node:crypto";
import { NextRequest, NextResponse } from "next/server";

function getRequiredEnv(name: string): string {
  const value = process.env[name]?.trim();
  if (!value) {
    throw new Error(`Missing environment variable: ${name}`);
  }
  return value;
}

function getBaseUrl(req: NextRequest): string {
  const configured = process.env.NEXT_PUBLIC_APP_URL?.trim();
  if (configured) return configured.replace(/\/$/, "");
  return req.nextUrl.origin;
}

export async function GET(req: NextRequest) {
  try {
    const glpiBaseUrl = getRequiredEnv("GLPI_BASE_URL").replace(/\/$/, "");
    const clientId = getRequiredEnv("GLPI_OAUTH_CLIENT_ID");
    const scope = (process.env.GLPI_OAUTH_SCOPE || "api").trim();

    const redirectUri =
      process.env.GLPI_OAUTH_REDIRECT_URI?.trim() || `${getBaseUrl(req)}/api/auth/glpi/callback`;

    const authorizePath = process.env.GLPI_OAUTH_AUTHORIZE_PATH?.trim() || "/oauth/authorize.php";
    const authorizeUrl = new URL(authorizePath, `${glpiBaseUrl}/`);

    const state = crypto.randomBytes(24).toString("hex");

    authorizeUrl.searchParams.set("response_type", "code");
    authorizeUrl.searchParams.set("client_id", clientId);
    authorizeUrl.searchParams.set("redirect_uri", redirectUri);
    authorizeUrl.searchParams.set("scope", scope);
    authorizeUrl.searchParams.set("state", state);

    const res = NextResponse.redirect(authorizeUrl.toString());
    res.cookies.set("glpi_oauth_state", state, {
      httpOnly: true,
      sameSite: "lax",
      secure: process.env.NODE_ENV === "production",
      path: "/",
      maxAge: 60 * 10,
    });
    return res;
  } catch (error) {
    const message = error instanceof Error ? error.message : "OAuth start failed";
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
