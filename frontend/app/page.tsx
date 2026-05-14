'use client';

import { useEffect, useState } from 'react';

type DocumentOut = {
  id: string;
  filename: string;
  content_type: string;
  created_at: string;
};

type Citation = { filename: string; page_number: number; chunk_id: number };

const API = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000/api/v1';

export default function Home() {
  const [documents, setDocuments] = useState<DocumentOut[]>([]);
  const [question, setQuestion] = useState('Summarize key medical events.');
  const [answer, setAnswer] = useState('');
  const [citations, setCitations] = useState<Citation[]>([]);

  async function refreshDocs() {
    const res = await fetch(`${API}/documents`);
    if (res.ok) setDocuments(await res.json());
  }

  useEffect(() => {
    refreshDocs();
  }, []);

  async function uploadFile(file: File) {
    const fd = new FormData();
    fd.append('file', file);
    await fetch(`${API}/documents`, { method: 'POST', body: fd });
    await refreshDocs();
  }

  async function chat() {
    const res = await fetch(`${API}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, top_k: 5 }),
    });
    const data = await res.json();
    setAnswer(data.answer ?? '');
    setCitations(data.citations ?? []);
  }

  return (
    <main style={{ padding: 20, fontFamily: 'sans-serif' }}>
      <h1>Legal Medical RAG Platform (MVP)</h1>
      <input type="file" onChange={(e) => e.target.files?.[0] && uploadFile(e.target.files[0])} />

      <h2>Uploaded Documents</h2>
      <ul>
        {documents.map((doc) => (
          <li key={doc.id}>{doc.filename}</li>
        ))}
      </ul>

      <h2>Chat</h2>
      <textarea value={question} onChange={(e) => setQuestion(e.target.value)} rows={4} cols={80} />
      <br />
      <button onClick={chat}>Generate Answer</button>
      <button onClick={() => navigator.clipboard.writeText(answer)}>Copy Output</button>

      <pre>{answer}</pre>
      <h3>Citations</h3>
      <ul>
        {citations.map((c, i) => (
          <li key={`${c.chunk_id}-${i}`}>{c.filename} p.{c.page_number} (chunk #{c.chunk_id})</li>
        ))}
      </ul>
    </main>
  );
}
