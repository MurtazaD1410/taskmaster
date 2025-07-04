<script setup lang="ts">
import * as z from "zod";
import type { FormSubmitEvent } from "@nuxt/ui";
import { ref } from "vue";
import { useAuthStore } from "~/stores/auth";

const authStore = useAuthStore();

if (authStore.isLoggedIn) {
  navigateTo("/tasks");
}

const schema = z.object({
  email: z.string().email("Invalid email"),
  password: z.string().min(8, "Password must be at least 8 characters"),
});

type Schema = z.infer<typeof schema>;

const state = reactive<Partial<Schema>>({
  email: undefined,
  password: undefined,
});

// --- NEW STATE ---
// Create a reactive reference to hold the visibility state.
// It starts as false (password hidden).
const isPasswordVisible = ref(false);

function togglePasswordVisibility() {
  isPasswordVisible.value = !isPasswordVisible.value;
}

const toast = useToast();
const { $api } = useNuxtApp();
const router = useRouter();

async function onSubmit(event: FormSubmitEvent<Schema>) {
  try {
    const response = await $api("auth/login/", {
      method: "POST",
      body: event.data,
    });
    toast.add({ title: "Login Successful!", color: "success" });
    console.log(response);
    authStore.setLoginData({
      user: response.user,
      tokens: {
        access: response.tokens.access,
        refresh: response.tokens.refresh,
      },
    });

    await router.push("/tasks");
  } catch (error) {
    toast.add({
      title: "Login Failed",
      description:
        // @ts-expect-error unknown type
        Object.values(error.response._data)[0][0] || "Please check credentials",
      color: "error",
    });
  }
}
</script>

<template>
  <UContainer
    class="flex h-[calc(100vh-120px)] items-center justify-center py-12"
  >
    <!-- UCard provides tcd he nice-looking card with a border and background -->
    <UCard class="w-full max-w-sm bg-gray-100 dark:bg-gray-800 rounded-md">
      <!-- The #header slot is for the title of the card -->
      <template #header>
        <h1 class="text-2xl font-bold text-center">Login to TaskMaster</h1>
      </template>

      <!-- UForm helps manage the form state and submission -->
      <UForm
        ref="form"
        :validate-on="['change']"
        :schema="schema"
        :state="state"
        class="space-y-4"
        @submit="onSubmit"
      >
        <UFormField name="email" label="Email" :ui="{ error: false }">
          <UInput
            v-model="state.email"
            class="w-full"
            size="lg"
            placeholder="Enter your email"
            icon="i-heroicons-envelope"
          />
        </UFormField>
        <UFormField label="Password" name="password">
          <div class="relative w-full">
            <UInput
              v-model="state.password"
              class="w-full"
              size="lg"
              placeholder="Enter your password"
              leading-icon="i-heroicons-lock-closed"
              :type="isPasswordVisible ? 'text' : 'password'"
            >
              <button
                type="button"
                class="absolute right-2 top-1/2 flex justify-center items-center transform -translate-y-1/2 text-gray-500 w-6 h-6 hover:text-gray-700"
                aria-label="Toggle password visibility"
                @click="togglePasswordVisibility"
              >
                <UIcon
                  class="text-lg text-gray-400 dark:text-gray-400"
                  :name="
                    isPasswordVisible
                      ? 'i-heroicons-eye-slash'
                      : 'i-heroicons-eye'
                  "
                />
              </button>
            </UInput>
          </div>
        </UFormField>

        <UButton type="submit" block class="mt-2" size="lg">Login</UButton>
      </UForm>
    </UCard>
  </UContainer>
</template>
