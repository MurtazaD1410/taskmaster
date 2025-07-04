<script setup>
import { ref, onMounted } from "vue";
import { useIntersectionObserver } from "@vueuse/core";

// --- Hero Animation Logic ---
// We'll add a class after the component has mounted to trigger the entry animation.
const isMounted = ref(false);
onMounted(() => {
  // Use a short timeout to ensure elements are rendered before we start the transition.
  setTimeout(() => {
    isMounted.value = true;
  }, 100);
});

// --- Features Animation Logic ---
// We'll use an Intersection Observer to detect when the features section is visible.
const featuresSection = ref(null);
const featuresVisible = ref(false);

useIntersectionObserver(
  featuresSection,
  ([{ isIntersecting }]) => {
    // When the section intersects with the viewport, set the flag to true.
    // We only want this to trigger once.
    if (isIntersecting && !featuresVisible.value) {
      featuresVisible.value = true;
    }
  },
  // Options: Trigger when 10% of the element is visible.
  { threshold: 0.1 }
);

// Define the features data to keep the template clean.
const features = [
  {
    icon: "i-heroicons-cursor-arrow-rays",
    title: "Intuitive Interface",
    description:
      "An interface so simple, it gets out of your way. Drag, drop, and get things done with zero friction.",
  },
  {
    icon: "i-heroicons-bolt",
    title: "Blazing Fast",
    description:
      "Built for speed. Navigate, create, and complete tasks in milliseconds, not seconds.",
  },
  {
    icon: "i-lucide-sun",
    title: "Light & Dark Modes",
    description:
      "Work comfortably at any time of day. Your eyes will thank you for it.",
  },
];
</script>

<template>
  <div>
    <!-- ================================================================= -->
    <!-- HERO SECTION                                                      -->
    <!-- ================================================================= -->
    <UContainer class="py-24 sm:py-32">
      <div class="text-center max-w-3xl mx-auto">
        <!-- Animated Headline -->
        <h1
          class="text-5xl md:text-6xl font-bold tracking-tight text-gray-900 dark:text-white transition-all duration-700 ease-out"
          :class="
            isMounted ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'
          "
        >
          Conquer Your Tasks.
          <span class="text-primary">Find Your Focus.</span>
        </h1>

        <!-- Animated Sub-headline -->
        <p
          class="mt-6 text-lg md:text-xl leading-8 text-gray-600 dark:text-gray-300 transition-all duration-700 ease-out delay-300"
          :class="
            isMounted ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'
          "
        >
          TaskMaster is the simple yet powerful way to organize your work,
          manage your projects, and reclaim your peace of mind.
        </p>

        <!-- Animated Buttons -->
        <div
          class="mt-10 flex items-center justify-center gap-x-6 transition-all duration-700 ease-out delay-500"
          :class="
            isMounted ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'
          "
        >
          <UButton to="/register" size="xl" label="Get Started for Free" />
          <UButton
            to="#features"
            size="xl"
            color="white"
            variant="link"
            label="Learn More"
            trailing-icon="i-heroicons-arrow-right"
          />
        </div>
      </div>
    </UContainer>

    <!-- ================================================================= -->
    <!-- FEATURES SECTION                                                  -->
    <!-- ================================================================= -->
    <div
      id="features"
      ref="featuresSection"
      class="py-24 sm:py-32 bg-gray-50 dark:bg-gray-900/50"
    >
      <UContainer>
        <!-- Section Header -->
        <div class="max-w-2xl mx-auto text-center">
          <h2
            class="text-3xl font-bold tracking-tight text-gray-900 dark:text-white"
          >
            Everything you need. Nothing you don't.
          </h2>
          <p class="mt-4 text-lg text-gray-600 dark:text-gray-400">
            TaskMaster is designed with powerful features to boost your
            productivity.
          </p>
        </div>

        <!-- Features Grid -->
        <div class="mt-16 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          <UCard
            v-for="(feature, index) in features"
            :key="feature.title"
            class="transition-all duration-500 ease-out"
            :class="
              featuresVisible
                ? 'opacity-100 translate-y-0'
                : 'opacity-0 translate-y-8'
            "
            :style="{ transitionDelay: `${index * 150}ms` }"
          >
            <div class="flex flex-col items-center text-center">
              <UIcon :name="feature.icon" class="text-4xl text-primary" />
              <h3 class="mt-4 text-xl font-bold text-gray-900 dark:text-white">
                {{ feature.title }}
              </h3>
              <p class="mt-2 text-base text-gray-600 dark:text-gray-300">
                {{ feature.description }}
              </p>
            </div>
          </UCard>
        </div>
      </UContainer>
    </div>

    <!-- ================================================================= -->
    <!-- FINAL CTA SECTION                                                 -->
    <!-- ================================================================= -->
    <div class="py-24 sm:py-32">
      <UContainer class="text-center">
        <h2
          class="text-4xl font-bold tracking-tight text-gray-900 dark:text-white"
        >
          Ready to take control?
        </h2>
        <p class="mt-4 text-lg text-gray-600 dark:text-gray-400">
          Start organizing your life today. It's free forever.
        </p>
        <div class="mt-8">
          <UButton to="/register" size="xl" label="Sign Up Now" />
        </div>
      </UContainer>
    </div>
  </div>
</template>

<style scoped>
/* Optional: For smoother scrolling when clicking "Learn More" */
html {
  scroll-behavior: smooth;
}
</style>
