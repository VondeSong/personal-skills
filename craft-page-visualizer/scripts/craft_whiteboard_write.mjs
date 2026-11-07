#!/usr/bin/env node

import { readFile } from "node:fs/promises";

const DIGITS = `0123456789${Array.from({ length: 26 }, (_, i) => {
  const lower = String.fromCharCode(97 + i);
  return `${lower}${lower.toUpperCase()}`;
}).join("")}`;

const args = parseArgs(process.argv.slice(2));
const operation = args.operation || "create";
const dryRun = args["dry-run"] === "true";
const API_URL = process.env.CRAFT_API_URL?.replace(/\/$/, "");
if (!dryRun && !API_URL) fail("Set CRAFT_API_URL to the Craft Connect API base URL.");
const pageId = args["page-id"];
const whiteboardIdArg = args["whiteboard-id"];
const elementsPath = args.elements;
const position = args.position || "end";
const allowExisting = args["allow-existing"] === "true";
const normalizeIndexes = args["normalize-indexes"] !== "false";

if (!elementsPath) fail("Missing --elements <path>.");
if (!new Set(["create", "append", "update"]).has(operation)) {
  fail("--operation must be create, append, or update.");
}
if (operation === "create" && !pageId) fail("create requires --page-id.");
if (operation !== "create" && !whiteboardIdArg) {
  fail(`${operation} requires --whiteboard-id.`);
}
if (!new Set(["start", "end"]).has(position)) fail("--position must be start or end.");

const raw = JSON.parse(await readFile(elementsPath, "utf8"));
let elements = Array.isArray(raw) ? raw : raw.elements;
if (!Array.isArray(elements) || elements.length === 0) {
  fail("Elements input must be a non-empty array or { elements: [...] }.");
}

elements = structuredClone(elements);
const validation = validateElements(elements, { partial: operation === "update" });
if (validation.errors.length) {
  fail(`Element validation failed:\n- ${validation.errors.join("\n- ")}`);
}

if (normalizeIndexes && operation !== "update") {
  elements = normalizeElementOrder(elements);
}

if (dryRun) {
  console.log(JSON.stringify({
    ok: true,
    dryRun: true,
    operation,
    elementCount: elements.length,
    firstIds: elements.slice(0, 8).map((element) => element.id),
    firstIndexes: elements.slice(0, 8).map((element) => element.index || null),
    bounds: calculateBounds(elements),
    warnings: validation.warnings,
  }, null, 2));
  process.exit(0);
}

const connection = await request("/connection");
let whiteboardId = whiteboardIdArg;
let pageBefore;

if (operation === "create") {
  pageBefore = await request(`/blocks?id=${encodeURIComponent(pageId)}&maxDepth=1`);
  if (!new Set(["page", "text", "collectionItem"]).has(pageBefore.type)) {
    fail(`Target ${pageId} is not a supported parent block (type=${pageBefore.type}).`);
  }
  const existing = collectWhiteboardIds(pageBefore);
  if (existing.length && !allowExisting) {
    fail(`Target already contains whiteboard(s): ${existing.join(", ")}. Confirm create vs update, then rerun with --allow-existing true only for an intentional additional whiteboard.`);
  }

  const created = await request("/whiteboards", {
    method: "POST",
    body: JSON.stringify({ position: { position, pageId } }),
  });
  whiteboardId = created.whiteboardBlockId;
  if (!whiteboardId) fail(`Create response omitted whiteboardBlockId: ${JSON.stringify(created)}`);
}

const existingState = operation === "create"
  ? { elements: [] }
  : await request(`/whiteboards/${encodeURIComponent(whiteboardId)}/elements`);
const existingIds = new Set((existingState.elements || []).map((element) => element.id));

if (operation === "append") {
  const conflicts = elements.filter((element) => existingIds.has(element.id)).map((element) => element.id);
  if (conflicts.length) fail(`append would reuse existing IDs: ${conflicts.join(", ")}`);
}
if (operation === "update") {
  const missingExisting = elements.filter((element) => !existingIds.has(element.id)).map((element) => element.id);
  if (missingExisting.length) fail(`update IDs do not exist in the whiteboard: ${missingExisting.join(", ")}`);
}

const endpoint = `/whiteboards/${encodeURIComponent(whiteboardId)}/elements`;
if (operation === "update") {
  for (const batch of payloadBatches(elements)) {
    await request(endpoint, { method: "PUT", body: JSON.stringify({ elements: batch }) });
  }
} else {
  await appendWithRecovery(endpoint, elements);
}

const verified = await request(endpoint);
const verifiedElements = Array.isArray(verified.elements) ? verified.elements : [];
const verifiedById = new Map(verifiedElements.map((element) => [element.id, element]));
const missing = elements.filter((element) => !verifiedById.has(element.id)).map((element) => element.id);
const mismatched = operation === "update"
  ? elements.filter((element) => !submittedFieldsMatch(element, verifiedById.get(element.id))).map((element) => element.id)
  : [];

if (missing.length || mismatched.length) {
  fail(`Post-write verification failed for whiteboard ${whiteboardId}. Missing: ${missing.join(", ") || "none"}; mismatched: ${mismatched.join(", ") || "none"}. Do not create another whiteboard; recover this one by ID.`);
}

let attachedToTarget = null;
if (operation === "create") {
  const pageAfter = await request(`/blocks?id=${encodeURIComponent(pageId)}&maxDepth=1`);
  attachedToTarget = collectWhiteboardIds(pageAfter).includes(whiteboardId);
  if (!attachedToTarget) {
    fail(`Whiteboard ${whiteboardId} contains the elements but was not found under target page ${pageId}. Recover by whiteboard ID; do not create another.`);
  }
}

const bounds = calculateBounds(verifiedElements.filter((element) => verifiedById.has(element.id)));
console.log(JSON.stringify({
  ok: true,
  operation,
  space: connection.space ? { id: connection.space.id, name: connection.space.name } : null,
  pageId: pageId || null,
  whiteboardBlockId: whiteboardId,
  submittedElementCount: elements.length,
  verifiedElementCount: verifiedElements.length,
  attachedToTarget,
  bounds,
  warnings: validation.warnings,
}, null, 2));

async function appendWithRecovery(endpoint, desired) {
  try {
    for (const batch of payloadBatches(desired)) {
      await request(endpoint, { method: "POST", body: JSON.stringify({ elements: batch }) });
    }
    return;
  } catch (firstError) {
    const current = await request(endpoint);
    const saved = new Set((current.elements || []).map((element) => element.id));
    const missing = desired.filter((element) => !saved.has(element.id));
    if (!missing.length) return;
    try {
      for (const batch of payloadBatches(missing)) {
        await request(endpoint, { method: "POST", body: JSON.stringify({ elements: batch }) });
      }
    } catch (retryError) {
      throw new Error(`Append failed and one missing-only retry also failed. Whiteboard=${whiteboardId}. First=${firstError.message}; Retry=${retryError.message}`);
    }
  }
}

async function request(path, options = {}) {
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: { Accept: "application/json", "Content-Type": "application/json", ...(options.headers || {}) },
  });
  const body = await response.text();
  let data;
  try { data = body ? JSON.parse(body) : {}; } catch { data = { raw: body }; }
  if (!response.ok) throw new Error(`${response.status} ${path}: ${JSON.stringify(data)}`);
  return data;
}

function validateElements(items, { partial = false } = {}) {
  const errors = [];
  const warnings = [];
  const ids = new Set();
  for (const [i, element] of items.entries()) {
    const label = element?.id || `element[${i}]`;
    if (!element || typeof element !== "object") { errors.push(`element[${i}] is not an object`); continue; }
    if (!element.id || typeof element.id !== "string") errors.push(`element[${i}] has no string id`);
    else if (ids.has(element.id)) errors.push(`duplicate id ${element.id}`);
    else ids.add(element.id);
    if (!partial && (!element.type || typeof element.type !== "string")) errors.push(`${label} has no type`);
    if (partial && element.type != null && typeof element.type !== "string") errors.push(`${label}.type is not a string`);
    for (const field of ["x", "y", "width", "height"]) {
      if ((!partial || element[field] != null) && !Number.isFinite(element[field])) errors.push(`${label}.${field} is not finite`);
    }
    if (Number.isFinite(element.width) && element.width < 0) errors.push(`${label}.width is negative`);
    if (Number.isFinite(element.height) && element.height < 0) errors.push(`${label}.height is negative`);
    if (element.type === "text" || (partial && element.text != null)) {
      if (typeof element.text !== "string" || !element.text.trim()) errors.push(`${label} has empty text`);
      if (element.originalText != null && element.originalText !== element.text) warnings.push(`${label}: originalText differs from text`);
    }
    if (["arrow", "line"].includes(element.type) || (partial && element.points != null)) {
      if (!Array.isArray(element.points) || element.points.length < 2) errors.push(`${label} needs at least two points`);
    }
  }
  if (items.length > 500) warnings.push(`${items.length} elements will be submitted in deterministic batches of 400`);
  return { errors, warnings };
}

function normalizeElementOrder(items) {
  const typePriority = (type) => {
    if (type === "frame") return 0;
    if (["arrow", "line"].includes(type)) return 1;
    if (type === "text") return 3;
    return 2;
  };
  return items
    .map((element, originalOrder) => ({ element, originalOrder }))
    .sort((a, b) => typePriority(a.element.type) - typePriority(b.element.type) || a.originalOrder - b.originalOrder)
    .map(({ element }, i) => ({ ...element, index: excalidrawIndex(i) }));
}

function excalidrawIndex(n) {
  if (n < DIGITS.length) return `a${DIGITS[n]}`;
  return `b${encodeBase62(n - DIGITS.length).padStart(2, DIGITS[0])}`;
}

function encodeBase62(n) {
  let out = "";
  do {
    out = DIGITS[n % DIGITS.length] + out;
    n = Math.floor(n / DIGITS.length);
  } while (n > 0);
  return out;
}

function collectWhiteboardIds(block) {
  const result = [];
  const visit = (node) => {
    if (!node || typeof node !== "object") return;
    if (node.type === "whiteboard" && node.id) result.push(node.id);
    if (Array.isArray(node.content)) node.content.forEach(visit);
  };
  visit(block);
  return result;
}

function submittedFieldsMatch(submitted, actual) {
  if (!actual) return false;
  return Object.entries(submitted).every(([key, value]) => JSON.stringify(actual[key]) === JSON.stringify(value));
}

function calculateBounds(items) {
  const finite = items.filter((element) => Number.isFinite(element.x) && Number.isFinite(element.y));
  if (!finite.length) return null;
  return finite.reduce((acc, element) => ({
    minX: Math.min(acc.minX, element.x),
    minY: Math.min(acc.minY, element.y),
    maxX: Math.max(acc.maxX, element.x + (Number.isFinite(element.width) ? element.width : 0)),
    maxY: Math.max(acc.maxY, element.y + (Number.isFinite(element.height) ? element.height : 0)),
  }), { minX: Infinity, minY: Infinity, maxX: -Infinity, maxY: -Infinity });
}

function payloadBatches(items, { maxCount = 400, maxBytes = 64 * 1024 } = {}) {
  const result = [];
  let batch = [];
  for (const item of items) {
    const candidate = [...batch, item];
    const bytes = new TextEncoder().encode(JSON.stringify({ elements: candidate })).length;
    if (batch.length && (candidate.length > maxCount || bytes > maxBytes)) {
      result.push(batch);
      batch = [item];
    } else {
      batch = candidate;
    }
  }
  if (batch.length) result.push(batch);
  return result;
}

function parseArgs(argv) {
  const parsed = {};
  for (let i = 0; i < argv.length; i += 2) {
    const key = argv[i];
    const value = argv[i + 1];
    if (!key?.startsWith("--") || value == null) fail(`Invalid arguments near ${key || "end"}`);
    parsed[key.slice(2)] = value;
  }
  return parsed;
}

function fail(message) {
  console.error(message);
  process.exit(1);
}
