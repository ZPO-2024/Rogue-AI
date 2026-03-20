/**
 * seed_priority_oss.js
 * Seeds the Apocalypse Zero OSS integration queue with priority repos.
 * Run once to initialize data/apocalypse-zero/repo-queue.json.
 * Usage: node scripts/seed_priority_oss.js
 */

const fs = require("fs");
const path = require("path");

const DATA_DIR = path.join(__dirname, "..", "data", "apocalypse-zero");
const QUEUE_FILE = path.join(DATA_DIR, "repo-queue.json");
const BRIEFS_DIR = path.join(DATA_DIR, "briefs");

// Priority OSS repos for AZ integration
const PRIORITY_REPOS = [
  {
    id: "voltagent",
    name: "VoltAgent",
    repo: "voltagent/voltagent",
    priority: 1,
    status: "queued",
    reason: "TypeScript AI agent framework — primary orchestration backbone for AZ",
    integrationTarget: "echo-api",
    briefFile: "voltagent.md",
    addedAt: new Date().toISOString(),
  },
  {
    id: "qdrant-js",
    name: "Qdrant JS Client",
    repo: "qdrant/qdrant-client-ts",
    priority: 2,
    status: "queued",
    reason: "Vector memory backend — wire after VoltAgent as memory provider",
    integrationTarget: "echo-api",
    briefFile: "qdrant-js.md",
    addedAt: new Date().toISOString(),
    dependsOn: ["voltagent"],
  },
  {
    id: "deer-flow",
    name: "DeerFlow",
    repo: "bytedance/deer-flow",
    priority: 3,
    status: "queued",
    reason: "Deep research multi-agent — Python sidecar on port 3002 for AZ research tasks",
    integrationTarget: "echo-api",
    briefFile: "deer-flow.md",
    addedAt: new Date().toISOString(),
  },
];

function seed() {
  // Ensure directories exist
  if (!fs.existsSync(DATA_DIR)) {
    fs.mkdirSync(DATA_DIR, { recursive: true });
    console.log("Created:", DATA_DIR);
  }
  if (!fs.existsSync(BRIEFS_DIR)) {
    fs.mkdirSync(BRIEFS_DIR, { recursive: true });
    console.log("Created:", BRIEFS_DIR);
  }

  // Write or merge queue
  let existing = [];
  if (fs.existsSync(QUEUE_FILE)) {
    try {
      existing = JSON.parse(fs.readFileSync(QUEUE_FILE, "utf-8"));
      console.log("Existing queue loaded:", existing.length, "entries");
    } catch (e) {
      console.warn("Could not parse existing queue, starting fresh");
    }
  }

  // Merge: skip existing IDs
  const existingIds = new Set(existing.map((r) => r.id));
  const toAdd = PRIORITY_REPOS.filter((r) => !existingIds.has(r.id));
  const merged = [...existing, ...toAdd];

  fs.writeFileSync(QUEUE_FILE, JSON.stringify(merged, null, 2));
  console.log("Queue seeded:", QUEUE_FILE);
  console.log("Added", toAdd.length, "new entries:", toAdd.map((r) => r.id).join(", "));
  console.log("Total queue size:", merged.length);
}

seed();
