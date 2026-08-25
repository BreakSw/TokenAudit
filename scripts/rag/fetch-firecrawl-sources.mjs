import { createHash } from "node:crypto";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";

function parseArgs(argv) {
  const args = {};
  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    if (!token.startsWith("--")) continue;
    const name = token.slice(2);
    args[name] = argv[index + 1];
    index += 1;
  }
  return args;
}

function parseEnv(text) {
  const values = new Map();
  for (const rawLine of text.split(/\r?\n/u)) {
    const line = rawLine.trim();
    if (!line || line.startsWith("#")) continue;
    const separator = line.indexOf("=");
    if (separator < 1) continue;
    const key = line.slice(0, separator).trim();
    let value = line.slice(separator + 1).trim();
    if (
      value.length >= 2 &&
      ((value.startsWith('"') && value.endsWith('"')) ||
        (value.startsWith("'") && value.endsWith("'")))
    ) {
      value = value.slice(1, -1);
    }
    values.set(key, value);
  }
  return values;
}

function resolveEndpoint(baseUrl) {
  const normalized = baseUrl.replace(/\/+$/u, "");
  if (/\/scrape$/u.test(normalized)) return normalized;
  if (/\/v[12]$/u.test(normalized)) return `${normalized}/scrape`;
  return `${normalized}/v2/scrape`;
}

function yamlValue(value) {
  return JSON.stringify(value ?? "");
}

function sha256(text) {
  return createHash("sha256").update(text, "utf8").digest("hex");
}

function sleep(milliseconds) {
  return new Promise((resolve) => setTimeout(resolve, milliseconds));
}

function safeFirecrawlMetadata(metadata = {}) {
  const allowedKeys = [
    "title",
    "description",
    "language",
    "sourceURL",
    "url",
    "statusCode",
    "contentType",
    "publishedTime",
    "modifiedTime",
    "author",
    "ogTitle",
    "ogDescription",
  ];
  return Object.fromEntries(
    allowedKeys
      .filter((key) => metadata[key] !== undefined)
      .map((key) => [key, metadata[key]]),
  );
}

async function captureSource({
  source,
  model,
  modelReviewStatus,
  outputRoot,
  endpoint,
  apiKey,
}) {
  const capturedAt = new Date().toISOString();
  const sourceDirectory = path.join(
    outputRoot,
    source.priority.toLowerCase(),
    source.id,
  );
  await mkdir(sourceDirectory, { recursive: true });

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 90_000);

  let httpStatus = null;
  let payload = null;
  let requestError = null;

  try {
    const response = await fetch(endpoint, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${apiKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        url: source.url,
        formats: ["markdown"],
        onlyMainContent: true,
      }),
      signal: controller.signal,
    });
    httpStatus = response.status;
    const responseText = await response.text();
    try {
      payload = JSON.parse(responseText);
    } catch {
      requestError = "Firecrawl returned a non-JSON response.";
    }
  } catch (error) {
    requestError = error instanceof Error ? error.message : String(error);
  } finally {
    clearTimeout(timeout);
  }

  const data = payload?.data ?? {};
  const remoteMetadata = data.metadata ?? {};
  const markdown = typeof data.markdown === "string" ? data.markdown.trim() : "";
  const pageStatus = Number(remoteMetadata.statusCode ?? httpStatus ?? 0) || null;
  const valid = Boolean(
    payload?.success === true &&
      httpStatus !== null &&
      httpStatus < 400 &&
      pageStatus !== null &&
      pageStatus < 400 &&
      markdown.length >= 80,
  );

  const metadata = {
    schemaVersion: 1,
    model,
    modelReviewStatus,
    priority: source.priority,
    sourceId: source.id,
    label: source.label,
    requestedUrl: source.url,
    finalUrl: remoteMetadata.sourceURL ?? remoteMetadata.url ?? source.url,
    capturedAt,
    captureProvider: "firecrawl",
    endpointVersion: endpoint.match(/\/v([12])\//u)?.[1] ?? "unknown",
    firecrawlHttpStatus: httpStatus,
    sourceHttpStatus: pageStatus,
    apiSuccess: payload?.success === true,
    acceptedForReview: valid,
    markdownCharacters: markdown.length,
    markdownSha256: markdown ? sha256(markdown) : null,
    error: requestError ?? payload?.error ?? null,
    sourceMetadata: safeFirecrawlMetadata(remoteMetadata),
  };

  await writeFile(
    path.join(sourceDirectory, "metadata.json"),
    `${JSON.stringify(metadata, null, 2)}\n`,
    "utf8",
  );

  if (markdown) {
    const frontMatter = [
      "---",
      `model: ${yamlValue(model)}`,
      `priority: ${yamlValue(source.priority)}`,
      `source_id: ${yamlValue(source.id)}`,
      `title: ${yamlValue(remoteMetadata.title ?? source.label)}`,
      `source_url: ${yamlValue(source.url)}`,
      `final_url: ${yamlValue(metadata.finalUrl)}`,
      `captured_at: ${yamlValue(capturedAt)}`,
      `capture_provider: ${yamlValue("firecrawl")}`,
      `accepted_for_review: ${valid}`,
      `sha256: ${yamlValue(metadata.markdownSha256)}`,
      "---",
      "",
    ].join("\n");
    const filename = valid ? "content.md" : "rejected-content.md";
    await writeFile(
      path.join(sourceDirectory, filename),
      `${frontMatter}${markdown}\n`,
      "utf8",
    );
  }

  return {
    sourceId: source.id,
    priority: source.priority,
    requestedUrl: source.url,
    acceptedForReview: valid,
    firecrawlHttpStatus: httpStatus,
    sourceHttpStatus: pageStatus,
    markdownCharacters: markdown.length,
    directory: path.relative(outputRoot, sourceDirectory).replaceAll("\\", "/"),
    error: metadata.error,
  };
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (!args.manifest || !args.output || !args.env) {
    throw new Error(
      "Usage: node fetch-firecrawl-sources.mjs --manifest <file> --output <dir> --env <file>",
    );
  }

  const [manifestText, envText] = await Promise.all([
    readFile(path.resolve(args.manifest), "utf8"),
    readFile(path.resolve(args.env), "utf8"),
  ]);
  const manifest = JSON.parse(manifestText);
  const env = parseEnv(envText);
  const apiKey = env.get("firecrawl-api-key") ?? env.get("FIRECRAWL_API_KEY");
  const baseUrl =
    env.get("firecrawl-base-url") ??
    env.get("FIRECRAWL_BASE_URL") ??
    "https://api.firecrawl.dev/v2";
  if (!apiKey) throw new Error("Firecrawl API key is missing.");

  const outputRoot = path.resolve(args.output);
  const delayMilliseconds = Math.max(0, Number(args["delay-ms"] ?? 0));
  if (!Number.isFinite(delayMilliseconds)) {
    throw new Error("--delay-ms must be a finite number.");
  }
  await mkdir(outputRoot, { recursive: true });
  const endpoint = resolveEndpoint(baseUrl);
  const results = [];

  for (const source of manifest.sources) {
    process.stdout.write(`Capturing ${source.priority}/${source.id} ... `);
    const result = await captureSource({
      source,
      model: manifest.model,
      modelReviewStatus: manifest.reviewStatus ?? "UNREVIEWED",
      outputRoot,
      endpoint,
      apiKey,
    });
    results.push(result);
    process.stdout.write(result.acceptedForReview ? "accepted\n" : "rejected\n");
    if (delayMilliseconds > 0) {
      await sleep(delayMilliseconds);
    }
  }

  const report = {
    schemaVersion: 1,
    model: manifest.model,
    modelReviewStatus: manifest.reviewStatus ?? "UNREVIEWED",
    generatedAt: new Date().toISOString(),
    total: results.length,
    accepted: results.filter((item) => item.acceptedForReview).length,
    rejected: results.filter((item) => !item.acceptedForReview).length,
    results,
  };
  await writeFile(
    path.join(outputRoot, "capture-report.json"),
    `${JSON.stringify(report, null, 2)}\n`,
    "utf8",
  );
  process.stdout.write(
    `Done: ${report.accepted} accepted, ${report.rejected} rejected.\n`,
  );
}

main().catch((error) => {
  process.stderr.write(`${error instanceof Error ? error.message : String(error)}\n`);
  process.exitCode = 1;
});
