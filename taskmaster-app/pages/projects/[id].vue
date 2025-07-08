<script setup lang="ts">
import { z } from "zod";
import { UFormField, UInput, USelect } from "#components";
import type { Project, Task, TaskPaginatedResponse } from "~/types/types";
import type { FormSubmitEvent } from "@nuxt/ui";

import { useRoute } from "#app";
import { formatDeadline, isOverdue } from "~/helpers/utils";
import TaskModal from "~/components/TaskModal.vue";

const { $api } = useNuxtApp();

const route = useRoute();
const { user } = useAuthStore();
const router = useRouter();
const toast = useToast();

const priorityOptions = ref([
  { label: "Low", value: "L" },
  { label: "Medium", value: "M" },
  { label: "High", value: "H" },
]);

const inviteState = reactive({
  email: "",
});

const emailCheckStatus = ref<
  "idle" | "checking" | "exists" | "not_found" | "invalid"
>("idle");
const emailCheckMessage = ref("");
let debounceTimeout: NodeJS.Timeout;

watch(
  () => inviteState.email,
  (newEmail) => {
    // Clear any previous debounce timer
    clearTimeout(debounceTimeout);

    // Reset status if the input is cleared
    if (!newEmail) {
      emailCheckStatus.value = "idle";
      emailCheckMessage.value = "";
      return;
    }

    // Set a new timer
    debounceTimeout = setTimeout(async () => {
      // Basic email format check before hitting the API
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(newEmail)) {
        emailCheckStatus.value = "invalid";
        emailCheckMessage.value = "Please enter a valid email format.";
        return;
      }

      try {
        emailCheckStatus.value = "checking";
        emailCheckMessage.value = "Checking email...";

        // We will create this API endpoint in the next step
        const response = await $api("/auth/users/check-email/", {
          method: "POST",
          body: { email: newEmail },
        });

        // User exists!
        emailCheckStatus.value = "exists";
        // Assuming the API returns the user's name
        emailCheckMessage.value = `User found: ${response.username}. They will be added to the project.`;
      } catch (error: any) {
        if (error.statusCode === 404) {
          // User does not exist
          emailCheckStatus.value = "not_found";
          emailCheckMessage.value = "User not found.";
        } else {
          // Other API errors
          emailCheckStatus.value = "idle";
          emailCheckMessage.value = "Could not verify email at this time.";
        }
      }
    }, 750); // Wait 750ms after the user stops typing
  }
);

const currentTab = ref<"ALL" | "TODO" | "IN_PROGRESS" | "DONE">("ALL");
const page = ref(1);
const isModalOpen = ref(false);
const isProjectModalOpen = ref(false);
const isInviteMemberModalOpen = ref(false);
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

definePageMeta({
  middleware: "auth",
});

function openTaskCreateModal() {
  editingTask.value = null; // Clear any previous editing state
  isModalOpen.value = true;
}

function openTaskEditModal(task: Task) {
  editingTask.value = task; // Set the task to be edited
  isModalOpen.value = true;
}

function openProjectEditModal(project: Project) {
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

watch(currentTab, () => {
  page.value = 1; // reset page on tab change
});

const {
  data: tasksPaginatedResponse,
  pending: tasksPending,
  error: tasksError,
  refresh: tasksRefresh,
} = useAsyncData<TaskPaginatedResponse>(
  () => `tasks-${currentTab.value}-${page.value}-${route.params.id}`,
  () => {
    let url = `/tasks/?project=${route.params.id}&page=${page.value}`;
    if (currentTab.value !== "ALL")
      url = `/tasks/?project=${route.params.id}&status=${currentTab.value}&page=${page.value}`;
    return $api(url);
  },
  {
    watch: [currentTab, page],
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

function onTaskSaved() {
  tasksRefresh();
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
      : "An error occurred.";
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

async function onSubmit(event: FormSubmitEvent<{ email: string }>) {
  try {
    await $api(`projects/${route.params.id}/invitations/`, {
      method: "POST",
      body: event.data,
    });
    toast.add({ title: "Invite sent Successfully!", color: "success" });
    isInviteMemberModalOpen.value = false;
    await refresh();
  } catch (error) {
    toast.add({
      title: "Could not send invite.",
      description: "Check if you are authorized to send an invite.",
      color: "error",
    });
  }
  isInviteMemberModalOpen.value = false;
}

const sortedMembers = computed(() => {
  if (!project.value?.members) return [];
  return [...project.value.members].sort((a, b) => {
    if (a.id === project.value?.owner.id) return -1;
    if (b.id === project.value?.owner.id) return 1;
    return 0;
  });
});

async function removeMember(user_id: number, project_id: number) {
  try {
    await $api(`projects/${project_id}/members/${user_id}/`, {
      method: "DELETE",
    });
    toast.add({ title: "User removed Successfully!", color: "success" });

    await refresh();
  } catch (error) {
    toast.add({
      title: "An error occurred",
      description: (error as { detail: string }).detail,
      color: "error",
    });
  }
}
async function leaveProject(project_id: number) {
  try {
    await $api(`projects/${project_id}/members/`, {
      method: "DELETE",
    });
    toast.add({ title: "Project left Successfully!", color: "success" });

    navigateTo("/projects");
  } catch (error) {
    toast.add({
      title: "An error occurred",
      description: (error as { detail: string }).detail,
      color: "error",
    });
  }
}

const dropdownItems = computed(() =>
  sortedMembers.value.map((member) => {
    const isOwner = member.id === project.value?.owner.id;
    const isSelf = member.id === user?.id;

    return {
      label: member.username,
      avatar: { src: member.avatar, alt: member.username },
      // Only add children if member is NOT the owner
      ...(isOwner
        ? {}
        : {
            children: [
              [
                {
                  label: "Remove",
                  icon: "i-heroicons-trash",
                  color: "error",
                  onSelect: () => removeMember(member.id, project.value!.id),
                },
              ],
            ],
          }),

      ...(isSelf && !isOwner
        ? {
            children: [
              [
                {
                  label: "Leave",
                  icon: "i-heroicons-arrow-left-start-on-rectangle-20-solid",
                  color: "error",
                  onSelect: () => leaveProject(project.value!.id),
                },
              ],
            ],
          }
        : {}),
    };
  })
);
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
            <div class="flex gap-4">
              <h1 class="text-2xl md:text-3xl lg:text-4xl font-bold">
                {{ project?.title }}
              </h1>
              <div
                v-if="project?.owner.id !== user?.id"
                class="flex items-center gap-1"
              >
                <UIcon name="i-heroicons-folder" class="text-primary-500" />
                <span
                  class="text-primary-500 dark:text-primary-400 font-medium text-lg"
                >
                  {{ project?.owner.username }}
                </span>
              </div>
            </div>
            <p class="text-muted">{{ project?.description }}</p>
          </div>
        </div>
        <div class="flex flex-row gap-2 lg:gap-4 items-center">
          <UDropdownMenu
            :items="dropdownItems"
            :content="{
              align: 'end',
              side: 'bottom',
              sideOffset: 8,
            }"
            size="lg"
            :ui="{
              content: 'w-48',
            }"
          >
            <UAvatarGroup size="xl" max="2">
              <UTooltip
                v-for="member in sortedMembers"
                :key="member.id"
                :text="member.username"
              >
                <UAvatar
                  :src="member.avatar"
                  :alt="member.username"
                  :class="
                    member.id == project?.owner.id &&
                    'border-2 border-primary-500'
                  "
                />
              </UTooltip>
            </UAvatarGroup>
          </UDropdownMenu>

          <UButton
            v-if="project?.owner.id === user?.id"
            icon="i-heroicons-user-plus"
            size="md"
            class="w-8 h-8 lg:w-auto lg:h-auto flex items-center justify-center"
            :ui="{
              leadingIcon: 'text-xl lg:text-lg',
            }"
            @click="isInviteMemberModalOpen = true"
          >
            <span class="hidden lg:inline">Invite Member</span>
          </UButton>

          <UButton
            icon="i-heroicons-plus"
            size="md"
            class="w-8 h-8 lg:w-auto lg:h-auto flex items-center justify-center"
            :ui="{
              leadingIcon: 'text-xl lg:text-lg',
            }"
            @click="openTaskCreateModal"
          >
            <span class="hidden lg:inline">Add Task</span>
          </UButton>
          <UDropdownMenu
            v-if="project?.owner.id === user?.id"
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

      <TaskFilterButton v-model:current-tab="currentTab" class="mb-8" />

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
      <div v-else class="flex flex-col gap-4">
        <div class="flex flex-col">
          <UCard
            v-for="task in tasksPaginatedResponse?.results"
            :key="task.id"
            class="cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors mb-3"
            @click="openTaskEditModal(task)"
          >
            <div class="flex justify-between items-center">
              <div class="flex flex-col gap-2 flex-1">
                <!-- Main task info -->

                <div class="flex flex-col gap-1">
                  <span class="font-semibold text-lg">{{ task.title }}</span>
                  <span
                    class="font-light text-sm text-gray-600 dark:text-gray-400"
                  >
                    {{ task.description }}
                  </span>
                </div>

                <!-- Optional fields row -->
                <div class="flex flex-wrap gap-2 items-center text-xs">
                  <!-- Project -->
                  <div
                    v-if="task.project_details"
                    class="flex items-center gap-1"
                  >
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
                      priorityOptions.find((p) => p.value === task.priority)
                        ?.label
                    }}
                  </UBadge>

                  <!-- Deadline -->
                  <div v-if="task.deadline" class="flex items-center gap-1">
                    <UIcon
                      name="i-heroicons-calendar-days"
                      class="w-3 h-3"
                      :class="
                        isOverdue(task.deadline)
                          ? 'text-red-500'
                          : 'text-gray-500'
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
      </div>
    </div>
    <!-- The Modal for Creating and Editing -->

    <!-- <UModal
      v-model:open="isModalOpen"
      :dismissible="false"
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
          <UFormField label="Priority" name="priority">
            <USelect
              v-model="taskState.priority"
              :items="priorityOptions"
              class="w-full"
            />
          </UFormField>
          <UFormField label="Deadline" name="deadline">
            <CalendarFormFeild
              v-model="taskState.deadline"
              class="w-full bg-transparent"
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
              @click="() => deleteTask(editingTask!.id)"
            />
            <UButton type="submit" label="Save" icon="i-heroicons-check" />
          </div>
        </UForm>
      </template>
    </UModal> -->
    <TaskModal
      v-model:is-modal-open="isModalOpen"
      :projects="null"
      :status-create="null"
      :editing-task="editingTask"
      :current-tab="currentTab"
      :project-id="route.params.id as string"
      @saved="onTaskSaved"
    />

    <UModal
      v-model:open="isProjectModalOpen"
      :dismissible="false"
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

    <UModal v-model:open="isInviteMemberModalOpen" :dismissible="false">
      <template #header>
        <h3 class="text-lg font-semibold">Invite a New Member</h3>
      </template>
      <template #body>
        <UForm :state="inviteState" class="space-y-4" @submit="onSubmit">
          <UFormField
            label="Email"
            name="email"
            :help="emailCheckMessage"
            :ui="{
              help: `text-sm ${
                emailCheckStatus === 'exists'
                  ? 'text-green-500'
                  : emailCheckStatus === 'not_found'
                  ? 'text-orange-500'
                  : emailCheckStatus === 'invalid'
                  ? 'text-red-500'
                  : ''
              }`,
            }"
          >
            <UInput
              v-model="inviteState.email"
              class="w-full"
              placeholder="you@example.com"
              :loading="emailCheckStatus === 'checking'"
              :icon="
                emailCheckStatus === 'exists'
                  ? 'i-heroicons-check-circle-20-solid'
                  : emailCheckStatus === 'invalid'
                  ? 'i-heroicons-exclamation-circle-20-solid'
                  : undefined
              "
            />
          </UFormField>

          <div class="flex justify-end gap-3">
            <UButton
              label="Cancel"
              color="neutral"
              variant="outline"
              icon="i-heroicons-x-mark"
              @click="isInviteMemberModalOpen = false"
            />
            <UButton
              type="submit"
              label="Send Invite"
              color="primary"
              :disabled="emailCheckStatus !== 'exists'"
            />
          </div>
        </UForm>
      </template>
    </UModal>
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
