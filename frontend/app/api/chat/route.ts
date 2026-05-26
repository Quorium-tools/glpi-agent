import { execFile } from "node:child_process";
import path from "node:path";
import { promisify } from "node:util";
import { NextRequest, NextResponse } from "next/server";

const execFileAsync = promisify(execFile);
const repoRoot = path.resolve(process.cwd(), "..");

type ChatRequest = {
  agent?: "admin" | "knowledge-base";
  message?: string;
  dryRun?: boolean;
  model?: string;
  userEmail?: string;
};

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

  const isKb = body.agent === "knowledge-base";
  const module = isKb ? "glpi_agent.cli_knowledge_base_agent" : "glpi_agent.cli";

  const args = ["-m", module];
  if (body.dryRun) {
    args.push("--dry-run");
  }
  if (body.model?.trim()) {
    args.push("--model", body.model.trim());
  }
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
