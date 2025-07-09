<script setup lang="ts">
import type { Project, Task, TaskPaginatedResponse } from "~/types/types";
import type { TabsItem } from "@nuxt/ui";

definePageMeta({
  middleware: "auth",
});

const { $api } = useNuxtApp();
const { user } = useAuthStore();
const route = useRoute();

const currentTab = ref<"ALL" | "TODO" | "IN_PROGRESS" | "DONE">("ALL");
const page = ref(1);
const isModalOpen = ref(false);
const editingTask = ref<Task | null>(null); // null when creating, holds a task when editing
const statusCreate = ref<Task["status"] | null>(null);
function openCreateModal(status: Task["status"] | null) {
  if (status) statusCreate.value = status;

  editingTask.value = null; // Clear any previous editing state
  isModalOpen.value = true;
}

function openEditModal(task: Task) {
  editingTask.value = task; // Set the task to be edited
  isModalOpen.value = true;
}
provide(OpenEditModalKey, openEditModal);

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
  page.value = 1;
});

const {
  data: tasksPaginatedResponse,
  pending,
  error,
  refresh,
} = useAsyncData<TaskPaginatedResponse>(
  () => `tasks-${currentTab.value}-${page.value}`,
  () => {
    let url = `/tasks/?author=${user!.id}&page=${page.value}`;
    if (currentTab.value !== "ALL")
      url = `/tasks/?author=${user!.id}&status=${currentTab.value}&page=${
        page.value
      }`;
    return $api(url);
  },
  {
    watch: [currentTab, page],
    server: false,
  }
);

function onTaskSaved() {
  refresh();
  statusCreate.value = null;
}

const items = [
  {
    label: "Kanban",
    icon: "i-heroicons-view-columns",
    slot: "kanban" as const,
  },
  {
    label: "List",
    icon: "i-heroicons-list-bullet",
    slot: "list" as const,
  },
] satisfies TabsItem[];
</script>

<template>
  <UContainer class="py-12">
    <div class="flex justify-between items-center mb-8">
      <h1 class="text-4xl font-bold">My Tasks</h1>

      <UButton
        label="Add Task"
        icon="i-heroicons-plus"
        size="md"
        :ui="{
          leadingIcon: 'text-lg',
        }"
        @click="() => openCreateModal(null)"
      />
    </div>

    <UTabs
      :items="items"
      variant="link"
      class="gap-4 w-full"
      size="xl"
      :ui="{ trigger: 'grow' }"
    >
      <template #list="{}">
        <TaskList
          v-model:current-tab="currentTab"
          v-model:page="page"
          :project-page="false"
          :tasks-paginated-response="tasksPaginatedResponse"
          :pending="pending"
          :error="error"
          @open-edit-modal="openEditModal"
        />
      </template>

      <template #kanban="{}">
        <KanbanView :projects="projects" :project-page="false" />
      </template>
    </UTabs>

    <TaskModal
      v-model:is-modal-open="isModalOpen"
      :projects="projects"
      :project-id="null"
      :editing-task="editingTask"
      :current-tab="currentTab"
      @saved="onTaskSaved"
    />
  </UContainer>
</template>
