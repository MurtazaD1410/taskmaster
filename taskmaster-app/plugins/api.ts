// plugins/api.ts
import { ofetch } from "ofetch";
import { useAuthStore } from "~/stores/auth"; // Make sure to import the store

export default defineNuxtPlugin(() => {
  // 🚨 DO NOT get the authStore here.

  const apiFetcher = ofetch.create({
    baseURL: "http://127.0.0.1:8000/api/",

    onRequest({ options }) {
      // ✅ Get a fresh instance of the store on EACH request.
      const authStore = useAuthStore();
      if (authStore.accessToken) {
        const headers = new Headers(options.headers);
        headers.set("Authorization", `Bearer ${authStore.accessToken}`);
        options.headers = headers;
      }
    },

    async onResponseError({ request, response, options }) {
      // ✅ Get a fresh instance of the store here as well.
      const authStore = useAuthStore();
      console.log(response);

      if (response.status !== 401) {
        return;
      }

      // I've adjusted your endpoint to match the Django default
      if (String(request).endsWith("/auth/refresh")) {
        return;
      }

      try {
        console.log("Access token expired, attempting to refresh...");
        const newAccessToken = await authStore.refreshAccessToken();

        if (!newAccessToken) {
          throw new Error("Failed to fetch access token");
        }

        const newHeaders = new Headers(options.headers);
        newHeaders.set("Authorization", `Bearer ${newAccessToken}`);

        console.log("Retrying original request with new token.");
        // Retry the original request with the new token
        await ofetch(request, { ...options, headers: newHeaders });
      } catch (error) {
        console.error("Could not retrieve refresh token.", error);
        // If refresh fails, log the user out.
        authStore.logout();
      }
    },
  });

  return {
    provide: {
      api: apiFetcher,
    },
  };
});
// 54.221.5.89
