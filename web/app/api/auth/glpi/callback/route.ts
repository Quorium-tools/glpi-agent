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
    const state = req.nextUrl.searchParams.get("state") || "";
    const code = req.nextUrl.searchParams.get("code") || "";
    const expectedState = req.cookies.get("glpi_oauth_state")?.value || "";

    if (!code) {
      return NextResponse.redirect(new URL("/login?error=missing_code", req.url));
    }

    if (!state || !expectedState || state !== expectedState) {
      return NextResponse.redirect(new URL("/login?error=invalid_state", req.url));
    }

    const glpiBaseUrl = getRequiredEnv("GLPI_BASE_URL").replace(/\/$/, "");
    const clientId = getRequiredEnv("GLPI_OAUTH_CLIENT_ID");
    const clientSecret = getRequiredEnv("GLPI_OAUTH_CLIENT_SECRET");

    const redirectUri =
      process.env.GLPI_OAUTH_REDIRECT_URI?.trim() || `${getBaseUrl(req)}/api/auth/glpi/callback`;

    const tokenPath = process.env.GLPI_OAUTH_TOKEN_PATH?.trim() || "/oauth/token.php";
    const tokenUrl = new URL(tokenPath, `${glpiBaseUrl}/`);

    const payload = new URLSearchParams({
      grant_type: "authorization_code",
      code,
      client_id: clientId,
      client_secret: clientSecret,
      redirect_uri: redirectUri,
    });

    const tokenResponse = await fetch(tokenUrl.toString(), {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: payload.toString(),
      cache: "no-store",
    });

    if (!tokenResponse.ok) {
      const detail = await tokenResponse.text();
      const redirect = new URL("/login", req.url);
      redirect.searchParams.set("error", "token_exchange_failed");
      redirect.searchParams.set("status", String(tokenResponse.status));
      redirect.searchParams.set("detail", detail.slice(0, 180));
      return NextResponse.redirect(redirect);
    }

    const tokenJson = (await tokenResponse.json()) as {
      access_token?: string;
      refresh_token?: string;
      expires_in?: number;
      token_type?: string;
      scope?: string;
      username?: string;
      user_name?: string;
      name?: string;
      email?: string;
      user?: {
        username?: string;
        name?: string;
        email?: string;
      };
    };

    if (!tokenJson.access_token) {
      return NextResponse.redirect(new URL("/login?error=missing_access_token", req.url));
    }

    const redirect = NextResponse.redirect(new URL("/departments-support-agent?auth=success", req.url));
    redirect.cookies.delete("glpi_oauth_state");
    redirect.cookies.set("glpi_access_token", tokenJson.access_token, {
      httpOnly: true,
      sameSite: "lax",
      secure: process.env.NODE_ENV === "production",
      path: "/",
      maxAge: Math.max(60, tokenJson.expires_in || 3600),
    });

    if (tokenJson.refresh_token) {
      redirect.cookies.set("glpi_refresh_token", tokenJson.refresh_token, {
        httpOnly: true,
        sameSite: "lax",
        secure: process.env.NODE_ENV === "production",
        path: "/",
        maxAge: 60 * 60 * 24 * 30,
      });
    }

    if (tokenJson.scope) {
      redirect.cookies.set("glpi_oauth_scope", tokenJson.scope, {
        httpOnly: true,
        sameSite: "lax",
        secure: process.env.NODE_ENV === "production",
        path: "/",
        maxAge: 60 * 60 * 24,
      });
    }

    const candidateName = tokenJson.name || tokenJson.user?.name;
    const candidateUsername = tokenJson.username || tokenJson.user_name || tokenJson.user?.username;
    const candidateEmail = tokenJson.email || tokenJson.user?.email;
    if (candidateName || candidateUsername || candidateEmail) {
      redirect.cookies.set(
        "glpi_user_info",
        JSON.stringify({
          name: candidateName || "",
          username: candidateUsername || "",
          email: candidateEmail || "",
        }),
        {
          httpOnly: true,
          sameSite: "lax",
          secure: process.env.NODE_ENV === "production",
          path: "/",
          maxAge: 60 * 60 * 24,
        },
      );
    }

    return redirect;
  } catch {
    return NextResponse.redirect(new URL("/login?error=oauth_callback_failed", req.url));
  }
}
