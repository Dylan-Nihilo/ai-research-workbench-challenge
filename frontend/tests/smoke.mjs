import assert from 'node:assert/strict';

const base = 'http://127.0.0.1:5173';
const json = { 'Content-Type': 'application/json' };
let taskId;

const page = await fetch(base);
assert.equal(page.status, 200);
assert.match(await page.text(), /id="root"/);
const health = await fetch(`${base}/api/health`);
assert.equal(health.status, 200);
assert.deepEqual(await health.json(), { status: 'ok' });

try {
  const created = await fetch(`${base}/api/tasks`, {
    method: 'POST', headers: json, body: JSON.stringify({ question: '容器联通验证' }),
  });
  assert.equal(created.status, 201);
  const task = await created.json();
  taskId = task.id;
  assert.equal(task.status, 'draft');

  const detail = await fetch(`${base}/api/tasks/${taskId}`);
  assert.deepEqual(await detail.json(), task);
  const list = await (await fetch(`${base}/api/tasks`)).json();
  assert.ok(list.some(item => item.id === taskId));

  const updated = await fetch(`${base}/api/tasks/${taskId}`, {
    method: 'PATCH', headers: json, body: JSON.stringify({ question: '容器联通验证已更新' }),
  });
  assert.equal(updated.status, 200);
  assert.equal((await updated.json()).question, '容器联通验证已更新');
  const invalid = await fetch(`${base}/api/tasks`, {
    method: 'POST', headers: json, body: JSON.stringify({ question: '' }),
  });
  assert.equal(invalid.status, 422);
} finally {
  if (taskId) {
    const removed = await fetch(`${base}/api/tasks/${taskId}`, { method: 'DELETE' });
    assert.equal(removed.status, 204);
  }
}

console.log('PASS: frontend, API proxy, task CRUD and input validation');
