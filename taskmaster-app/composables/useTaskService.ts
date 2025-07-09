import type { FormSubmitEvent } from "@nuxt/ui";
import type { TaskSchema } from "~/schemas/taskSchema";
import type { Task } from "~/types/types";

export const useTaskService = () => {
  const toast = useToast();
  const { $api } = useNuxtApp();

  const saveTask = async (
    payload: FormSubmitEvent<TaskSchema>,
    taskId?: number
  ) => {
    try {
      if (taskId) {
        await $api(`tasks/${taskId}/`, {
          method: "PUT",
          body: payload.data,
        });
        toast.add({ title: "Task updated successfully", color: "success" });
      } else {
        await $api("tasks/", {
          method: "POST",
          body: payload.data,
        });
        toast.add({ title: "Task created successfully", color: "success" });
      }
    } catch (error: any) {
      const errorData = error.response?._data;
      const errorMessage = errorData
        ? Object.values(errorData).flat().join(" ")
        : "An unknown error occurred.";

      toast.add({
        title: "An error occurred",
        description: errorMessage,
        color: "error",
      });

      throw error;
    }
  };

  async function deleteTask(taskId: number) {
    if (!confirm("Are you sure you want to delete this task?")) return;

    try {
      await $api(`tasks/${taskId}/`, {
        method: "DELETE",
      });
      toast.add({ title: "Task deleted Successfully!", color: "success" });
    } catch (error: any) {
      const errorData = error?.response?._data;
      const errorMessage = errorData
        ? Object.values(errorData).flat().join(" ")
        : "An unknown error occurred.";
      toast.add({
        title: "Could not delete Task",
        description: errorMessage,
        color: "error",
      });
      throw error;
    }
  }

  async function updateColumnOnBackend(
    columnStatus: Task["status"],
    tasksInColumn: Task[]
  ) {
    const orderedIds = tasksInColumn.map((task) => task.id);
    const payload = {
      status: columnStatus,
      ordered_ids: orderedIds,
    };

    console.log(payload);

    try {
      await $api("/tasks/update-order/", {
        method: "POST",
        body: payload,
      });
    } catch (error) {
      console.error(
        `Failed to update order for column ${columnStatus}:`,
        error
      );
    }
  }

  return {
    saveTask,
    deleteTask,
    updateColumnOnBackend,
  };
};
