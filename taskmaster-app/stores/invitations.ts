import { defineStore } from "pinia";
import type { Invitation } from "~/types/types";

const toast = useToast();

export const useInvitationStore = defineStore("invitations", {
  state: () => ({
    invitations: null as Invitation[] | null,
    pending: false,
    error: null as string | null,
  }),
  getters: {
    count: (state) => state.invitations?.length || 0,
  },

  actions: {
    async fetchInvitations() {
      const authStore = useAuthStore();

      // A crucial guard clause: do not attempt to fetch if the user is not logged in.
      if (!authStore.isLoggedIn) {
        // You can clear the state here to be safe
        this.invitations = [];
        return;
      }

      // Set the 'pending' state to true, just like useAsyncData does.
      this.pending = true;
      this.error = null; // Clear previous errors
      const { $api } = useNuxtApp();

      try {
        // The API call is the same.
        const data = await $api<Invitation[]>("/invitations/pending/");
        // On success, update the state.
        this.invitations = data;
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
      } catch (e: any) {
        // On error, update the error state.
        this.error = e;
        console.error("Failed to fetch pending invitations:", e);
      } finally {
        // Finally, set 'pending' back to false.
        this.pending = false;
      }
    },

    async acceptInvitation(invitation: Invitation) {
      const { $api } = useNuxtApp();

      try {
        // The API call is the same.
        await $api("/invitations/accept/", {
          method: "POST",
          body: { token: invitation.token },
        });

        // On success, the most important step is to refresh the state.
        // This will automatically remove the accepted invitation from the list.
        await this.fetchInvitations();
      } catch (error) {
        // It's good practice for store actions to re-throw the error
        // so the component that called it knows something went wrong
        console.error("Failed to accept invitation:", error);
        throw error;
      }
    },

    async declineInvitation(invitation: Invitation) {
      const { $api } = useNuxtApp();

      try {
        // The API call is the same.
        await $api("/invitations/decline/", {
          method: "POST",
          body: { token: invitation.token },
        });

        // On success, the most important step is to refresh the state.
        // This will automatically remove the accepted invitation from the list.
        await this.fetchInvitations();
      } catch (error) {
        // It's good practice for store actions to re-throw the error
        // so the component that called it knows something went wrong
        console.error("Failed to decline invitation:", error);
        throw error;
      }
    },
  },
});
