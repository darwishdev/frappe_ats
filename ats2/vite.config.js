import path from "node:path";
import vue from "@vitejs/plugin-vue";
import frappeui from "frappe-ui/vite";
import { defineConfig } from "vite";

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [
        frappeui({
            frappeProxy: true,
            jinjaBootData: true,
            lucideIcons: true,
            buildConfig: {
                outDir: "../mawhub/public/ats2",
                indexHtmlPath: "../mawhub/www/ats2.html",
                emptyOutDir: true,
                sourcemap: true,
            },
        }),
        vue(),
    ],
    build: {
        chunkSizeWarningLimit: 1500,
        outDir: "../mawhub/public/ats2",
        emptyOutDir: true,
        target: "es2015",
        sourcemap: true,
    },
    resolve: {
        alias: {
            "@": path.resolve(__dirname, "src"),
            "tailwind.config.js": path.resolve(__dirname, "tailwind.config.js"),
        },
    },
    optimizeDeps: {
        include: ["feather-icons", "showdown", "highlight.js/lib/core", "interactjs"],
    },
    server: {
        allowedHosts: true,
        port: 8080,
    },
});
