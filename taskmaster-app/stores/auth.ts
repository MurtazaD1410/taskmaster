import { defineStore } from "pinia";
import type { User } from "~/types/types";

export const useAuthStore = defineStore("auth", {
  // The state is a function that returns the initial state
  state: () => ({
    accessToken: null as string | null,
    refreshToken: null as string | null,
    user: null as User | null,
  }),

  // Getters are like computed properties for your store
  getters: {
    isLoggedIn: (state) => !!state.accessToken,
  },

  // Actions are functions that can be called to modify the state
  // actions: {
  //   loadInitialState() {
  //     console.log("inside init");
  //     if (import.meta.client) {
  //       this.accessToken = localStorage.getItem("access-token");
  //       this.refreshToken = localStorage.getItem("refresh-token");
  //     }
  //   },

  //   setLoginData(loginResponse: {
  //     user: User;
  //     tokens: { access: string; refresh: string };
  //   }) {
  //     this.user = loginResponse.user;
  //     this.accessToken = loginResponse.tokens.access;
  //     this.refreshToken = loginResponse.tokens.refresh;

  //     if (import.meta.client) {
  //       localStorage.setItem("access-token", loginResponse.tokens.access);
  //       localStorage.setItem("refresh-token", loginResponse.tokens.refresh);
  //     }
  //   },

  //   async refreshAccessToken() {
  //     if (!this.refreshToken) {
  //       throw new Error("No refresh token available.");
  //     }
  //     try {
  //       const response = await $fetch<{ access: string }>("/api/auth/refresh", {
  //         method: "POST",
  //         body: { refreshToken: this.refreshToken },
  //       });

  //       // ✅ CRUCIAL: Are you doing this?
  //       // Update the store and localStorage with the NEW token.
  //       this.accessToken = response.access; // 'access' should match your Django response key
  //       localStorage.setItem("access-token", response.access);

  //       return response.access;
  //     } catch (error) {
  //       console.error("Failed to refresh token, logging out.", error);
  //       this.logout();
  //       throw new Error("Refresh failed, user logged out.");
  //     }
  //   },

  //   async fetchUser() {
  //     // If there's no token, we can't fetch a user.
  //     if (!this.accessToken) {
  //       return;
  //     }

  //     const { $api } = useNuxtApp();

  //     try {
  //       // Use the custom $api instance to make the call.
  //       // It will automatically add the Authorization header.
  //       const user = await $api<User>("auth/me"); // Calls /api/auth/me
  //       this.user = user;
  //     } catch (error) {
  //       console.error("Failed to fetch user with token, logging out.", error);

  //       this.logout();
  //     }
  //   },

  //   logout() {
  //     this.accessToken = null;
  //     this.refreshToken = null;
  //     this.user = null;
  //     // removing from local storage
  //     localStorage.removeItem("access-token");
  //     localStorage.removeItem("refresh-token");

  //     navigateTo("/login");
  //   },
  // },
  actions: {
    // ✅ GUARDED
    loadInitialState() {
      if (import.meta.client) {
        this.accessToken = localStorage.getItem("access-token");
        this.refreshToken = localStorage.getItem("refresh-token");
      }
    },

    // ✅ GUARDED
    setLoginData(loginResponse: {
      user: User;
      tokens: { access: string; refresh: string };
    }) {
      this.user = loginResponse.user;
      this.accessToken = loginResponse.tokens.access;
      this.refreshToken = loginResponse.tokens.refresh;

      if (import.meta.client) {
        localStorage.setItem("access-token", loginResponse.tokens.access);
        localStorage.setItem("refresh-token", loginResponse.tokens.refresh);
      }
    },

    // ✅ GUARDED
    async refreshAccessToken() {
      if (!this.refreshToken) {
        throw new Error("No refresh token available.");
      }
      try {
        const response = await $fetch<{ access: string }>("/api/auth/refresh", {
          method: "POST",
          body: { refreshToken: this.refreshToken },
        });

        this.accessToken = response.access;
        if (import.meta.client) {
          localStorage.setItem("access-token", response.access);
        }
        return response.access;
      } catch (error) {
        console.error("Failed to refresh token, logging out.");
        this.logout();
        throw new Error("Refresh failed, user logged out.");
      }
    },

    // ✅ GUARDED
    logout() {
      this.accessToken = null;
      this.refreshToken = null;
      this.user = null;

      if (import.meta.client) {
        localStorage.removeItem("access-token");
        localStorage.removeItem("refresh-token");
        // Redirect on the client side
        navigateTo("/login");
      }
    },

    // fetchUser does not need guards as it only deals with API calls and state.
    async fetchUser() {
      if (!this.accessToken) return;
      const { $api } = useNuxtApp();
      try {
        this.user = await $api<User>("/auth/me");
      } catch (error) {
        console.error("Error fetching user:", error);
        this.logout();
      }
    },
  },
});
