import { execFile } from "node:child_process";
import path from "node:path";
import { promisify } from "node:util";
import { NextRequest, NextResponse } from "next/server";

const execFileAsync = promisify(execFile);
const repoRoot = path.resolve(process.cwd(), "..");

type ChatRequest = {
  agent?: "admin" | "knowledge-base";
  message?: string;
  messages?: Array<{
    role?: "assistant" | "user";
    content?: string;
  }>;
  model?: string;
  userEmail?: string;
};

function buildContextualMessage(body: ChatRequest, message: string): string {
  const history = Array.isArray(body.messages) ? body.messages : [];
  const cleaned = history
    .filter((item) => item.role && typeof item.content === "string" && item.content.trim())
    .slice(-8)
    .map((item) => `${item.role === "assistant" ? "Assistant" : "User"}: ${item.content!.trim()}`);

  if (cleaned.length <= 1) {
    return message;
  }

  return [
    "Conversation context from the web chat:",
    ...cleaned,
    "",
    "Use the context above to resolve short confirmations like \"yes create it\" or \"do it\".",
    `Current user message: ${message}`,
  ].join("\n");
}

export async function POST(request: NextRequest) {
  let body: ChatRequest;

  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: "Invalid JSON request." }, { status: 400 });
  }

  const message = body.message?.trim();
  if (!message) {
    return NextResponse.json({ error: "Message is required." }, { status: 400 });
  }

  const contextualMessage = buildContextualMessage(body, message);

  if (process.env.BACKEND_URL) {
    try {
      const response = await fetch(`${process.env.BACKEND_URL.replace(/\/$/, "")}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: contextualMessage,
          dryRun: false,
          model: body.model?.trim() || undefined,
        }),
      });

      const data = await response.json();
      return NextResponse.json(data, { status: response.status });
    } catch (error) {
      const detail = error instanceof Error ? error.message : "Unknown error";
      return NextResponse.json(
        {
          error: "The GLPI backend is unreachable.",
          detail,
        },
        { status: 502 },
      );
    }
  const isKb = body.agent === "knowledge-base";
  const module = isKb ? "glpi_agent.cli_knowledge_base_agent" : "glpi_agent.cli";

  const args = ["-m", module];
  if (body.dryRun) {
    args.push("--dry-run");
  }

  const args = ["-m", "glpi_agent.cli"];
  if (body.model?.trim()) {
    args.push("--model", body.model.trim());
  }
  args.push(contextualMessage);
  if (isKb && body.userEmail?.trim()) {
    args.push("--user-email", body.userEmail.trim());
  }
  args.push(message);

  try {
    const { stdout, stderr } = await execFileAsync("python", args, {
      cwd: repoRoot,
      timeout: 120000,
      maxBuffer: 1024 * 1024,
    });

    return NextResponse.json({
      answer: stdout.trim() || "The agent finished without a text response.",
      stderr: stderr.trim() || null,
    });
  } catch (error) {
    const detail = error instanceof Error ? error.message : "Unknown error";
    return NextResponse.json(
      {
        error: isKb ? "The Knowledge Base agent failed." : "The GLPI agent failed.",
        detail,
      },
      { status: 500 },
    );
  }
}
