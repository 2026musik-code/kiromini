import express from "express";
import path from "path";
import { createServer as createViteServer } from "vite";
import zlib from "zlib";

async function startServer() {
  const app = express();
  const PORT = 3000;

  // Increase payload limit for large Python scripts
  app.use(express.json({ limit: "10mb" }));

  // API Route to obfuscate and generate Cloudflare Worker code
  app.post("/api/generate", (req, res) => {
    try {
      const { pythonCode } = req.body;
      if (!pythonCode) {
        return res.status(400).json({ error: "Python code is required" });
      }

      // 1. Inject the .env parser at the top of the script
      const injectedCode = `
import os
import sys

# --- AUTO ENV PARSER ---
if os.path.exists('.env'):
    with open('.env', 'r', encoding='utf-8') as f:
        for line in f:
            if '=' in line and not line.strip().startswith('#'):
                k, v = line.strip().split('=', 1)
                os.environ[k.strip()] = v.strip()

# Validasi ENV
if not os.environ.get("KEY_MINI") or not os.environ.get("URL_MINI"):
    print("\\n[!] ERROR: File .env tidak ditemukan atau tidak lengkap!")
    print("[!] Buat file .env di folder ini dengan isi:")
    print("URL_MINI=https://...")
    print("KEY_MINI=sk-...")
    sys.exit(1)
# -----------------------

${pythonCode}
`;

      // 2. Compress using zlib and encode to base64
      // Node's zlib.deflateSync creates a zlib stream compatible with Python's zlib.decompress
      const compressed = zlib.deflateSync(Buffer.from(injectedCode, 'utf-8'));
      const base64Str = compressed.toString('base64');

      // 3. Wrap it in a Cloudflare Worker script
      const workerCode = `
export default {
  async fetch(request, env, ctx) {
    // Generated Obfuscated Python Script
    const pythonPayload = \`
import base64, zlib
try:
    exec(zlib.decompress(base64.b64decode('${base64Str}')).decode('utf-8'))
except Exception as e:
    print(f"\\n[!] Execution Error: {e}")
\`.trim();

    return new Response(pythonPayload, {
      headers: {
        "content-type": "text/plain;charset=UTF-8",
        "Access-Control-Allow-Origin": "*",
      },
    });
  },
};
`;

      res.json({ workerCode });
    } catch (error: any) {
      console.error(error);
      res.status(500).json({ error: error.message });
    }
  });

  // Vite middleware for development
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), "dist");
    app.use(express.static(distPath));
    app.get("*", (req, res) => {
      res.sendFile(path.join(distPath, "index.html"));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`Server running on http://localhost:${PORT}`);
  });
}

startServer();
