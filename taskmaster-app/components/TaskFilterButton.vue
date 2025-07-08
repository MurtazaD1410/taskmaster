<script setup lang="ts">
type TabValue = "ALL" | "TODO" | "IN_PROGRESS" | "DONE";

const props = defineProps<{
  currentTab: "ALL" | "TODO" | "IN_PROGRESS" | "DONE";
}>();

const emit = defineEmits<{
  (e: "update:currentTab", value: TabValue): void;
}>();

const tabs = [
  { value: "ALL" as TabValue, label: "All" },
  { value: "TODO" as TabValue, label: "Todo" },
  { value: "IN_PROGRESS" as TabValue, label: "In Progress" },
  { value: "DONE" as TabValue, label: "Done" },
];
</script>

<template>
  <UButtonGroup size="xl">
    <UButton
      v-for="tab in tabs"
      :key="tab.value"
      :color="currentTab === tab.value ? 'success' : 'neutral'"
      variant="subtle"
      :label="tab.label"
      :class="currentTab !== tab.value && 'bg-transparent'"
      @click="emit('update:currentTab', tab.value)"
    />
  </UButtonGroup>
</template>
