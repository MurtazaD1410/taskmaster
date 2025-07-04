// plugins/auth.ts (The new debugging version)
import { useAuthStore } from "~/stores/auth";

export default defineNuxtPlugin(async () => {
  console.log("1. Auth plugin is starting to run.");

  const authStore = useAuthStore();

  // This check is crucial. Does your browser have access to localStorage?
  if (import.meta.client) {
    console.log("2. Running on the client side.");

    // First, let's see what's in localStorage BEFORE we do anything.
    const tokenFromStorage = localStorage.getItem("access-token");
    console.log("3. Token in localStorage:", tokenFromStorage);

    // Now, run the action.
    authStore.loadInitialState();

    // AFTER running the action, is the token in the store?
    console.log("4. Token in Pinia store after load:", authStore.accessToken);

    if (authStore.accessToken) {
      console.log("5. ✅ Token exists in store! Attempting to fetch user...");
      try {
        await authStore.fetchUser();
        console.log("6. ✅ User fetch completed.");
      } catch (e) {
        console.error("6. ❌ User fetch FAILED.", e);
      }
    } else {
      console.log("5. ❌ No access token in the store. Skipping user fetch.");
    }
  } else {
    console.log(
      "2. Running on the server side. Plugin will not execute logic."
    );
  }
});
