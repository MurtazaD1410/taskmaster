<script setup lang="ts">
import type { Invitation } from "~/types/types";

const toast = useToast();
const { $api } = useNuxtApp();
const authStore = useAuthStore();
const { user } = storeToRefs(authStore);
const invitationStore = useInvitationStore();

const { invitations, pending, error } = storeToRefs(invitationStore);

// This watcher is the trigger.
watch(
  user,
  (newUser) => {
    if (newUser) {
      // When a user exists, tell the store to fetch the data.
      invitationStore.fetchInvitations();
    } else {
      // When the user logs out, clear the data.
      invitationStore.invitations = [];
    }
  },
  { immediate: true }
);

async function handleAccept(invitation: Invitation) {
  try {
    // await $api("invitations/accept/", {
    //   method: "POST",
    //   body: { token: invitation.token },
    // });
    await invitationStore.acceptInvitation(invitation);
    toast.add({ title: "Invitation accepted Successfully!", color: "success" });

    // await refresh();
  } catch (error) {
    toast.add({
      title: "An error occurred",
      description: (error as { detail: string }).detail,
      color: "error",
    });
  }
}

async function handleDecline(invitation: Invitation) {
  try {
    await invitationStore.declineInvitation(invitation);
    toast.add({ title: "Invitation declined Successfully!", color: "success" });
  } catch (error) {
    toast.add({
      title: "An error occurred",
      description: (error as { detail: string }).detail,
      color: "error",
    });
  }
}
</script>

<template>
  <UContainer class="py-12">
    <div class="flex justify-between items-center mb-8">
      <h1 class="text-4xl font-bold">My Invitations</h1>
    </div>

    <div v-if="pending" class="text-center py-16">
      <UIcon name="i-heroicons-arrow-path" class="text-4xl animate-spin" />
    </div>
    <div v-else-if="error" class="text-center py-16 text-red-500">
      Failed to load invitations.
    </div>
    <div
      v-else-if="!invitations || invitations.length === 0"
      class="text-center py-16 text-gray-500"
    >
      No invitations yet.
    </div>
    <div v-else class="flex flex-col">
      <UCard
        v-for="invitation in invitations"
        :key="invitation.id"
        class="cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors mb-3"
      >
        <div class="flex justify-between items-center">
          <div class="flex flex-col gap-2 flex-1">
            <!-- Main task info -->
            <div class="flex flex-col gap-1">
              <div class="flex gap-3 items-center">
                <span class="font-semibold text-lg">{{
                  invitation.project.title
                }}</span>
                <UBadge
                  :leading-icon="
                    invitation.status === 'D'
                      ? 'i-heroicons-x-circle'
                      : invitation.status === 'P'
                      ? 'i-heroicons-exclamation-circle'
                      : 'i-heroicons-check-circle'
                  "
                  size="lg"
                  class="capitalize"
                  :color="
                    invitation.status === 'D'
                      ? 'error'
                      : invitation.status === 'P'
                      ? 'warning'
                      : 'success'
                  "
                  variant="outline"
                >
                  {{ invitation.status === "D" ? "Declined" : "Pending" }}
                </UBadge>
              </div>
              <span class="font-light text-sm text-gray-600 dark:text-gray-400">
                {{ invitation.project.description }}
              </span>
            </div>
          </div>

          <!-- Status and dropdown -->
          <div
            class="ml-4 flex-shrink-0 flex flex-col gap-3 justify-center items-end"
          >
            <!-- Dropdown menu -->
            <UDropdownMenu
              :items="[
                {
                  label: 'Accept',
                  icon: 'i-heroicons-hand-thumb-up',
                  color: 'success',
                  onSelect: () => handleAccept(invitation),
                },
                {
                  label: 'Reject',
                  icon: 'i-heroicons-hand-thumb-down',
                  color: 'error',
                  onSelect: () => handleDecline(invitation),
                },
              ]"
              :content="{
                align: 'end',
                side: 'bottom',
                sideOffset: 8,
              }"
              :ui="{
                content: 'w-48',
              }"
            >
              <UButton
                icon="i-lucide-menu"
                color="neutral"
                variant="outline"
                size="lg"
                class="w-8 h-8"
              />
            </UDropdownMenu>
            <p class="text-muted text-sm">
              Invited by: {{ invitation.invited_by.username }}
            </p>
          </div>
        </div>
      </UCard>
    </div>
  </UContainer>
</template>
