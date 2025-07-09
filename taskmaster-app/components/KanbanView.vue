<script setup lang="ts">
import { ref } from "vue";
import draggable from "vuedraggable";
import type { Project, Task } from "~/types/types";
import KanbanTaskCard from "./KanbanTaskCard.vue";
import { taskSchema } from "~/schemas/taskSchema";
import type { TaskSchema } from "~/schemas/taskSchema";
import type { FormSubmitEvent } from "@nuxt/ui";
import { getIconAndColorForStatus } from "~/helpers/utils";

const props = defineProps<{
  projects: Project[] | null;
  projectPage?: boolean;
  projectId?: number;
}>();

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

const formRef = ref();
const { $api } = useNuxtApp();
const { saveTask, deleteTask, updateColumnOnBackend } = useTaskService();
const authStore = useAuthStore();
const isSliderOpen = ref(false);
const route = useRoute();
const router = useRouter();
const editingTask = ref<Task | null>(null); // null when creating, holds a task when editing

const { user } = storeToRefs(authStore);

const getDefaultState = (): Partial<TaskSchema> => ({
  title: undefined,
  description: undefined,
  project: props.projectId || undefined,
  status: "TODO",
  priority: undefined,
  deadline: undefined,
});

const state = reactive<Partial<TaskSchema>>(getDefaultState());

watch(
  () => [editingTask.value],
  (isOpen) => {
    if (isOpen) {
      if (editingTask.value) {
        const task = editingTask.value;
        state.title = task.title;
        state.description = task.description || "";
        state.project = task.project_details?.id;
        state.status = task.status;
        state.priority = task.priority || undefined;
        state.deadline = task.deadline || undefined;
      } else {
        Object.assign(state, getDefaultState());
      }
    }
  }
);

const {
  data: tasks,
  pending,
  error,
  refresh,
} = useAsyncData<Array<Task>>(
  () => `tasks-kanban`,
  () => {
    let url = `/tasks/?author=${user.value?.id}&paginate=false`;

    if (props.projectPage) {
      url = `/tasks/?project=${props.projectId}&paginate=false`;
    }
    return $api(url);
  },
  {
    watch: [user],
    server: false,
  }
);

const columns = reactive<{ [key in Task["status"]]: Task[] }>({
  TODO: [],
  BACKLOG: [],
  IN_PROGRESS: [],
  DONE: [],
});

watch(
  () => tasks.value,
  (newTasksArray) => {
    const allTasks = newTasksArray ?? [];

    // Reset all columns first to handle deletions
    columns.TODO = [];
    columns.BACKLOG = [];
    columns.IN_PROGRESS = [];
    columns.DONE = [];

    // Distribute tasks into the correct column
    for (const task of allTasks) {
      if (columns[task.status]) {
        columns[task.status].push(task);
      }
    }
  },
  { deep: true, immediate: true }
);

function openEditSlider(task: Task) {
  editingTask.value = task; // Set the task to be edited
  isSliderOpen.value = true;
}

function openCreateSlider(status: Task["status"]) {
  editingTask.value = null;
  state.status = status;
  isSliderOpen.value = true;
}

async function handleSave(event: FormSubmitEvent<TaskSchema>) {
  try {
    await saveTask(event, editingTask.value?.id);
    isSliderOpen.value = false;
    refresh();
  } catch (error) {
    console.error("Save task failed, keeping modal open.");
  }
}

async function handleDelete(taskId: number) {
  try {
    await deleteTask(taskId);
    isSliderOpen.value = false;
    refresh();
  } catch (error) {
    console.error("Save task failed, keeping modal open.");
  }
}

const dragInfo = ref<{ fromColumnStatus: string | null }>({
  fromColumnStatus: null,
});

function onDragStart(event: any, columnStatus: Task["status"]) {
  dragInfo.value.fromColumnStatus = columnStatus;
}

// --- 3. THE CLEANER onDragEnd HANDLER ---
async function onDragEnd(event: any, toStatus: Task["status"]) {
  const fromStatus = dragInfo.value.fromColumnStatus;

  if (!fromStatus || !toStatus) {
    console.error("Could not determine source or destination column status.");
    return;
  }

  const destTasks = columns[toStatus];
  await updateColumnOnBackend(toStatus, destTasks);

  if (fromStatus !== toStatus) {
    const sourceTasks = columns[fromStatus as Task["status"]];
    await updateColumnOnBackend(fromStatus as Task["status"], sourceTasks);
  }

  refresh();
  dragInfo.value.fromColumnStatus = null;
}

async function handleTaskChange(event: any, columnStatus: Task["status"]) {
  // This function will be called MULTIPLE times during a single drag-and-drop
  // between columns: once for the 'removed' event on the source column, and
  // once for the 'added' event on the destination column.

  if (event.added) {
    // --- A TASK WAS ADDED TO THIS COLUMN ---
    // The `v-model` has already updated the local array.
    // We just need to tell the backend about the new state of this column.
    console.log(`Task ADDED to ${columnStatus}. Updating backend.`);
    const tasksInColumn = columns[columnStatus];
    await updateColumnOnBackend(columnStatus, tasksInColumn);
  } else if (event.removed) {
    // --- A TASK WAS REMOVED FROM THIS COLUMN ---
    // Same logic applies. The local array is already updated (the task is gone).
    // We tell the backend about the new state of this source column.
    console.log(`Task REMOVED from ${columnStatus}. Updating backend.`);
    const tasksInColumn = columns[columnStatus];
    await updateColumnOnBackend(columnStatus, tasksInColumn);
  } else if (event.moved) {
    // --- A TASK WAS RE-ORDERED WITHIN THIS COLUMN ---
    // Same logic again. The local array is already re-ordered.
    // Tell the backend about the new order.
    console.log(`Task MOVED within ${columnStatus}. Updating backend.`);
    const tasksInColumn = columns[columnStatus];
    await updateColumnOnBackend(columnStatus, tasksInColumn);
  }
}
</script>

<template>
  <div class="">
    <p class="text-gray-600 mb-4">Kanban - Organize your tasks easily</p>

    <div
      class="flex gap-3 overflow-x-scroll"
      :style="{ scrollbarWidth: 'none' }"
    >
      <div
        v-for="(tasksInColumn, status) in columns"
        :key="status"
        class="flex-1 min-w-xs bg-gray-100 dark:bg-gray-800 rounded-lg"
      >
        <div
          class="flex justify-between items-center border-b dark:border-gray-600 border-gray-300 p-3"
        >
          <UBadge
            :leading-icon="getIconAndColorForStatus(status).icon"
            size="xl"
            class="capitalize"
            :color="getIconAndColorForStatus(status).color"
            variant="outline"
            :ui="{
              leadingIcon: 'text-xl',
            }"
          >
            {{ getIconAndColorForStatus(status).label }}
          </UBadge>
          <UButton
            icon="i-heroicons-plus"
            variant="subtle"
            @click="openCreateSlider(status)"
          />
        </div>
        <draggable
          v-model="columns[status]"
          group="tasks"
          :animation="200"
          ghost-class="ghost"
          item-key="id"
          :swap-threshold="0.7"
          class="min-h-[200px] pb-10 p-3"
          @change="handleTaskChange($event, status)"
        >
          <template #item="{ element: task }">
            <KanbanTaskCard :task="task" @click="openEditSlider(task)" />
          </template>
        </draggable>
      </div>
    </div>
  </div>
  <USlideover
    v-model:open="isSliderOpen"
    :dismissible="false"
    :ui="{ footer: 'justify-end' }"
    :title="editingTask ? 'Edit Task' : 'Add New Task'"
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
          v-if="!projectPage"
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
            :items="priorityOptions"
            class="w-full"
          />
        </UFormField>
        <UFormField label="Deadline" name="deadline">
          <CalendarFormFeild
            v-model="state.deadline"
            class="w-full bg-transparent"
          />
        </UFormField>
      </UForm>
      <div v-if="editingTask?.author" class="my-4 flex items-center space-x-3">
        <UAvatar
          :src="editingTask.author.avatar"
          :alt="editingTask.author.username"
          size="md"
        />
        <div>
          <p class="text-sm font-medium text-gray-700">Created by</p>
          <p class="text-sm text-gray-500">{{ editingTask.author.username }}</p>
        </div>
      </div>
    </template>
    <template #footer="{ close }">
      <UButton
        label="Cancel"
        color="neutral"
        variant="outline"
        icon="i-heroicons-x-mark"
        @click="close"
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
    </template>
  </USlideover>
</template>
