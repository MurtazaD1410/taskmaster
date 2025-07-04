<script setup lang="ts">
import { z } from "zod";
import { UFormField, UInput, USelect } from "#components";
import type { Project, Task } from "~/types/types";
import type { DropdownMenuItem, FormSubmitEvent } from "@nuxt/ui";

import { useRoute } from "#app";

const { $api } = useNuxtApp();

const route = useRoute();
const router = useRouter();
const toast = useToast();
const statusOptions = ref(["TODO", "IN_PROGRESS", "DONE"]);

const currentTab = ref<"all" | "todo" | "in_progress" | "done">("all");
// --- Modal State ---
const isModalOpen = ref(false);
const isProjectModalOpen = ref(false);
const editingTask = ref<Task | null>(null);
const editingProject = ref<Project | null>(null);

const projectSchema = z.object({
  title: z.string().min(1, "Title is required"),
  description: z.string().optional(),
});

type ProjectSchema = z.infer<typeof projectSchema>;

const projectState = reactive<Partial<ProjectSchema>>({
  title: undefined,
  description: undefined,
});

const taskSchema = z.object({
  title: z.string().min(1, "Title is required"),
  description: z.string().optional(),
  project: z.number().optional(),
  status: z.enum(["TODO", "IN_PROGRESS", "DONE"]),
});

type TaskSchema = z.infer<typeof taskSchema>;

const taskState = reactive<Partial<TaskSchema>>({
  title: undefined,
  status: "TODO",
  description: undefined,
  project: undefined,
});

definePageMeta({
  middleware: "auth",
});

function openTaskCreateModal() {
  editingTask.value = null;
  taskState.title = "";
  taskState.description = "";
  taskState.project = parseInt(route.params.id as string);
  taskState.status =
    currentTab.value !== "all"
      ? (currentTab.value.toUpperCase() as "TODO" | "IN_PROGRESS" | "DONE")
      : "TODO";
  isModalOpen.value = true;
}

function openTaskEditModal(task: Task) {
  editingTask.value = task; // Clear any previous editing state
  // Reset form state for a new task
  taskState.title = task.title;
  taskState.description = task.description || "";
  taskState.project = task.project_details?.id || undefined;
  taskState.status = task.status;
  isModalOpen.value = true;
}

function openProjectEditModal(project: Project) {
  console.log("clicked edit ");
  editingProject.value = project; // Clear any previous editing state
  // Reset form state for a new task
  projectState.title = project.title;
  projectState.description = project.description || "";
  isProjectModalOpen.value = true;
}

const {
  data: project,
  pending,
  error,
  refresh,
} = useAsyncData<Project>(
  () => `project`,
  () => $api(`/projects/${route.params.id}`),

  {
    server: false,
  }
);

const {
  data: tasks,
  pending: tasksPending,
  error: tasksError,
  refresh: tasksRefresh,
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

async function saveProject(event: FormSubmitEvent<ProjectSchema>) {
  try {
    await $api(`projects/${route.params.id}/`, {
      method: "PUT",
      body: event.data,
    });
    toast.add({ title: "Project updated Successfully!", color: "success" });

    isProjectModalOpen.value = false;
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
async function saveTask(event: FormSubmitEvent<TaskSchema>) {
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
    await tasksRefresh();
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
    await tasksRefresh();
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

async function deleteProject(projectId: number) {
  if (!confirm("Are you sure you want to delete this task?")) return;

  try {
    await $api(`projects/${projectId}/`, {
      method: "DELETE",
    });
    isModalOpen.value = false;
    toast.add({ title: "Project deleted Successfully!", color: "success" });
    navigateTo("/projects");
  } catch (error) {
    // @ts-expect-error error is type unknown
    const errorData = error?.response?._data;
    const errorMessage = errorData
      ? Object.values(errorData).flat().join(" ")
      : "An unknown error occurred.";
    toast.add({
      title: "Could not delete Project",
      description: errorMessage,
      color: "error",
    });
  }
}

const items = computed(() => {
  if (!project.value) {
    return [
      [
        {
          label: "Loading...",
          icon: "i-heroicons-arrow-path",
        },
      ],
    ];
  }

  return [
    [
      {
        label: project.value.title,
        icon: "i-heroicons-briefcase",
        type: "label",
        class: "font-semibold",
      },
    ],
    [
      {
        label: "Edit",
        icon: "i-heroicons-pencil",
        onSelect() {
          openProjectEditModal(project.value!);
        },
      },
      {
        label: "Delete",
        icon: "i-heroicons-trash",
        color: "error",
        onSelect() {
          deleteProject(project.value!.id);
        },
      },
    ],
  ];
});
</script>

<template>
  <UContainer class="py-12">
    <div v-if="pending" class="text-center py-16">
      <UIcon name="i-heroicons-arrow-path" class="text-4xl animate-spin" />
    </div>
    <div v-else-if="error" class="text-center py-16 text-red-500">
      Failed to load project.
    </div>
    <div v-else class="">
      <div class="flex justify-between items-center mb-8">
        <div class="flex flow-row gap-4 items-center">
          <UButton
            icon="i-heroicons-arrow-left-solid"
            size="xl"
            variant="ghost"
            color="neutral"
            class="aspect-square h-8 w-8"
            :ui="{
              leadingIcon: 'text-xl',
            }"
            @click="router.back()"
          />
          <div class="">
            <h1 class="text-4xl font-bold">{{ project.title }}</h1>
            <p class="text-muted">{{ project.description }}</p>
          </div>
        </div>
        <div class="flex flex-row gap-4 items-center">
          <UButton
            label="Add Task"
            icon="i-heroicons-plus"
            size="lg"
            @click="openTaskCreateModal"
          />
          <UDropdownMenu
            :items="items"
            :content="{
              align: 'end',
              side: 'bottom',
              sideOffset: 8,
            }"
            :ui="{
              content: 'w-48',
            }"
          >
            <UButton
              icon="i-lucide-menu"
              color="neutral"
              variant="outline"
              size="lg"
              class="w-8 h-8"
            />
          </UDropdownMenu>
        </div>
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
      <div v-else class="flex flex-col gap-4">
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
        <div class="flex flex-col-reverse">
          <UCard
            v-for="task in tasks"
            :key="task.id"
            class="cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors mb-3"
            @click="openTaskEditModal(task)"
          >
            <div class="flex justify-between items-center">
              <div class="flex flex-col gap-2">
                <span class="font-semibold text-lg">{{ task.title }}</span>
                <span class="font-light text-sm text-muted">{{
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
      </div>
    </div>
    <!-- The Modal for Creating and Editing -->

    <UModal
      v-model:open="isModalOpen"
      :title="editingTask ? 'Edit Task' : 'Add New Task'"
      :ui="{ footer: 'justify-end' }"
    >
      <template #body>
        <UForm
          :schema="taskSchema"
          :state="taskState"
          class="space-y-4"
          @submit="saveTask"
        >
          <UFormField label="Title" name="title" required>
            <UInput v-model="taskState.title" class="w-full" />
          </UFormField>
          <UFormField label="Description" name="description">
            <UTextarea v-model="taskState.description" class="w-full" />
          </UFormField>
          <UFormField label="Status" name="status" required>
            <USelect
              v-model="taskState.status"
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

    <UModal
      v-model:open="isProjectModalOpen"
      title="Edit Project"
      :ui="{ footer: 'justify-end' }"
    >
      <template #body>
        <UForm
          :schema="projectSchema"
          :state="projectState"
          class="space-y-4"
          @submit="saveProject"
        >
          <UFormField label="Title" name="title" required>
            <UInput v-model="projectState.title" class="w-full" />
          </UFormField>
          <UFormField label="Description" name="description">
            <UTextarea v-model="projectState.description" class="w-full" />
          </UFormField>
          <div class="flex justify-end gap-3 pt-4">
            <UButton
              label="Cancel"
              color="neutral"
              variant="outline"
              icon="i-heroicons-x-mark"
              @click="isProjectModalOpen = false"
            />
            <UButton type="submit" label="Save" icon="i-heroicons-check" />
          </div>
        </UForm>
      </template>
    </UModal>
  </UContainer>
</template>
