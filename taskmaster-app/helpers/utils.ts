import type { Task } from "~/types/types";

export const isOverdue = (deadline: string) => {
  if (!deadline) return false;
  return new Date(deadline) < new Date();
};

export const formatDeadline = (deadline: string) => {
  if (!deadline) return "";

  const date = new Date(deadline);
  const now = new Date();
  const diffTime = date.getTime() - now.getTime();
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

  if (diffDays < 0) {
    return `${Math.abs(diffDays)} days overdue`;
  } else if (diffDays === 0) {
    return "Due today";
  } else if (diffDays === 1) {
    return "Due tomorrow";
  } else if (diffDays <= 7) {
    return `Due in ${diffDays} days`;
  } else {
    return date.toLocaleDateString();
  }
};

export const formatDate = (date: string) => {
  if (!date) return "";

  const dateObj = new Date(date);
  const options: Intl.DateTimeFormatOptions = {
    year: "numeric",
    month: "short",
    day: "numeric",
  };

  return dateObj.toLocaleDateString("en-US", options);
};

export const getIconAndColorForStatus = (
  status: Task["status"]
): {
  color:
    | "error"
    | "primary"
    | "secondary"
    | "success"
    | "info"
    | "warning"
    | "neutral"
    | undefined;
  icon: string;
  label: string;
} => {
  switch (status) {
    case "TODO":
      return {
        color: "error",
        icon: "i-heroicons-exclamation-circle",
        label: "Todo",
      };
    case "BACKLOG":
      return {
        color: "secondary",
        icon: "i-heroicons-clock",
        label: "Backlog",
      };
    case "IN_PROGRESS":
      return {
        color: "warning",
        icon: "i-heroicons-arrow-right-circle",
        label: "In Progress",
      };
    case "DONE":
      return {
        color: "success",
        icon: "i-heroicons-check-circle",
        label: "Done",
      };
  }
};
