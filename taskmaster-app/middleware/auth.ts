import { useAuthStore } from "~/stores/auth";

export default defineNuxtRouteMiddleware(async (to) => {
  // We don't need to do anything on the server-side, because our `auth` plugin
  // will run first and handle fetching the user. The initial state will be
  // determined by the time the app hydrates on the client.
  if (import.meta.server) {
    return;
  }

  const authStore = useAuthStore();
  const publicRoutes = ["/login", "/register", "/"]; // Routes that don't require login

  // If the user's state is not yet loaded, the `auth` plugin is likely still running.
  // We can wait for it, but for now, we'll rely on it completing before navigation.
  // The crucial check happens when the app is mounted on the client.

  if (!authStore.isLoggedIn && !publicRoutes.includes(to.path)) {
    console.log("Middleware: User not logged in, redirecting to /login");
    // ✅ MUST return navigateTo to stop the original navigation.
    return navigateTo("/login");
  }
});
