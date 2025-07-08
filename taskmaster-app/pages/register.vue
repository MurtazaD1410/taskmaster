<script setup lang="ts">
import * as z from "zod";
import type { FormSubmitEvent } from "@nuxt/ui";
import { useAuthStore } from "~/stores/auth";

const authStore = useAuthStore();

if (authStore.isLoggedIn) {
  navigateTo("/tasks");
}

const schema = z
  .object({
    username: z.string().min(1, "Username is required"),
    email: z.string().email("Invalid email"),
    password: z.string().min(8, "Password must be at least 8 characters"),
    confirm_password: z
      .string()
      .min(8, "Confirm Password must be at least 8 characters"),
    // first_name: z.string().min(1, "First name is required"),
    // last_name: z.string().min(1, "Last name is required"),
  })
  .refine((data) => data.password === data.confirm_password, {
    message: "Passwords do not match",
    path: ["confirm_password"],
  });

type Schema = z.infer<typeof schema>;

const state = reactive<Partial<Schema>>({
  email: undefined,
  password: undefined,
  confirm_password: undefined,
  // first_name: undefined,
  // last_name: undefined,
  username: undefined,
});

// --- NEW STATE ---
// Create a reactive reference to hold the visibility state.
// It starts as false (password hidden).
const isPasswordVisible = ref(false);
const isConfirmPasswordVisible = ref(false);

function togglePasswordVisibility() {
  isPasswordVisible.value = !isPasswordVisible.value;
}

function toggleConfirmPasswordVisibility() {
  isConfirmPasswordVisible.value = !isConfirmPasswordVisible.value;
}

const toast = useToast();
const { $api } = useNuxtApp();
const router = useRouter();

async function onSubmit(event: FormSubmitEvent<Schema>) {
  try {
    const response = await $api("auth/register/", {
      method: "POST",
      body: {
        email: event.data.email,
        username: event.data.username,
        password: event.data.password,
        password2: event.data.confirm_password,
      },
    });
    toast.add({ title: "Registration Successful!", color: "success" });
    console.log(response);

    await authStore.setLoginData({
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
        Object.values(error.response._data)[0][0] || "Registration failed",
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
        <h1 class="text-2xl font-bold text-center">Register to TaskMaster</h1>
      </template>

      <!-- UForm helps manage the form state and submission -->
      <UForm
        :schema="schema"
        :state="state"
        class="space-y-4"
        @submit="onSubmit"
      >
        <UFormField label="Username" name="username" required>
          <UInput
            v-model="state.username"
            class="w-full"
            size="lg"
            placeholder="Enter your username"
            icon="i-heroicons-user-circle"
          />
        </UFormField>
        <UFormField label="Email" name="email" required>
          <UInput
            v-model="state.email"
            class="w-full"
            size="lg"
            placeholder="Enter your email"
            icon="i-heroicons-envelope"
          />
        </UFormField>

        <UFormField label="Password" name="password" required>
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
        <UFormField label="Confirm Password" name="confirm_password" required>
          <div class="relative w-full">
            <UInput
              v-model="state.confirm_password"
              class="w-full"
              size="lg"
              placeholder="Re-enter your password"
              leading-icon="i-heroicons-shield-check"
              :type="isConfirmPasswordVisible ? 'text' : 'password'"
            >
              <button
                type="button"
                class="absolute right-2 top-1/2 flex justify-center items-center transform -translate-y-1/2 text-gray-500 w-6 h-6 hover:text-gray-700"
                aria-label="Toggle password visibility"
                @click="toggleConfirmPasswordVisibility"
              >
                <UIcon
                  class="text-lg text-gray-400 dark:text-gray-400"
                  :name="
                    isConfirmPasswordVisible
                      ? 'i-heroicons-eye-slash'
                      : 'i-heroicons-eye'
                  "
                />
              </button>
            </UInput>
          </div>
        </UFormField>

        <UButton type="submit" block size="lg" class="mt-2">Register</UButton>
        <p class="text-sm text-muted text-center">
          Already have an account?
          <router-link to="/login" class="text-primary-500">Login</router-link>
        </p>
      </UForm>
    </UCard>
  </UContainer>
</template>
