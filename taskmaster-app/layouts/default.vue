<script setup lang="ts">
import { useAuthStore } from "~/stores/auth";
import { storeToRefs } from "pinia";
import { ClientOnly } from "#components";
import { ref, onMounted, onUnmounted } from "vue";

const authStore = useAuthStore();
const invitationStore = useInvitationStore();
const route = useRoute();

const { user } = storeToRefs(authStore);
const { isLoggedIn } = storeToRefs(authStore);
const isScrolled = ref(false);
const mobileMenuOpen = ref(false);

const toggleMobileMenu = () => {
  mobileMenuOpen.value = !mobileMenuOpen.value;
};

// 3. Define the function that will handle the scroll event
const handleScroll = () => {
  // If window.scrollY is greater than 0, set isScrolled to true
  isScrolled.value = window.scrollY > 0;
};

// 4. Add and remove the event listener safely
onMounted(() => {
  window.addEventListener("scroll", handleScroll);
});

onUnmounted(() => {
  window.removeEventListener("scroll", handleScroll);
});
async function handleLogout() {
  authStore.logout();

  navigateTo("/login");
}

const isActive = (path: string) => {
  return route.path.startsWith(path);
};

const { count } = storeToRefs(invitationStore);

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
</script>

<template>
  <div
    class="bg-white dark:bg-gray-900 text-gray-900 dark:text-white min-h-screen flex flex-col"
  >
    <!-- HEADER -->
    <header
      :class="[
        'sticky top-0 z-30 transition-all duration-300 ',
        isScrolled
          ? 'bg-white/75 dark:bg-gray-900/75 backdrop-blur-[2px] border-b border-gray-200 dark:border-gray-800'
          : 'bg-gray-100 dark:bg-gray-800 border-b border-transparent',
      ]"
    >
      <UContainer
        class="flex items-center justify-between h-16 px-4 sm:px-8 max-w-[1440px] w-full mx-auto"
      >
        <!-- logo and site -->
        <NuxtLink to="/" class="flex items-center gap-2">
          <UIcon
            name="i-heroicons-clipboard-document-check"
            class="text-3xl text-primary"
          />
          <span class="text-xl font-bold">TaskMaster</span>
        </NuxtLink>

        <!-- navlinks -->
        <nav class="hidden md:flex items-center gap-4">
          <ThemeToggle />
          <template v-if="isLoggedIn">
            <ClientOnly>
              <UChip :text="count" size="3xl">
                <UButton
                  icon="i-heroicons-bell-alert"
                  class="w-8 h-8 flex items-center justify-center text-xl"
                  variant="outline"
                  :color="isActive('/invitations') ? 'primary' : 'neutral'"
                  @click="navigateTo('/invitations')"
                />
              </UChip>
              <NuxtLink
                to="/tasks"
                :class="[
                  isActive('/tasks')
                    ? 'text-primary dark:text-primary-400'
                    : 'text-gray-500 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white',
                ]"
                >Tasks</NuxtLink
              >
              <NuxtLink
                to="/projects"
                :class="[
                  isActive('/projects')
                    ? 'text-primary dark:text-primary-400'
                    : 'text-gray-500 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white',
                ]"
              >
                Projects
              </NuxtLink>
              <NuxtLink
                to="/profile"
                :class="[
                  isActive('/profile')
                    ? 'text-primary dark:text-primary-400 font-bold'
                    : 'text-gray-500 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white font-bold',
                ]"
              >
                {{ authStore.user?.username }}
              </NuxtLink>
            </ClientOnly>

            <button
              class="text-gray-700 dark:text-gray-300 hover:text-primary"
              @click="handleLogout"
            >
              Logout
            </button>
          </template>

          <template v-else>
            <ClientOnly>
              <NuxtLink
                to="/login"
                :class="[
                  isActive('/login')
                    ? 'text-primary dark:text-primary-400'
                    : 'text-gray-500 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white',
                ]"
                >Login</NuxtLink
              >
              <NuxtLink
                to="/register"
                :class="[
                  isActive('/register')
                    ? 'text-primary dark:text-primary-400'
                    : 'text-gray-500 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white',
                ]"
                >Register</NuxtLink
              >
            </ClientOnly>
          </template>
        </nav>
        <button
          class="md:hidden text-gray-700 dark:text-gray-300 focus:outline-none"
          @click="toggleMobileMenu"
        >
          <UIcon name="i-heroicons-bars-3" class="w-6 h-6" />
        </button>
      </UContainer>
      <ClientOnly>
        <div
          v-if="mobileMenuOpen"
          class="md:hidden bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700 px-4 pb-4"
        >
          <ThemeToggle class="my-4" />
          <template v-if="isLoggedIn">
            <div class="flex flex-col gap-4">
              <ClientOnly>
                <NuxtLink
                  to="/tasks"
                  :class="[
                    isActive('/tasks')
                      ? 'text-primary dark:text-primary-400'
                      : 'text-gray-500 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white',
                  ]"
                  @click="mobileMenuOpen = false"
                  >Tasks</NuxtLink
                >
                <NuxtLink
                  to="/projects"
                  :class="[
                    isActive('/projects')
                      ? 'text-primary dark:text-primary-400'
                      : 'text-gray-500 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white',
                  ]"
                  @click="mobileMenuOpen = false"
                >
                  Projects
                </NuxtLink>
                <NuxtLink
                  to="/profile"
                  :class="[
                    isActive('/profile')
                      ? 'text-primary dark:text-primary-400'
                      : 'text-gray-500 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white',
                  ]"
                  @click="mobileMenuOpen = false"
                >
                  Profile
                </NuxtLink>
              </ClientOnly>
            </div>

            <button
              class="text-gray-700 dark:text-gray-300 hover:text-primary my-4"
              @click="
                () => {
                  mobileMenuOpen = false;
                  handleLogout();
                }
              "
            >
              Logout
            </button>
          </template>

          <template v-else>
            <div class="flex flex-col gap-4">
              <ClientOnly>
                <NuxtLink
                  to="/login"
                  :class="[
                    isActive('/login')
                      ? 'text-primary dark:text-primary-400'
                      : 'text-gray-500 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white',
                  ]"
                  @click="mobileMenuOpen = false"
                  >Login</NuxtLink
                >
                <NuxtLink
                  to="/register"
                  :class="[
                    isActive('/register')
                      ? 'text-primary dark:text-primary-400'
                      : 'text-gray-500 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white',
                  ]"
                  @click="mobileMenuOpen = false"
                  >Register</NuxtLink
                >
              </ClientOnly>
            </div>
          </template>
        </div>
      </ClientOnly>
    </header>

    <!-- MAIN CONTENT -->
    <main class="flex-1 px-4 sm:px-8 max-w-[1440px] w-full mx-auto">
      <slot />
    </main>

    <!-- FOOTER -->
    <footer
      class="bg-gray-100 dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700"
    >
      <UContainer
        class="text-center py-4 px-4 sm:px-8 max-w-[1440px] w-full mx-auto"
      >
        <p class="text-sm text-gray-500">
          &copy; {{ new Date().getFullYear() }} TaskMaster. All rights reserved.
        </p>
      </UContainer>
    </footer>
  </div>
</template>
