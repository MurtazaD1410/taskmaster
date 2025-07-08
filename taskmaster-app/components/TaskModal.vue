<script setup lang="ts">
import { reactive, watch } from "vue";
import type { FormSubmitEvent } from "@nuxt/ui";
import { taskSchema } from "~/schemas/taskSchema";
import type { TaskSchema } from "~/schemas/taskSchema";
import type { Project, Task } from "~/types/types";
import { de } from "@nuxt/ui/runtime/locale/index.js";

const route = useRoute();
const router = useRouter();
const { saveTask, deleteTask } = useTaskService();

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

const props = defineProps<{
  isModalOpen: boolean;
  editingTask: Task | null;
  projects: Project[] | null;
  projectId: string | null;
  currentTab: "ALL" | "TODO" | "IN_PROGRESS" | "DONE";
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

console.log(props.projectId);
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
        state.deadline = task.deadline || undefined;
      } else {
        // Reset form for creating
        Object.assign(state, getDefaultState());
      }
    }
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

        <div class="flex justify-end gap-3 pt-4">
          <UButton
            label="Cancel"
            color="neutral"
            variant="outline"
            icon="i-heroicons-x-mark"
            @click="emit('update:isModalOpen', false)"
          />
          <UButton
            v-if="editingTask"
            label="Delete"
            color="error"
            icon="i-heroicons-trash"
            @click="() => handleDelete(editingTask!.id)"
          />
          <UButton type="submit" label="Save" icon="i-heroicons-check" />
        </div>
      </UForm>
    </template>
  </UModal>
</template>
