import { execFile } from "node:child_process";
import path from "node:path";
import { promisify } from "node:util";
import { NextRequest, NextResponse } from "next/server";

const execFileAsync = promisify(execFile);
const repoRoot = path.resolve(process.cwd(), "..");

type ChatRequest = {
  agent?: "admin" | "departments-support-agent";
  message?: string;
  messages?: Array<{
    role?: "assistant" | "user";
    content?: string;
  }>;
  model?: string;
  state?: Record<string, unknown>;
  user?: {
    email?: string;
    name?: string;
  };
};

function buildContextualMessage(body: ChatRequest, message: string): string {
  const history = Array.isArray(body.messages) ? body.messages : [];
  const cleaned = history
    .filter((item) => item.role && typeof item.content === "string" && item.content.trim())
    .slice(-8)
    .map((item) => `${item.role === "assistant" ? "Assistant" : "Utilisateur"}: ${item.content!.trim()}`);

  if (cleaned.length <= 1) {
    return message;
  }

  return [
    "Contexte de conversation du chat web :",
    ...cleaned,
    "",
    "Utilise le contexte ci-dessus pour résoudre les confirmations courtes comme \"oui crée-le\" ou \"fais-le\".",
    `Message utilisateur courant : ${message}`,
  ].join("\n");
}

export async function POST(request: NextRequest) {
  let body: ChatRequest;

  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: "Requête JSON invalide." }, { status: 400 });
  }

  const message = body.message?.trim();
  if (!message) {
    return NextResponse.json({ error: "Le message est requis." }, { status: 400 });
  }

  const isDepartmentsSupportAgent = body.agent === "departments-support-agent";
  const contextualMessage = buildContextualMessage(body, message);

  const backendUrl = isDepartmentsSupportAgent
    ? (process.env.BACKEND_KB_URL || process.env.BACKEND_URL)
    : process.env.BACKEND_URL;

  if (backendUrl) {
    try {
      const response = await fetch(`${backendUrl.replace(/\/$/, "")}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: contextualMessage,
          model: body.model?.trim() || undefined,
          state: isDepartmentsSupportAgent && body.state ? body.state : undefined,
          user: isDepartmentsSupportAgent && body.user ? body.user : undefined,
        }),
      });
      const data = await response.json();
      return NextResponse.json(data, { status: response.status });
    } catch (error) {
      const detail = error instanceof Error ? error.message : "Erreur inconnue";
      return NextResponse.json(
        {
          error: isDepartmentsSupportAgent
            ? "Le backend Support Départements est inaccessible."
            : "Le backend GLPI est inaccessible.",
          detail,
        },
        { status: 502 },
      );
    }
  }

  const agentDir = isDepartmentsSupportAgent ? "departments-support-agent" : "help-desk-agent";
  const args = ["run", "main.py"];
  if (body.model?.trim()) {
    args.push("--model", body.model.trim());
  }
  args.push(contextualMessage);

  try {
    const { stdout, stderr } = await execFileAsync("uv", args, {
      cwd: path.join(repoRoot, agentDir),
      timeout: 120000,
      maxBuffer: 1024 * 1024,
    });

    return NextResponse.json({
      answer: stdout.trim() || "L'agent a terminé sans réponse textuelle.",
      stderr: stderr.trim() || null,
    });
  } catch (error) {
    const detail = error instanceof Error ? error.message : "Erreur inconnue";
    return NextResponse.json(
      {
        error: isDepartmentsSupportAgent
          ? "L'agent Support Départements a échoué."
          : "L'agent GLPI a échoué.",
        detail,
      },
      { status: 500 },
    );
  }
}
