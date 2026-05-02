import path from "path";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import { tanstackRouter } from "@tanstack/router-plugin/vite";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    // TanStack Router plugin must come before React
    tanstackRouter({
      target: "react",
      autoCodeSplitting: true,
    }),
    react(),
    tailwindcss(),
  ],
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: ["./src/tests/setup.ts"],
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
      components: path.resolve(__dirname, "./src/components"),
      integrations: path.resolve(__dirname, "./src/integrations"),
      hooks: path.resolve(__dirname, "./src/hooks"),
      layout: path.resolve(__dirname, "./src/layout"),
      pages: path.resolve(__dirname, "./src/pages"),
      routes: path.resolve(__dirname, "./src/routes"),
      utils: path.resolve(__dirname, "./src/utils"),
      tests: path.resolve(__dirname, "./src/tests"),
      types: path.resolve(__dirname, "./src/types"),
    },
  },
});
