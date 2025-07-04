<script setup>
import { useAuthStore } from "~/stores/auth";
import { storeToRefs } from "pinia";
import { ClientOnly } from "#components";
import { ref, onMounted, onUnmounted } from "vue";

const authStore = useAuthStore();
const route = useRoute();

const { isLoggedIn } = storeToRefs(authStore);
const isScrolled = ref(false);

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

const isActive = (path) => {
  return route.path.startsWith(path);
};
</script>

<template>
  <div
    class="bg-white dark:bg-gray-900 text-gray-900 dark:text-white min-h-screen flex flex-col"
  >
    <!-- HEADER -->
    <header
      :class="[
        'sticky top-0 z-30 transition-all duration-300',
        isScrolled
          ? 'bg-white/75 dark:bg-gray-900/75 backdrop-blur-xs border-b border-gray-200 dark:border-gray-800'
          : 'bg-gray-100 dark:bg-gray-800 border-b border-transparent',
      ]"
    >
      <UContainer
        class="flex items-center justify-between h-16 px-4 sm:px-8 md:px-12 max-w-7xl w-full mx-auto"
      >
        <!-- logo and site -->
        <NuxtLink to="/" class="flex items-center gap-2">
          <UIcon name="i-heroicons-check-badge" class="text-2xl text-primary" />
          <span class="text-xl font-bold">TaskMaster</span>
        </NuxtLink>

        <!-- navlinks -->
        <nav class="flex items-center gap-4">
          <ThemeToggle />
          <template v-if="isLoggedIn">
            <ClientOnly>
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
      </UContainer>
    </header>

    <!-- MAIN CONTENT -->
    <main class="flex-1 px-4 sm:px-8 md:px-12 max-w-7xl w-full mx-auto">
      <slot />
    </main>

    <!-- FOOTER -->
    <footer
      class="bg-gray-100 dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700"
    >
      <UContainer
        class="text-center py-4 px-4 sm:px-8 md:px-12 max-w-7xl w-full mx-auto"
      >
        <p class="text-sm text-gray-500">
          &copy; {{ new Date().getFullYear() }} TaskMaster. All rights reserved.
        </p>
      </UContainer>
    </footer>
  </div>
</template>
