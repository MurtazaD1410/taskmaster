export interface User {
  id: number;
  username: string;
  email: string;
}

export interface RefreshTokenObject {
  access: string;
}

export interface Project {
  id: number;
  title: string;
  description?: string | null;
  author: User;
  created_at: Date;
}

export type TaskStatus = "TODO" | "IN_PROGRESS" | "DONE";

export interface Task {
  id: number;
  title: string;
  description?: string | null;
  status: TaskStatus;
  project_details: Project;
  author: User;
  created_at: Date;
}
