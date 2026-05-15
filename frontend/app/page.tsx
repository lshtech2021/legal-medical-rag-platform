'use client';

import { useEffect, useState } from 'react';

type DocumentOut = { id: string; filename: string; content_type: string; created_at: string };
type Citation = { filename: string; page_number: number; chunk_id: number };
type ChronologyItem = { date: string; event: string; citations: Citation[] };

const API = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000/api/v1';
const API_KEY = process.env.NEXT_PUBLIC_INTERNAL_API_KEY ?? 'dev-internal-key';
const headers = { 'x-api-key': API_KEY };

export default function Home() {
  const [documents, setDocuments] = useState<DocumentOut[]>([]);
  const [question, setQuestion] = useState('Summarize key medical events.');
  const [answer, setAnswer] = useState('');
  const [citations, setCitations] = useState<Citation[]>([]);
  const [chronology, setChronology] = useState<ChronologyItem[]>([]);
  const [report, setReport] = useState('');

  async function refreshDocs() {
    const res = await fetch(`${API}/documents`, { headers });
    if (res.ok) setDocuments(await res.json());
  }
  useEffect(() => { refreshDocs(); }, []);

  async function uploadFile(file: File) {
    const fd = new FormData(); fd.append('file', file);
    await fetch(`${API}/documents`, { method: 'POST', body: fd, headers });
    await refreshDocs();
  }

  async function chat() {
    const res = await fetch(`${API}/chat`, { method: 'POST', headers: { ...headers, 'Content-Type': 'application/json' }, body: JSON.stringify({ question, top_k: 5 }) });
    const data = await res.json(); setAnswer(data.answer ?? ''); setCitations(data.citations ?? []);
  }

  async function generateChronology() {
    const res = await fetch(`${API}/chronology`, { method: 'POST', headers });
    const data = await res.json(); setChronology(data.items ?? []);
  }

  async function generateReport() {
    const res = await fetch(`${API}/reports`, { method: 'POST', headers: { ...headers, 'Content-Type': 'application/json' }, body: JSON.stringify({ prompt: question, format: 'medical_narrative' }) });
    const data = await res.json(); setReport(data.body ?? ''); setCitations(data.citations ?? []);
  }

  async function exportFile(kind: 'pdf' | 'docx') {
    const res = await fetch(`${API}/reports/export/${kind}`, { method: 'POST', headers: { ...headers, 'Content-Type': 'application/json' }, body: JSON.stringify({ prompt: question, format: 'medical_narrative' }) });
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a'); a.href = url; a.download = `report.${kind}`; a.click(); URL.revokeObjectURL(url);
  }

  return <main style={{ padding: 20, fontFamily: 'sans-serif' }}>
    <h1>Legal Medical RAG Platform</h1>
    <input type="file" onChange={(e) => e.target.files?.[0] && uploadFile(e.target.files[0])} />
    <h2>Uploaded Documents</h2><ul>{documents.map((d) => <li key={d.id}>{d.filename}</li>)}</ul>
    <h2>AI Chat</h2>
    <textarea value={question} onChange={(e) => setQuestion(e.target.value)} rows={4} cols={90} /><br />
    <button onClick={chat}>Generate Answer</button>
    <button onClick={generateChronology}>Generate Chronology</button>
    <button onClick={generateReport}>Generate Report</button>
    <button onClick={() => exportFile('docx')}>Export DOCX</button>
    <button onClick={() => exportFile('pdf')}>Export PDF</button>
    <button onClick={() => navigator.clipboard.writeText(report || answer)}>Copy Output</button>
    <h3>Answer</h3><pre>{answer}</pre>
    <h3>Report</h3><pre>{report}</pre>
    <h3>Chronology</h3><ul>{chronology.map((i, idx) => <li key={idx}>{i.date} — {i.event}</li>)}</ul>
    <h3>Citations</h3><ul>{citations.map((c, i) => <li key={`${c.chunk_id}-${i}`}>{c.filename} p.{c.page_number} (chunk #{c.chunk_id})</li>)}</ul>
  </main>;
}
