<script setup lang="ts">
import { UAvatar, UInput, UTextarea } from "#components";
import type { FormSubmitEvent } from "@nuxt/ui";
import { z } from "zod";
import { formatDate } from "~/helpers/utils";
import type { UserDetail } from "~/types/types";

const toast = useToast();

const schema = z.object({
  first_name: z
    .string()
    .max(50, "First name must be less than 50 characters")
    .optional(),
  last_name: z
    .string()
    .max(50, "Last name must be less than 50 characters")
    .optional(),
  bio: z.string().optional(),
  avatar: z.any().optional(),
});

type Schema = z.infer<typeof schema>;

const isModalOpen = ref(false);
const previewAvatar = ref<string | null>(null);
const editingUser = ref<UserDetail | null>(null);

const { $api } = useNuxtApp();
const {
  data: user,
  pending,
  error,
  refresh,
} = useAsyncData<UserDetail>(
  () => `user`,
  () => $api(`auth/profile`),

  {
    server: false,
  }
);

function handleFileUpload(event: Event) {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];
  if (!file) return;
  state.avatar = file;
}

const state = reactive<Partial<Schema>>({
  avatar: user.value?.avatar,
  bio: user.value?.bio,
  first_name: user.value?.first_name,
  last_name: user.value?.last_name,
});

function openUserEditModal(user: UserDetail) {
  console.log(user);
  editingUser.value = user; // Clear any previous editing state
  // Reset form state for a new task
  state.first_name = user.first_name || "";
  state.last_name = user.last_name || "";
  state.bio = user.bio || "";
  state.avatar = user.avatar || undefined;

  isModalOpen.value = true;
}

const items = computed(() => {
  if (!user.value) {
    return [
      [
        {
          label: "Loading...",
          icon: "i-heroicons-arrow-path",
        },
      ],
    ];
  }

  return [
    [
      {
        label: user.value?.username,
        icon: "i-heroicons-briefcase",
        type: "label",
        class: "font-semibold",
      },
    ],
    [
      {
        label: "Edit",
        icon: "i-heroicons-pencil",
        onSelect() {
          openUserEditModal(user.value!);
        },
      },
      {
        label: "Delete",
        icon: "i-heroicons-trash",
        color: "error",
        onSelect() {},
      },
    ],
  ];
});

function onAvatarChange(event: Event) {
  const file = (event.target as HTMLInputElement).files?.[0];
  if (file) {
    state.avatar = file;
    previewAvatar.value = URL.createObjectURL(file);
  }
}

async function saveProfile(event: FormSubmitEvent<Schema>) {
  console.log(event.data);
  try {
    const formData = new FormData();
    formData.append("first_name", event.data.first_name || "");
    formData.append("last_name", event.data.last_name || "");
    formData.append("bio", event.data.bio || "");

    if (event.data.avatar instanceof File) {
      formData.append("avatar", event.data.avatar);
    }

    await $api(`auth/profile/`, {
      method: "PUT",
      body: formData,
    });
    toast.add({ title: "Profile updated Successfully!", color: "success" });

    isModalOpen.value = false;
    previewAvatar.value = null;
    await refresh();
  } catch (error) {
    // @ts-expect-error error is type unknown
    const errorData = error?.response?._data;
    const errorMessage = errorData
      ? Object.values(errorData).flat().join(" ")
      : "An unknown error occurred.";
    toast.add({
      title: "An error occurred",
      description: errorMessage,
      color: "error",
    });
  }
}

async function deleteUser() {
  if (!confirm("Are you sure you want to delete this task?")) return;

  try {
    await $api(`auth/profile/`, {
      method: "DELETE",
    });
    isModalOpen.value = false;
    toast.add({ title: "Profile deleted Successfully!", color: "success" });
    navigateTo("/");
  } catch (error) {
    // @ts-expect-error error is type unknown
    const errorData = error?.response?._data;
    const errorMessage = errorData
      ? Object.values(errorData).flat().join(" ")
      : "An unknown error occurred.";
    toast.add({
      title: "Could not delete Profile",
      description: errorMessage,
      color: "error",
    });
  }
}
</script>

<template>
  <UContainer class="py-12">
    <div class="flex justify-center mb-3">
      <h1 class="text-2xl md:text-4xl font-bold">Profile</h1>
    </div>
    <div v-if="pending" class="text-center py-16">
      <UIcon name="i-heroicons-arrow-path" class="text-4xl animate-spin" />
    </div>
    <div v-else-if="error" class="text-center py-16 text-red-500">
      Failed to load profile.
    </div>
    <div v-else-if="user">
      <UCard class="relative">
        <UDropdownMenu
          class="absolute top-2 right-2"
          :items="items"
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
        <div class="flex flex-col gap-2 items-center justify-center">
          <UAvatar :src="user.avatar" :alt="user.username" class="w-28 h-28" />
          <div class="flex flex-col items-center justify-center">
            <p class="font-semibold text-xl">
              {{ user.username }}
              <span class="text-muted italic text-xs font-normal"
                >Joined ({{ formatDate(user.created_at) }})</span
              >
            </p>
            <p class="text-muted">{{ user.email }}</p>
          </div>
          <div class="">
            <div v-if="user.first_name || user.last_name" class="flex gap-2">
              <p class="text-lg font-bold uppercase">
                {{ user.first_name }}
              </p>
              <p class="text-lg lowercase italic">{{ user.last_name }}</p>
            </div>
            <div v-else>
              <p class="font-light text-muted italic text-sm">
                Edit to enter your full name
              </p>
            </div>
          </div>
          <p
            v-if="user.bio"
            class="text-center dark:text-gray-300 text-gray-700"
          >
            {{ user.bio }}
          </p>
          <p v-else class="font-light text-muted italic text-sm">
            Add your bio.
          </p>
        </div>
      </UCard>
    </div>
    <UModal
      v-model:open="isModalOpen"
      title="Edit Project"
      :ui="{ footer: 'justify-end' }"
    >
      <template #body>
        <UForm
          :schema="schema"
          :state="state"
          class="space-y-4"
          @submit="saveProfile"
        >
          <UFormField label="Avatar" name="avatar">
            <div class="flex flex-col items-center gap-2 w-full">
              <label for="avatarInput" class="cursor-pointer group relative">
                <UAvatar
                  :src="previewAvatar || state.avatar"
                  :alt="user?.username"
                  class="rounded-full w-24 h-24 object-cover border transition duration-200 group-hover:brightness-75"
                />
                <div
                  class="absolute inset-0 flex items-center justify-center text-white text-sm opacity-0 group-hover:opacity-100 transition"
                >
                  Change
                </div>
              </label>

              <input
                id="avatarInput"
                type="file"
                accept="image/*"
                class="hidden"
                @change="onAvatarChange"
              />
            </div>
          </UFormField>

          <UFormField label="First name" name="first_name">
            <UInput v-model="state.first_name" class="w-full" />
          </UFormField>
          <UFormField label="Last name" name="last_name">
            <UInput v-model="state.last_name" class="w-full" />
          </UFormField>
          <UFormField label="Bio" name="bio">
            <UTextarea
              v-model="state.bio"
              class="w-full"
              autoresize
              :rows="6"
            />
          </UFormField>

          <div class="flex justify-end gap-3 pt-4">
            <UButton
              label="Cancel"
              color="neutral"
              variant="outline"
              icon="i-heroicons-x-mark"
              @click="
                () => {
                  isModalOpen = false;
                  previewAvatar = null;
                }
              "
            />
            <UButton type="submit" label="Save" icon="i-heroicons-check" />
          </div>
        </UForm>
      </template>
    </UModal>
  </UContainer>
</template>
