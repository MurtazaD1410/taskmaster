<script lang="ts" setup>
import {
  formatDeadline,
  getIconAndColorForStatus,
  isOverdue,
} from "~/helpers/utils";
import type { Task, TaskPaginatedResponse } from "~/types/types";

type TabValue = "ALL" | "TODO" | "BACKLOG" | "IN_PROGRESS" | "DONE";
const priorityOptions = ref([
  { label: "Low", value: "L" },
  { label: "Medium", value: "M" },
  { label: "High", value: "H" },
]);
const props = defineProps<{
  tasksPaginatedResponse: TaskPaginatedResponse | null;
  page: number;
  currentTab: TabValue;
  pending: boolean;
  error: any;
  projectPage?: boolean;
}>();

const emit = defineEmits<{
  (e: "open-edit-modal", task: Task): void;
  (e: "update:currentTab", value: TabValue): void;
  (e: "update:page", value: number): void;
}>();

function handleClick(task: Task) {
  emit("open-edit-modal", task); // Notify the parent
}
</script>

<template>
  <TaskFilterButton
    :current-tab="props.currentTab"
    class="mb-4"
    @update:current-tab="emit('update:currentTab', $event)"
  />

  <div v-if="pending" class="text-center py-16">
    <UIcon name="i-heroicons-arrow-path" class="text-4xl animate-spin" />
  </div>
  <div v-else-if="error" class="text-center py-16 text-red-500">
    Failed to load tasks.
  </div>
  <div
    v-else-if="tasksPaginatedResponse?.count === 0"
    class="text-center py-16 text-gray-500"
  >
    No tasks yet.
  </div>
  <div v-else class="flex flex-col">
    <UCard
      v-for="task in tasksPaginatedResponse?.results"
      :key="task.id"
      class="cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors mb-3"
      @click="handleClick(task)"
    >
      <div class="flex justify-between items-center">
        <div class="flex flex-col gap-2 flex-1">
          <!-- Main task info -->
          <div class="flex flex-col gap-1">
            <span class="font-semibold text-lg">{{ task.title }}</span>
            <span class="font-light text-sm text-gray-600 dark:text-gray-400">
              {{ task.description }}
            </span>
          </div>

          <!-- Optional fields row -->
          <div class="flex flex-wrap gap-2 items-center text-xs">
            <!-- Project -->
            <div
              v-if="task.project_details && !projectPage"
              class="flex items-center gap-1"
            >
              <UIcon
                name="i-heroicons-folder"
                class="w-3 h-3 text-primary-500"
              />
              <span class="text-primary-500 dark:text-primary-400 font-medium">
                {{ task.project_details?.title }}
              </span>
            </div>

            <!-- Priority -->
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
              {{
                priorityOptions.find((p) => p.value === task.priority)?.label
              }}
            </UBadge>

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
            :leading-icon="getIconAndColorForStatus(task.status).icon"
            size="lg"
            class="capitalize"
            :color="getIconAndColorForStatus(task.status).color"
            variant="outline"
            :ui="{
              leadingIcon: 'text-lg',
            }"
          >
            {{ getIconAndColorForStatus(task.status).label }}
          </UBadge>
          <div
            v-if="task.assignee_details"
            class="ml-4 flex-shrink-0 flex items-center justify-center"
          >
            <UTooltip :text="task.assignee_details.username">
              <UAvatar
                :src="task.assignee_details.avatar"
                :alt="task.assignee_details.username"
              />
            </UTooltip>

            <!-- <p class="text-muted text-sm">{{ task.author?.username }}</p> -->
          </div>
          <p v-if="projectPage" class="text-muted text-sm">
            {{ task.author?.username }}
          </p>
        </div>
      </div>
    </UCard>
  </div>
  <UPagination
    :page="page"
    class="flex justify-end"
    active-color="primary"
    active-variant="subtle"
    :total="tasksPaginatedResponse?.count"
    size="md"
    :items-per-page="6"
    show-edges
    :ui="{
      ellipsis: 'w-8 h-8 flex items-center justify-center',
      last: 'w-8 h-8 flex items-center justify-center',
      first: 'w-8 h-8 flex items-center justify-center',
      prev: 'w-8 h-8 flex items-center justify-center',
      next: 'w-8 h-8 flex items-center justify-center',
    }"
    :sibling-count="1"
    @update:page="emit('update:page', $event)"
  />
</template>
