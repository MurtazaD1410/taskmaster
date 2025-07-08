<script setup lang="ts">
import {
  CalendarDate,
  DateFormatter,
  getLocalTimeZone,
  parseDate,
} from "@internationalized/date";

interface Props {
  modelValue?: string | null;
  placeholder?: string;
  disabled?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: null,
  placeholder: "Select a date",
  disabled: false,
});

const emit = defineEmits<{
  "update:modelValue": [value: string | null];
}>();

const df = new DateFormatter("en-US", {
  dateStyle: "medium",
});

const calendarValue = computed({
  get: () => {
    if (!props.modelValue) return null;
    try {
      // Handle ISO datetime format from your API (2025-07-21T00:00:00Z)
      let dateString = props.modelValue;

      // Extract just the date part from datetime string
      if (dateString.includes("T")) {
        dateString = dateString.split("T")[0];
      }

      // Remove any timezone indicators
      if (dateString.includes("Z")) {
        dateString = dateString.replace("Z", "");
      }

      // Parse ISO date string (YYYY-MM-DD) to CalendarDate
      return parseDate(dateString);
    } catch (error) {
      console.warn("Failed to parse date:", props.modelValue, error);
      return null;
    }
  },
  set: (value: CalendarDate | null) => {
    // Convert CalendarDate to ISO string format that your API expects
    // Your API seems to expect datetime format, so we'll add the time part
    emit("update:modelValue", value ? `${value.toString()}T00:00:00Z` : null);
  },
});

const today = computed(() => {
  const now = new Date();
  return new CalendarDate(
    now.getFullYear(),
    now.getMonth() + 1, // months are 1-indexed in CalendarDate
    now.getDate()
  );
});

// Format display value
const displayValue = computed(() => {
  if (!calendarValue.value) return props.placeholder;
  return df.format(calendarValue.value.toDate(getLocalTimeZone()));
});
</script>

<template>
  <UPopover>
    <UButton
      color="neutral"
      variant="subtle"
      icon="i-lucide-calendar"
      :disabled="disabled"
      class="w-full justify-start"
    >
      {{ displayValue }}
    </UButton>

    <template #content>
      <UCalendar
        v-model="calendarValue"
        class="p-2"
        :disabled="disabled"
        :min-value="today"
      />
    </template>
  </UPopover>
</template>
