import express from "express";
import path from "path";
import { createServer as createViteServer } from "vite";
import zlib from "zlib";

async function startServer() {
  const app = express();
  const PORT = 3000;

  // Increase payload limit for large Python scripts
  app.use(express.json({ limit: "10mb" }));

  // API Route to serve the raw python script
  app.get("/api/script", (req, res) => {
    try {
      const scriptPath = path.join(process.cwd(), "script.py");
      res.sendFile(scriptPath);
    } catch (error: any) {
      res.status(500).send("Error serving script");
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
