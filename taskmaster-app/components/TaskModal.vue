<script setup lang="ts">
import { reactive, watch } from "vue";
import type { FormSubmitEvent } from "@nuxt/ui";
import { taskSchema } from "~/schemas/taskSchema";
import type { TaskSchema } from "~/schemas/taskSchema";
import type { Project, Task, User } from "~/types/types";

const formRef = ref();
const { $api } = useNuxtApp();
const route = useRoute();
const router = useRouter();
const { saveTask, deleteTask } = useTaskService();

const statusOptions = ref([
  { label: "Todo", value: "TODO" },
  { label: "Backlog", value: "BACKLOG" },
  { label: "In Progress", value: "IN_PROGRESS" },
  { label: "Done", value: "DONE" },
]);
const priorityOptions = ref([
  { label: "Low", value: "L" },
  { label: "Medium", value: "M" },
  { label: "High", value: "H" },
]);

const props = defineProps<{
  isModalOpen: boolean;
  editingTask: Task | null;
  projects: Project[] | null;
  projectId: string | null;
  projectPage?: boolean;
  currentTab: "ALL" | "TODO" | "BACKLOG" | "IN_PROGRESS" | "DONE";
}>();

const emit = defineEmits<{
  (e: "update:isModalOpen", value: boolean): void; // For v-model
  (e: "saved"): void; // To tell the parent to refresh data
}>();

const getDefaultState = (): Partial<TaskSchema> => ({
  title: undefined,
  description: undefined,
  // If a specific project page is open, default to that project.
  project: (props.projectId && parseInt(props.projectId)) || undefined,
  // If a specific status tab is active, default to that status.
  status:
    props.currentTab && props.currentTab !== "ALL" ? props.currentTab : "TODO",
  priority: undefined,
  deadline: undefined,
});

const state = reactive<Partial<TaskSchema>>(getDefaultState());

watch(
  () => props.isModalOpen,
  (isOpen) => {
    if (isOpen) {
      // When the modal opens, decide whether to load an editing task or reset the form.
      if (props.editingTask) {
        // Populate form for editing
        const task = props.editingTask;
        state.title = task.title;
        state.description = task.description || "";
        state.project = task.project_details?.id;
        state.status = task.status;
        state.priority = task.priority || undefined;
        state.assignee = task.assignee_details?.id;
        state.deadline = task.deadline || undefined;
      } else {
        // Reset form for creating
        Object.assign(state, getDefaultState());
      }
    }
  }
);

const {
  data: members,
  pending: membersPending,
  error: membersError,
  refresh: membersRefresh,
} = useAsyncData<Array<User>>(
  // () => `members-${props.projectId}`,
  // () => {
  //   return $api(
  //     `/projects/${props.projectPage ? props.projectId : state.project}/members`
  //   );
  // },
  // {
  //   watch: [() => state.project],
  //   server: false,
  // }
  () => `members-${props.projectId ?? state.project}`, // Key must stay unique
  () => {
    const projectId = props.projectPage ? props.projectId : state.project;

    if (!projectId) return Promise.resolve([]);

    return $api(`/projects/${projectId}/members`);
  },
  {
    // ✅ Watch both reactively, but only when they exist
    watch: [() => props.projectId, () => state.project],
    server: false,
  }
);

async function handleSave(event: FormSubmitEvent<TaskSchema>) {
  try {
    await saveTask(event, props.editingTask?.id);
    emit("saved");
    emit("update:isModalOpen", false);
  } catch (error) {
    console.error("Save task failed, keeping modal open.");
  }
}
async function handleDelete(taskId: number) {
  try {
    await deleteTask(taskId);

    emit("saved");
    emit("update:isModalOpen", false);
  } catch (error) {
    console.error("Save task failed, keeping modal open.");
  }
}

const items = ref<
  Array<{ label: string; avatar: { src: string; alt: string }; value: number }>
>([]);
watch(
  () => members.value,
  (newMembers) => {
    if (newMembers) {
      items.value = newMembers.map((member) => ({
        label: member.username,
        avatar: { src: member.avatar, alt: member.username },
        value: member.id, // optional, if needed for select
      }));
    }
  },
  { immediate: true }
);

const avatar = computed(() => {
  const item = items.value.find((item) => item.value === state.assignee);
  // item might be undefined, and might be primitive, so check type
  if (item && typeof item === "object" && "avatar" in item) {
    return item.avatar;
  }
  return undefined; // or some fallback
});
</script>

<template>
  <UModal
    :open="isModalOpen"
    :dismissible="false"
    :title="editingTask ? 'Edit Task' : 'Add New Task'"
    :ui="{ footer: 'justify-end' }"
    @update:open="emit('update:isModalOpen', $event)"
  >
    <template #body>
      <UForm
        ref="formRef"
        :schema="taskSchema"
        :state="state"
        class="space-y-4"
        @submit="handleSave"
      >
        <UFormField label="Title" name="title" required>
          <UInput v-model="state.title" class="w-full" />
        </UFormField>
        <UFormField label="Description" name="description">
          <UTextarea v-model="state.description" class="w-full" />
        </UFormField>
        <UFormField
          v-if="!projectId"
          label="Project"
          name="project"
          description="You can assign this task to a project later."
        >
          <USelect
            v-model="state.project"
            :items="[
                  ...projects?.map((project: Project) => ({
                    label: project.title,
                    value: project.id,
                  })) ?? [],
                  {
                    label: '+ Create New Project',
                    value: '__create__',
                    onSelect: (e) => {
                      e?.preventDefault()
                        router.push({
                          path: '/projects',
                          query: {
                            ...route.query,
                            create: 'true',
                          },
                        });

                    }
                  }
                ]"
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
        <UFormField label="Priority" name="priority">
          <USelect
            v-model="state.priority"
            :items="[{ label: 'None', value: null }, ...priorityOptions]"
            class="w-full"
          />
        </UFormField>
        <UFormField label="Deadline" name="deadline">
          <CalendarFormFeild
            v-model="state.deadline"
            class="w-full bg-transparent"
          />
        </UFormField>
        <UFormField
          v-if="state.project || projectPage"
          label="Assignee"
          name="assignee"
        >
          <USelect
            v-model="state.assignee"
            :items="[{ label: 'None', value: null }, ...items]"
            class="w-full"
            :avatar="avatar"
          />
        </UFormField>
      </UForm>
    </template>
    <template #footer>
      <div class="flex justify-end gap-3 pt-2">
        <UButton
          label="Cancel"
          color="neutral"
          variant="outline"
          icon="i-heroicons-x-mark"
          @click="
            () => {
              emit('update:isModalOpen', false);
            }
          "
        />
        <UButton
          v-if="editingTask"
          label="Delete"
          color="error"
          icon="i-heroicons-trash"
          @click="() => handleDelete(editingTask!.id)"
        />
        <UButton
          label="Save"
          icon="i-heroicons-check"
          @click="() => formRef?.submit()"
        />
      </div>
    </template>
  </UModal>
</template>
