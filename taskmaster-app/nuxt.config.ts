import tailwindcss from "@tailwindcss/vite";

// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  ssr: false,
  compatibilityDate: "2025-05-15",
  devtools: { enabled: true },
  css: ["~/assets/css/main.css"],
  vite: {
    plugins: [tailwindcss()],
  },
  runtimeConfig: {
    public: {
      // This variable will hold our API URL.
      // The default value points to your local Django server.
      // apiBase: "https://54.90.204.70/api/",
      apiBase: "http://localhost:8000/api/",
    },
  },

  modules: ["@nuxt/eslint", "@nuxt/icon", "@nuxt/ui", "@pinia/nuxt"],
});
