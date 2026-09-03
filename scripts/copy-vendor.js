import { cpSync, existsSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const vendorRoot = join(root, "assets", "vendor");

function copyFile(from, to) {
  mkdirSync(dirname(to), { recursive: true });
  cpSync(from, to);
}

function copyLenis() {
  const lenisDir = join(root, "node_modules", "lenis", "dist");

  if (!existsSync(lenisDir)) {
    console.warn("[copy-vendor] lenis not installed, skipping");
    return;
  }

  copyFile(join(lenisDir, "lenis.mjs"), join(vendorRoot, "lenis", "lenis.mjs"));
  copyFile(join(lenisDir, "lenis.css"), join(vendorRoot, "lenis", "lenis.css"));
}

copyLenis();

console.log("[copy-vendor] lenis copied to assets/vendor");
