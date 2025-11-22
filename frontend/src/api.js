import axios from 'axios';

const API_BASE = 'http://localhost:8000'; // adjust if backend runs elsewhere

export async function sendChat(message, history) {
  const payload = { question: message, history: history.map(m => [m.role, m.content]) };
  const res = await axios.post(`${API_BASE}/chat`, payload);
  return res.data; // { answer, sources }
}

export async function sendAgentChat(message, history) {
  const payload = { question: message, history: history.map(m => [m.role, m.content]) };
  const res = await axios.post(`${API_BASE}/agent_chat`, payload);
  return res.data; // { answer, sources }
}

export async function ingestPath(path) {
  const payload = { input_dir: path };
  const res = await axios.post(`${API_BASE}/ingest`, payload);
  return res.data; // { message, chunks_indexed, input_dir }
}
