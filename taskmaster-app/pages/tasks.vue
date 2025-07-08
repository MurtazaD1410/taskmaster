<script setup lang="ts">
import type { Project, Task, TaskPaginatedResponse } from "~/types/types";
import { formatDeadline, isOverdue } from "~/helpers/utils";

definePageMeta({
  middleware: "auth",
});

const { $api } = useNuxtApp();

const priorityOptions = ref([
  { label: "Low", value: "L" },
  { label: "Medium", value: "M" },
  { label: "High", value: "H" },
]);

const currentTab = ref<"ALL" | "TODO" | "IN_PROGRESS" | "DONE">("ALL");
const page = ref(1);
const isModalOpen = ref(false);
const editingTask = ref<Task | null>(null); // null when creating, holds a task when editing

function openCreateModal() {
  editingTask.value = null; // Clear any previous editing state
  isModalOpen.value = true;
}

function openEditModal(task: Task) {
  editingTask.value = task; // Set the task to be edited
  isModalOpen.value = true;
}

const {
  data: projects,
  pending: projectsPending,
  error: projectsError,
  refresh: projectRefresh,
} = useAsyncData<Array<Project>>(
  () => `projects`,
  () => $api("/projects"),

  {
    server: false,
  }
);

watch(currentTab, () => {
  page.value = 1; // reset page on tab change
});

const {
  data: tasksPaginatedResponse,
  pending,
  error,
  refresh,
} = useAsyncData<TaskPaginatedResponse>(
  () => `tasks-${currentTab.value}-${page.value}`,
  () => {
    let url = `/tasks/?page=${page.value}`;
    if (currentTab.value !== "ALL")
      url = `/tasks/?status=${currentTab.value}&page=${page.value}`;
    return $api(url);
  },
  {
    watch: [currentTab, page],
    server: false,
  }
);

function onTaskSaved() {
  refresh();
}
</script>

<template>
  <UContainer class="py-12">
    <div class="flex justify-between items-center mb-8">
      <h1 class="text-4xl font-bold">My Tasks</h1>

      <TaskFilterButton v-model:current-tab="currentTab" />

      <UButton
        label="Add Task"
        icon="i-heroicons-plus"
        size="md"
        :ui="{
          leadingIcon: 'text-lg',
        }"
        @click="openCreateModal"
      />
    </div>
    <TaskFilterButton
      v-model:current-tab="currentTab"
      class="block md:hidden mb-8"
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
        @click="openEditModal(task)"
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
              <div v-if="task.project_details" class="flex items-center gap-1">
                <UIcon
                  name="i-heroicons-folder"
                  class="w-3 h-3 text-primary-500"
                />
                <span
                  class="text-primary-500 dark:text-primary-400 font-medium"
                >
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
              :leading-icon="
                task.status === 'TODO'
                  ? 'i-heroicons-exclamation-circle'
                  : task.status === 'IN_PROGRESS'
                  ? 'i-heroicons-arrow-right-circle'
                  : 'i-heroicons-check-circle'
              "
              size="xl"
              class="capitalize"
              :color="
                task.status == 'TODO'
                  ? 'error'
                  : task.status === 'IN_PROGRESS'
                  ? 'warning'
                  : 'success'
              "
              variant="outline"
            >
              {{ task.status.replace("_", " ").toLowerCase() }}
            </UBadge>
            <p class="text-muted text-sm">{{ task.author?.username }}</p>
          </div>
        </div>
      </UCard>
    </div>

    <TaskModal
      v-model:is-modal-open="isModalOpen"
      :projects="projects"
      :project-id="null"
      :editing-task="editingTask"
      :current-tab="currentTab"
      @saved="onTaskSaved"
    />
    <UPagination
      v-model:page="page"
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
    />
  </UContainer>
</template>
