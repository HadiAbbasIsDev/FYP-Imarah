// Use: build the PWA and send development API calls to our Python server.
// Copyright (c) 2026 Imarah.tech. All rights reserved.
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/api": "http://127.0.0.1:8000",
      "/uploads": "http://127.0.0.1:8000",
      "/samples": "http://127.0.0.1:8000",
    },
  },
});
