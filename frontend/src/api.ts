export type Task = {
  id: string;
  question: string;
  status: "draft" | "queued" | "running" | "completed" | "failed" | "cancelled";
  stage: string;
  report: string | null;
  sources: { id: string; title: string; url: string; excerpt: string; fetched_at: string; published_at: string | null }[];
  events: { id: string; stage: string; message: string; created_at: string }[];
  error: { code: string; message: string } | null;
  created_at: string;
  updated_at: string;
};

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`/api${path}`, options);
  const body = await response.json();
  if (!response.ok) throw new Error(body.error?.message || `请求失败（${response.status}）`);
  return body as T;
}

export const listTasks = () => request<Task[]>("/tasks");
export const getTask = (id: string, signal?: AbortSignal) => request<Task>(`/tasks/${encodeURIComponent(id)}`, { signal });
export const createTask = (question: string) => request<Task>("/tasks", {
  method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ question }),
});
export const runTask = (id: string) => request<Task>(`/tasks/${encodeURIComponent(id)}/run`, { method: "POST" });
