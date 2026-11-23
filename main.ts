import { copyFileSync, mkdirSync, statSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR || "/output";
mkdirSync(outDir, { recursive: true });
const dest = join(outDir, "entry.png");
copyFileSync(join(here, "entry.png"), dest);
const bytes = statSync(dest).size;
if (bytes > 1048576) throw new Error(`entry.png too large: ${bytes} bytes`);
console.log(`wrote ${dest} (${bytes} bytes)`);
