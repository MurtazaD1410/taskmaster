<script setup lang="ts">
import { ref, computed } from "vue";
import draggable from "vuedraggable";
import { formatDeadline, isOverdue } from "~/helpers/utils";
import type { Project, Task, TaskPaginatedResponse } from "~/types/types";
import KanbanTaskCard from "./KanbanTaskCard.vue";
import { taskSchema } from "~/schemas/taskSchema";
import type { TaskSchema } from "~/schemas/taskSchema";
import type { FormSubmitEvent } from "@nuxt/ui";

const props = defineProps<{
  projects: Project[] | null;
}>();

const statusOptions = ref([
  { label: "Todo", value: "TODO" },
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
const { saveTask, deleteTask, changeTaskStatus } = useTaskService();
const authStore = useAuthStore();
const isSliderOpen = ref(false);
const route = useRoute();
const router = useRouter();
const editingTask = ref<Task | null>(null); // null when creating, holds a task when editing

const { user } = storeToRefs(authStore);

const getDefaultState = (): Partial<TaskSchema> => ({
  title: undefined,
  description: undefined,
  project: undefined,
  status: "TODO",
  priority: undefined,
  deadline: undefined,
});

const state = reactive<Partial<TaskSchema>>(getDefaultState());

watch(
  () => [editingTask.value],
  (isOpen) => {
    if (isOpen) {
      // When the modal opens, decide whether to load an editing task or reset the form.
      if (editingTask.value) {
        // Populate form for editing
        const task = editingTask.value;
        state.title = task.title;
        state.description = task.description || "";
        state.project = task.project_details?.id;
        state.status = task.status;
        state.priority = task.priority || undefined;
        state.deadline = task.deadline || undefined;
      } else {
        // Reset form for creating
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
    return $api(`/tasks/?author=${user.value?.id}&paginate=false`);
  },
  {
    watch: [user],
    server: false,
  }
);

const todoTasks = ref<Task[]>([]);
const inProgressTasks = ref<Task[]>([]);
const doneTasks = ref<Task[]>([]);

watch(
  // It's best practice to watch the .value directly for deep changes
  () => tasks.value,
  (newTasksArray) => {
    const allTasks: Task[] = newTasksArray ?? [];

    todoTasks.value = allTasks.filter((task) => task.status === "TODO");
    inProgressTasks.value = allTasks.filter(
      (task) => task.status === "IN_PROGRESS"
    );
    doneTasks.value = allTasks.filter((task) => task.status === "DONE");
  },
  {
    deep: true,
    immediate: true,
  }
);

async function handleTaskChange(event: any, newStatus: Task["status"]) {
  if (event.added) {
    console.log(event.added.element);
    const movedTask: Task = event.added.element;
    console.log(`Task "${movedTask.title}" was moved to status: ${newStatus}`);

    try {
      await changeTaskStatus(movedTask.id, newStatus);
      refresh();
    } catch (error) {
      console.error("Failed to update task status:", error);
    }
  }
}

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
</script>

<template>
  <div class="">
    <p class="text-gray-600 mb-4">KanbanView Example - Drag between lists</p>

    <div class="flex gap-3">
      <!-- Column 1 -->
      <div class="w-1/2 bg-gray-100 dark:bg-gray-800 rounded-lg min-h-[400px]">
        <div
          class="flex justify-between items-center border-b dark:border-gray-600 border-gray-300 p-3"
        >
          <!-- <h3 class="font-semibold flex gap-3 items-center">
            <UIcon name="i-heroicons-exclamation-circle text-2xl" size="xl" />
            Todo
          </h3> -->
          <UBadge
            :leading-icon="'i-heroicons-exclamation-circle'"
            size="xl"
            class="capitalize"
            color="error"
            variant="outline"
          >
            Todo
          </UBadge>
          <UButton
            icon="i-heroicons-plus"
            variant="subtle"
            @click="openCreateSlider('TODO')"
          />
        </div>
        <draggable
          v-model="todoTasks"
          group="tasks"
          :animation="200"
          ghost-class="ghost"
          item-key="id"
          :swap-threshold="0.7"
          class="min-h-[200px] pb-10 p-3"
          @change="(event:any) => handleTaskChange(event, 'TODO')"
        >
          <template #item="{ element: task }">
            <KanbanTaskCard :task="task" @click="openEditSlider(task)" />
          </template>
        </draggable>
      </div>

      <!-- Column 2 -->
      <div class="w-1/2 bg-gray-100 dark:bg-gray-800 rounded-lg min-h-[400px]">
        <div
          class="flex justify-between items-center border-b dark:border-gray-600 border-gray-300 p-3"
        >
          <!-- <h3 class="font-semibold flex gap-3 items-center">
            <UIcon name="i-heroicons-arrow-right-circle text-2xl" size="xl" />
            In Progress
          </h3> -->

          <UBadge
            :leading-icon="'i-heroicons-arrow-right-circle'"
            size="xl"
            class="capitalize"
            color="warning"
            variant="outline"
          >
            In Progress
          </UBadge>
          <UButton
            variant="subtle"
            icon="i-heroicons-plus"
            @click="openCreateSlider('IN_PROGRESS')"
          />
        </div>

        <draggable
          v-model="inProgressTasks"
          group="tasks"
          :animation="200"
          ghost-class="ghost"
          :swap-threshold="0.7"
          item-key="id"
          class="min-h-[200px] pb-10 p-3"
          @change="(event:any) => handleTaskChange(event, 'IN_PROGRESS')"
        >
          <template #item="{ element: task }">
            <KanbanTaskCard :task="task" @click="openEditSlider(task)" />
          </template>
        </draggable>
      </div>
      <div class="w-1/2 bg-gray-100 dark:bg-gray-800 rounded-lg min-h-[400px]">
        <div
          class="flex justify-between items-center border-b dark:border-gray-600 border-gray-300 p-3"
        >
          <!-- <h3 class="font-semibold flex gap-3 items-center">
            <UIcon name="i-heroicons-check-circle text-2xl" size="xl" />
            Done
          </h3> -->

          <UBadge
            :leading-icon="'i-heroicons-arrow-right-circle'"
            size="xl"
            class="capitalize"
            color="success"
            variant="outline"
          >
            Done
          </UBadge>
          <UButton
            variant="subtle"
            icon="i-heroicons-plus"
            @click="openCreateSlider('DONE')"
          />
        </div>
        <draggable
          v-model="doneTasks"
          group="tasks"
          :swap-threshold="0.7"
          :animation="200"
          ghost-class="ghost"
          item-key="id"
          class="min-h-[200px] pb-10 p-3"
          @change="(event:any) => handleTaskChange(event, 'DONE')"
        >
          <template #item="{ element: task }">
            <KanbanTaskCard :task="task" @click="openEditSlider(task)" />
          </template>
          <div class="h-16" />
        </draggable>
      </div>
    </div>
  </div>
  <USlideover
    v-model:open="isSliderOpen"
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
