import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Proxy /recommend and /events to FastAPI during local dev.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/recommend": "http://127.0.0.1:8000",
      "/events": "http://127.0.0.1:8000",
      "/health": "http://127.0.0.1:8000",
    },
  },
});
