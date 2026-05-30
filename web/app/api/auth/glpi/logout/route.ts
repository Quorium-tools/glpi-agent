import { NextResponse } from "next/server";

export async function POST(req: Request) {
  const response = NextResponse.redirect(new URL("/login?logged_out=1", req.url));
  response.cookies.delete("glpi_access_token");
  response.cookies.delete("glpi_refresh_token");
  response.cookies.delete("glpi_oauth_scope");
  response.cookies.delete("glpi_user_info");
  response.cookies.delete("glpi_oauth_state");
  return response;
}
