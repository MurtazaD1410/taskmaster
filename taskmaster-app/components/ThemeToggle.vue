<template>
  <USwitch
    v-model="isDark"
    checked-icon="i-heroicons-outline-moon"
    unchecked-icon="i-heroicons-outline-sun"
  />
</template>

<script setup lang="ts">
const { theme, setTheme } = useTheme();

// v-model works with a boolean, so map it
const isDark = computed({
  get: () => theme.value === "dark",
  set: (val: boolean) => setTheme(val ? "dark" : "light"),
});
</script>
