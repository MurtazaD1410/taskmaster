import type { InjectionKey } from "vue";
import type { Task } from "~/types/types";

// 1. Define and export the InjectionKey from this central file.
// Its type describes the function signature: a function that takes a Task and returns void.
export const OpenEditModalKey: InjectionKey<(task: Task) => void> =
  Symbol("OpenEditModalKey");
