import z from "zod";

export const taskSchema = z.object({
  title: z.string().min(1, "Title is required"),
  description: z.string().optional(),
  project: z.number().optional(),
  status: z.enum(["TODO", "BACKLOG", "IN_PROGRESS", "DONE"]),
  priority: z.enum(["L", "M", "H"]).optional(),
  deadline: z.string().optional(),
});

export type TaskSchema = z.infer<typeof taskSchema>;
