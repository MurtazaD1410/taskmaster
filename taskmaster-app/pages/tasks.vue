<script setup lang="ts">
import { z } from "zod";
import { UFormField, UInput, USelect } from "#components";
import type { Project, Task } from "~/types/types";
import type { FormSubmitEvent } from "@nuxt/ui";
import moment from "moment";

const schema = z.object({
  title: z.string().min(1, "Title is required"),
  description: z.string().optional(),
  project: z.number().optional(),
  status: z.enum(["TODO", "IN_PROGRESS", "DONE"]),
});

type Schema = z.infer<typeof schema>;

const state = reactive<Partial<Schema>>({
  title: undefined,
  description: undefined,
  project: undefined,
  status: "TODO",
});

definePageMeta({
  middleware: "auth",
});

const { $api } = useNuxtApp();

const toast = useToast();
const statusOptions = ref(["TODO", "IN_PROGRESS", "DONE"]);

const currentTab = ref<"all" | "todo" | "in_progress" | "done">("all");
// --- Modal State ---
const isModalOpen = ref(false);
const editingTask = ref<Task | null>(null); // null when creating, holds a task when editing

function openCreateModal() {
  editingTask.value = null; // Clear any previous editing state
  state.title = "";
  state.description = "";
  state.project = undefined;
  state.status =
    currentTab.value !== "all"
      ? (currentTab.value.toUpperCase() as "TODO" | "IN_PROGRESS" | "DONE")
      : "TODO";
  isModalOpen.value = true;
}

function openEditModal(task: Task) {
  editingTask.value = task; // Clear any previous editing state
  // Reset form state for a new task
  state.title = task.title;
  state.description = task.description || "";
  state.project = task.project_details?.id || undefined;
  state.status = task.status;
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

const {
  data: tasks,
  pending,
  error,
  refresh,
} = useAsyncData<Array<Task>>(
  () => `tasks-${currentTab.value}`,
  () => {
    let url = "/tasks";
    if (currentTab.value !== "all")
      url = `/tasks/?status=${currentTab.value.toUpperCase()}`;
    return $api(url);
  },
  {
    watch: [currentTab],
    server: false,
  }
);

async function saveTask(event: FormSubmitEvent<Schema>) {
  try {
    if (editingTask.value) {
      await $api(`tasks/${editingTask.value.id}/`, {
        method: "PUT",
        body: event.data,
      });
      toast.add({ title: "Task updated Successfully!", color: "success" });
    } else {
      await $api("tasks/", {
        method: "POST",
        body: event.data,
      });
      toast.add({ title: "Task created Successfully!", color: "success" });
    }
    isModalOpen.value = false;
    await refresh();
  } catch (error) {
    // @ts-expect-error error is type unknown
    const errorData = error?.response?._data;
    const errorMessage = errorData
      ? Object.values(errorData).flat().join(" ")
      : "An unknown error occurred.";
    toast.add({
      title: "An error occurred",
      description: errorMessage,
      color: "error",
    });
  }
}

async function deleteTask(taskId: number) {
  if (!confirm("Are you sure you want to delete this task?")) return;

  try {
    await $api(`tasks/${taskId}/`, {
      method: "DELETE",
    });
    isModalOpen.value = false;
    await refresh();
    toast.add({ title: "Task deleted Successfully!", color: "success" });
  } catch (error) {
    // @ts-expect-error error is type unknown
    const errorData = error?.response?._data;
    const errorMessage = errorData
      ? Object.values(errorData).flat().join(" ")
      : "An unknown error occurred.";
    toast.add({
      title: "Could not delete Task",
      description: errorMessage,
      color: "error",
    });
  }
}
</script>

<template>
  <UContainer class="py-12">
    <div class="flex justify-between items-center mb-8">
      <h1 class="text-4xl font-bold">My Tasks</h1>
      <UButtonGroup size="xl">
        <UButton
          :color="currentTab === 'all' ? 'success' : 'neutral'"
          variant="subtle"
          label="All"
          @click="currentTab = 'all'"
        />
        <UButton
          :color="currentTab === 'todo' ? 'success' : 'neutral'"
          variant="subtle"
          label="Todo"
          @click="currentTab = 'todo'"
        />
        <UButton
          :color="currentTab === 'in_progress' ? 'success' : 'neutral'"
          variant="subtle"
          label="In Progress"
          @click="currentTab = 'in_progress'"
        />
        <UButton
          :color="currentTab === 'done' ? 'success' : 'neutral'"
          variant="subtle"
          label="Done"
          @click="currentTab = 'done'"
        />
      </UButtonGroup>

      <UButton
        label="Add Task"
        icon="i-heroicons-plus"
        size="lg"
        @click="openCreateModal"
      />
    </div>

    <div v-if="pending" class="text-center py-16">
      <UIcon name="i-heroicons-arrow-path" class="text-4xl animate-spin" />
    </div>
    <div v-else-if="error" class="text-center py-16 text-red-500">
      Failed to load tasks.
    </div>
    <div
      v-else-if="!tasks || tasks.length === 0"
      class="text-center py-16 text-gray-500"
    >
      No tasks yet.
    </div>
    <div v-else class="flex flex-col-reverse">
      <UCard
        v-for="task in tasks"
        :key="task.id"
        class="cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors mb-3"
        @click="openEditModal(task)"
      >
        <div class="flex justify-between items-center">
          <div class="flex flex-col gap-2">
            <span class="font-semibold text-lg">{{ task.title }}</span>
            <span class="font-light text-sm">{{
              // moment(task.created_at).format("DD MMM YYYY")
              task.description
            }}</span>
          </div>
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
        </div>
      </UCard>
    </div>

    <!-- The Modal for Creating and Editing -->

    <UModal
      v-model:open="isModalOpen"
      :title="editingTask ? 'Edit Task' : 'Add New Task'"
      :ui="{ footer: 'justify-end' }"
    >
      <template #body>
        <UForm
          :schema="schema"
          :state="state"
          class="space-y-4"
          @submit="saveTask"
        >
          <UFormField label="Title" name="title" required>
            <UInput v-model="state.title" class="w-full" />
          </UFormField>
          <UFormField label="Description" name="description">
            <UTextarea v-model="state.description" class="w-full" />
          </UFormField>
          <UFormField label="Project" name="project">
            <USelect
              v-model="state.project"
              :items="projects.map((project: Project) => ({
                  label: project.title,
                  value: project.id,
                }))"
              class="w-full"
            />
          </UFormField>
          <UFormField label="Status" name="status" required>
            <USelect
              v-model="state.status"
              :items="statusOptions"
              class="w-full"
            />
          </UFormField>
          <div class="flex justify-end gap-3 pt-4">
            <UButton
              label="Cancel"
              color="neutral"
              variant="outline"
              icon="i-heroicons-x-mark"
              @click="isModalOpen = false"
            />
            <UButton
              v-if="editingTask"
              label="Delete"
              color="error"
              icon="i-heroicons-trash"
              @click="() => deleteTask(editingTask.id)"
            />
            <UButton type="submit" label="Save" icon="i-heroicons-check" />
          </div>
        </UForm>
      </template>
    </UModal>
  </UContainer>
</template>
