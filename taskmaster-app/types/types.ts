export interface User {
  id: number;
  username: string;
  email: string;
  avatar: string;
}
export interface UserDetail {
  id: number;
  username: string;
  first_name: string;
  last_name: string;
  email: string;
  bio: string;
  avatar: string;
  created_at: string;
}

export interface RefreshTokenObject {
  access: string;
}

export interface Project {
  id: number;
  title: string;
  description?: string | null;
  task_count: number;
  owner: User;
  members: User[];
  created_at: Date;
}

export type TaskStatus = "TODO" | "BACKLOG" | "IN_PROGRESS" | "DONE";
export type TaskPriority = "L" | "M" | "H";
export type InvitationStatus = "P" | "A" | "D";

export interface TaskPaginatedResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Task[];
}
export interface Task {
  id: number;
  title: string;
  description?: string | null;
  status: TaskStatus;
  project_details: Project | null;
  priority?: TaskPriority | null;
  deadline?: string | null;
  assignee_details: User | null;
  author: User;
  created_at: Date;
}

export interface Invitation {
  id: number;
  email: string;
  project: ProjectBasic;
  invited_by: User;
  status: InvitationStatus;
  created_at: Date;
  token: string;
}
export interface ProjectBasic {
  id: number;
  title: string;
  description?: string | null;
  owner: User;
  created_at: Date;
}
