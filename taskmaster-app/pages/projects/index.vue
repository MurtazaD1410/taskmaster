<script setup lang="ts">
import { z } from "zod";
import { UFormField, UInput } from "#components";
import type { Project, Task, TaskPaginatedResponse } from "~/types/types";
import type { FormSubmitEvent } from "@nuxt/ui";

const schema = z.object({
  title: z.string().min(1, "Title is required"),
  description: z.string().optional(),
});

type Schema = z.infer<typeof schema>;

const state = reactive<Partial<Schema>>({
  title: undefined,
  description: undefined,
});

definePageMeta({
  middleware: "auth",
});
const authStore = useAuthStore();
const route = useRoute();
const router = useRouter();
const { $api } = useNuxtApp();

const toast = useToast();
// --- Modal State ---
const isModalOpen = ref(false);
watchEffect(() => {
  isModalOpen.value = route.query.create === "true";
});

function openCreateModal() {
  state.title = "";
  state.description = "";
  router.push({ query: { ...route.query, create: "true" } });
}

const {
  data: projects,
  pending,
  error,
  refresh,
} = useAsyncData<Array<Project>>(
  () => `projects`,
  () => $api("/projects"),

  {
    server: false,
  }
);

const {
  data: tasksPaginatedResponse,
  pending: tasksPending,
  error: tasksError,
  refresh: tasksRefresh,
} = useAsyncData<TaskPaginatedResponse>(
  () => `tasks`,
  () => {
    return $api("/tasks");
  },
  {
    server: false,
  }
);

async function saveProject(event: FormSubmitEvent<Schema>) {
  try {
    await $api("projects/", {
      method: "POST",
      body: event.data,
    });
    toast.add({ title: "Project created Successfully!", color: "success" });

    const { create, ...rest } = route.query;
    router.replace({ query: { ...rest } });
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
</script>

<template>
  <UContainer class="py-12">
    <div class="flex justify-between items-center mb-8">
      <h1 class="text-4xl font-bold">My Projects</h1>

      <UButton
        label="Add Project"
        icon="i-heroicons-plus"
        size="md"
        :ui="{
          leadingIcon: 'text-lg',
        }"
        @click="openCreateModal"
      />
    </div>

    <div v-if="pending" class="text-center py-16">
      <UIcon name="i-heroicons-arrow-path" class="text-4xl animate-spin" />
    </div>
    <div v-else-if="error" class="text-center py-16 text-red-500">
      Failed to load projects.
    </div>
    <div
      v-else-if="!projects || projects.length === 0"
      class="text-center py-16 text-gray-500"
    >
      No projects yet.
    </div>
    <div v-else class="flex flex-col-reverse">
      <UCard
        v-for="project in projects"
        :key="project.id"
        class="cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors mb-3"
        @click="navigateTo(`/projects/${project.id}`)"
      >
        <div class="flex justify-between items-center">
          <div class="flex flex-col gap-2">
            <div class="flex items-center gap-4">
              <span class="font-semibold text-lg">{{ project.title }}</span>
              <div
                v-if="project.owner.id !== authStore.user?.id"
                class="flex items-center gap-1"
              >
                <UIcon
                  name="i-heroicons-folder"
                  class="w-3 h-3 text-primary-500"
                />
                <span
                  class="text-primary-500 dark:text-primary-400 font-medium"
                >
                  {{ project?.owner.username }}
                </span>
              </div>
            </div>
            <span class="font-light text-sm text-muted">{{
              // moment(task.created_at).format("DD MMM YYYY")
              project.description
            }}</span>
          </div>
          <UBadge
            icon="i-heroicons-list-bullet"
            size="lg"
            color="neutral"
            variant="outline"
            >{{ project.task_count }}</UBadge
          >
        </div>
      </UCard>
    </div>

    <!-- The Modal for Creating and Editing -->

    <UModal
      v-model:open="isModalOpen"
      title="Add New Project"
      :ui="{ footer: 'justify-end' }"
      :dismissible="false"
    >
      <template #body>
        <UForm
          :schema="schema"
          :state="state"
          class="space-y-4"
          @submit="saveProject"
        >
          <UFormField label="Title" name="title" required>
            <UInput v-model="state.title" class="w-full" />
          </UFormField>
          <UFormField label="Description" name="description">
            <UTextarea v-model="state.description" class="w-full" />
          </UFormField>

          <div class="flex justify-end gap-3 pt-4">
            <UButton
              label="Cancel"
              color="neutral"
              variant="outline"
              icon="i-heroicons-x-mark"
              @click="
                () => {
                  const { create, ...rest } = route.query;
                  router.replace({ query: { ...rest } }); // Use replace to avoid history spam
                }
              "
            />
            <!-- <UButton
              v-if="editingTask"
              label="Delete"
              color="error"
              icon="i-heroicons-trash"
              @click="() => deleteTask(editingTask.id)"
            /> -->
            <UButton type="submit" label="Save" icon="i-heroicons-check" />
          </div>
        </UForm>
      </template>
    </UModal>
  </UContainer>
</template>
