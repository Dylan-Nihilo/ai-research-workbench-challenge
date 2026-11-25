import { useEffect, useState, type FormEvent } from "react";
import { createTask, getTask, listTasks, runTask, type Task } from "./api";

const statusNames: Record<Task["status"], string> = {
  draft: "待开始", queued: "排队中", running: "执行中", completed: "已完成", failed: "失败", cancelled: "已取消",
};

const errorMessage = (error: unknown) => error instanceof Error ? error.message : "操作失败，请重试。";

export default function App() {
  const [question, setQuestion] = useState("");
  const [tasks, setTasks] = useState<Task[]>([]);
  const [selectedId, setSelectedId] = useState(() => new URLSearchParams(location.search).get("task"));
  const [task, setTask] = useState<Task | null>(null);
  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);
  const [detailVersion, setDetailVersion] = useState(0);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function refreshList() {
    setLoading(true);
    try { setTasks(await listTasks()); }
    catch (err) { setError(errorMessage(err)); }
    finally { setLoading(false); }
  }

  useEffect(() => { void refreshList(); }, []);

  useEffect(() => {
    if (!task || !["running", "queued"].includes(task.status)) return;
    const controller = new AbortController();
    const timer = window.setInterval(() => {
      getTask(task.id, controller.signal).then((updated) => {
        if (controller.signal.aborted) return;
        setTask(updated);
        setTasks((items) => items.map((item) => item.id === updated.id ? updated : item));
      }).catch((err) => { if (!controller.signal.aborted) setError(errorMessage(err)); });
    }, 2000);
    return () => { controller.abort(); window.clearInterval(timer); };
  }, [task?.id, task?.status]);

  useEffect(() => {
    if (!selectedId) return;
    const controller = new AbortController();
    setTask(null);
    setDetailLoading(true);
    getTask(selectedId, controller.signal).then(setTask).catch((err) => {
      if (!controller.signal.aborted) setError(errorMessage(err));
    }).finally(() => { if (!controller.signal.aborted) setDetailLoading(false); });
    return () => controller.abort();
  }, [selectedId, detailVersion]);

  function selectTask(id: string) {
    setError("");
    setSelectedId(id);
    const url = new URL(location.href);
    url.searchParams.set("task", id);
    history.replaceState(null, "", url);
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (busy || !question.trim()) return;
    setBusy(true);
    setError("");
    try {
      const created = await createTask(question);
      setTasks((items) => [created, ...items]);
      setQuestion("");
      selectTask(created.id);
    } catch (err) { setError(errorMessage(err)); }
    finally { setBusy(false); }
  }

  async function start() {
    if (!task || busy) return;
    setBusy(true);
    setError("");
    try {
      const updated = await runTask(task.id);
      setTask(updated);
      setTasks((items) => items.map((item) => item.id === updated.id ? updated : item));
    }
    catch (err) { setError(errorMessage(err)); }
    finally { setBusy(false); }
  }

  return <>
    <header className="topbar"><div className="brand-mark" aria-hidden="true">研</div><span>信息调研工作台</span></header>
    <main>
      <section className="compose" aria-labelledby="new-task">
        <h1 id="new-task">创建调研任务</h1>
        <form onSubmit={submit}>
          <label htmlFor="question">你想了解什么？</label>
          <textarea id="question" value={question} onChange={(event) => setQuestion(event.target.value)}
            rows={3} maxLength={2000} required placeholder="输入需要调研的问题" />
          <div className="form-footer"><span>{question.length} / 2000</span><button type="submit" disabled={busy || !question.trim()}>{busy ? "处理中…" : "创建任务"}</button></div>
        </form>
      </section>
      {error && <p className="error" role="alert">{error}</p>}
      <div className="workspace">
        <aside aria-label="任务列表">
          <div className="section-head"><h2>任务</h2><button className="text-button" onClick={() => void refreshList()} disabled={loading}>刷新列表</button></div>
          {loading ? <p className="muted" role="status">正在读取任务…</p> : tasks.length === 0 ? <p className="muted">还没有任务。先创建一项调研。</p> :
            <ul className="task-list">{tasks.map((item) => <li key={item.id}><button className={`task-item ${item.id === selectedId ? "selected" : ""}`} onClick={() => selectTask(item.id)} aria-current={item.id === selectedId ? "true" : undefined}>
              <span className="task-title">{item.question}</span><span className="task-meta">{statusNames[item.status]}</span>
            </button></li>)}</ul>}
        </aside>
        <section className="detail" aria-labelledby="task-detail">
          <div className="section-head"><h2 id="task-detail">任务详情</h2>{selectedId && <button className="text-button" onClick={() => { setError(""); setDetailVersion((value) => value + 1); }} disabled={detailLoading}>刷新详情</button>}</div>
          {detailLoading ? <p className="muted" role="status">正在读取详情…</p> : !task ? <p className="muted">选择一项任务，查看问题与结果。</p> : <>
            <div className="task-heading"><span className="status">{statusNames[task.status]}</span><p className="muted">{new Date(task.created_at).toLocaleString("zh-CN")}</p></div>
            <h3>{task.question}</h3>
            {["draft", "failed"].includes(task.status) && <button onClick={() => void start()} disabled={busy}>{task.status === "failed" ? "重试调研" : "开始调研"}</button>}
            <p className="muted" role="status">当前阶段：{task.stage}</p>
            {task.error && <p className="error" role="alert">{task.error.message}</p>}
            {task.events.length > 0 && <details><summary>执行记录</summary><ol>{task.events.map((event) => <li key={event.id}>{new Date(event.created_at).toLocaleTimeString("zh-CN")} · {event.message}</li>)}</ol></details>}
            <div className="report"><h4>调研结果</h4>{task.report ? <p className="report-text">{task.report}</p> : <p className="muted">任务完成后可在这里查看结果。</p>}</div>
            {task.sources.length > 0 && <section className="sources"><h4>引用来源</h4><p className="muted">报告中的 [编号] 对应下列来源。链接由检索服务提供，请结合原文核对。</p><ol>{task.sources.map((source) => <li key={source.id}><a href={/^https?:\/\//i.test(source.url) ? source.url : undefined} target="_blank" rel="noopener noreferrer">[{source.id}] {source.title}</a><p className="muted">检索于 {new Date(source.fetched_at).toLocaleString("zh-CN")}</p></li>)}</ol></section>}
          </>}
        </section>
      </div>
    </main>
  </>;
}
