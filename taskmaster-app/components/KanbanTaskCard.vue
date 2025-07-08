<script setup lang="ts">
import { formatDeadline, isOverdue } from "~/helpers/utils";
import type { Task } from "~/types/types";
const priorityOptions = ref([
  { label: "Low", value: "L" },
  { label: "Medium", value: "M" },
  { label: "High", value: "H" },
]);
const props = defineProps<{
  task: Task;
}>();
</script>

<template>
  <UCard
    :key="task.id"
    variant="outline"
    class="cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-900/80 transition-colors mb-3"
  >
    <div class="flex justify-between items-center">
      <div class="flex flex-col gap-2 flex-1">
        <!-- Main task info -->
        <div class="flex flex-col">
          <span class="font-semibold text-base line-clamp-1">{{
            task.title
          }}</span>
          <!-- <span class="font-light text-sm text-gray-600 dark:text-gray-400">
            {{ task.description }}
          </span> -->
        </div>

        <!-- Optional fields row -->
        <div class="flex flex-wrap gap-2 items-center text-xs">
          <!-- Project -->
          <div v-if="task.project_details" class="flex items-center gap-1">
            <UIcon name="i-heroicons-folder" class="w-3 h-3 text-primary-500" />
            <span
              class="text-primary-500 dark:text-primary-400 font-medium max-w-20 text-ellipsis line-clamp-1"
            >
              {{ task.project_details?.title }}
            </span>
          </div>

          <!-- Deadline -->
          <div v-if="task.deadline" class="flex items-center gap-1">
            <UIcon
              name="i-heroicons-calendar-days"
              class="w-3 h-3"
              :class="
                isOverdue(task.deadline) ? 'text-red-500' : 'text-gray-500'
              "
            />
            <span
              class="text-xs"
              :class="
                isOverdue(task.deadline)
                  ? 'text-red-600 dark:text-red-400 font-medium'
                  : 'text-gray-500 dark:text-gray-400'
              "
            >
              {{ formatDeadline(task.deadline) }}
            </span>
          </div>
        </div>
      </div>

      <!-- Status badge -->
      <div
        class="ml-4 flex-shrink-0 flex flex-col gap-3 justify-center items-end"
      >
        <UBadge
          v-if="task.priority"
          :color="
            task.priority === 'H'
              ? 'error'
              : task.priority === 'M'
              ? 'warning'
              : 'neutral'
          "
          variant="soft"
          size="sm"
        >
          {{ priorityOptions.find((p) => p.value === task.priority)?.label }}
        </UBadge>

        <!-- <p class="text-muted text-sm">{{ task.author?.username }}</p> -->
      </div>
    </div>
  </UCard>
</template>
