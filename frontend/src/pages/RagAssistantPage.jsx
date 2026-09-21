import { useEffect, useState } from 'react';
import { ragAPI } from '../utils/api';
import RagPanel from '../components/shared/RagPanel';
import DemoBadge from '../components/shared/DemoBadge';

const EXAMPLES = [
  'How should we respond to flood-damaged drinking water infrastructure?',
  'What university expertise fits a water quality IoT pilot?',
  'How does AquaGuard measure community impact after pilot?',
  'What industry support modes exist without real payments?',
];

export default function RagAssistantPage() {
  const [question, setQuestion] = useState(EXAMPLES[0]);
  const [domain, setDomain] = useState('');
  const [result, setResult] = useState(null);
  const [status, setStatus] = useState(null);
  const [docs, setDocs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [newDoc, setNewDoc] = useState({
    id: '',
    title: '',
    content: '',
    domain: 'Water',
    tags: 'custom, playbook',
  });

  const refreshMeta = async () => {
    const [s, d] = await Promise.all([ragAPI.status(), ragAPI.documents()]);
    setStatus(s.data);
    setDocs(d.data);
  };

  useEffect(() => {
    refreshMeta().catch((e) => setError(e.message));
  }, []);

  const ask = async (e) => {
    e?.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const { data } = await ragAPI.query({
        question,
        domain: domain || undefined,
        top_k: 5,
        prefer_llm: true,
        refresh_live_index: true,
      });
      setResult(data);
      await refreshMeta();
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  const reindex = async () => {
    await ragAPI.reindex();
    await refreshMeta();
  };

  const addDoc = async (e) => {
    e.preventDefault();
    const id = newDoc.id || `user-${Date.now()}`;
    await ragAPI.addDocument({
      id,
      title: newDoc.title,
      content: newDoc.content,
      domain: newDoc.domain,
      tags: newDoc.tags.split(',').map((t) => t.trim()).filter(Boolean),
      source_type: 'playbook',
      provenance: 'user',
    });
    setNewDoc({ id: '', title: '', content: '', domain: 'Water', tags: 'custom, playbook' });
    await refreshMeta();
  };

  return (
    <div className="max-w-5xl mx-auto px-4 py-8 space-y-6">
      <div className="flex flex-wrap justify-between gap-3">
        <div>
          <h1 className="font-display text-3xl font-bold">RAG Knowledge Assistant</h1>
          <p className="text-sm text-slate-600 mt-2">
            Ask questions grounded in SANGAM playbooks, policies, and live challenges/projects.
          </p>
        </div>
        <div className="flex gap-2 items-start">
          <DemoBadge label="Real retrieval" tone="green" />
          <button type="button" className="btn-secondary text-xs" onClick={reindex}>Reindex</button>
        </div>
      </div>

      {status && (
        <div className="panel p-4 grid sm:grid-cols-4 gap-3 text-sm">
          <Stat label="Documents" value={status.documents_indexed} />
          <Stat label="Chunks" value={status.chunks_indexed} />
          <Stat label="Retrieval" value={status.retrieval_method} />
          <Stat label="OpenAI key" value={status.openai_configured ? 'Configured' : 'Not set (local mode)'} />
        </div>
      )}

      <form onSubmit={ask} className="panel p-5 space-y-3">
        <label className="label">Question</label>
        <textarea
          className="input min-h-[90px]"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          required
        />
        <div className="flex flex-wrap gap-2">
          {EXAMPLES.map((ex) => (
            <button
              key={ex}
              type="button"
              className="badge bg-slate-100 border border-slate-200 text-slate-700 hover:bg-white"
              onClick={() => setQuestion(ex)}
            >
              {ex.slice(0, 42)}…
            </button>
          ))}
        </div>
        <div className="grid sm:grid-cols-2 gap-3">
          <div>
            <label className="label">Domain filter (optional)</label>
            <input className="input" value={domain} onChange={(e) => setDomain(e.target.value)} placeholder="Water" />
          </div>
        </div>
        {error && <p className="text-sm text-rose-700">{String(error)}</p>}
        <button className="btn-primary" type="submit" disabled={loading}>
          {loading ? 'Retrieving…' : 'Ask RAG'}
        </button>
      </form>

      {result && <RagPanel rag={result} />}

      <div className="grid lg:grid-cols-2 gap-4">
        <div className="panel p-4">
          <h3 className="font-semibold mb-3">Indexed documents</h3>
          <div className="max-h-80 overflow-y-auto space-y-2 text-sm">
            {docs.map((d) => (
              <div key={d.id} className="border rounded-lg p-2">
                <p className="font-medium">{d.title}</p>
                <p className="text-xs text-slate-500">{d.domain} · {d.source_type} · {d.provenance}</p>
              </div>
            ))}
          </div>
        </div>
        <form onSubmit={addDoc} className="panel p-4 space-y-2">
          <h3 className="font-semibold">Add knowledge document</h3>
          <p className="text-xs text-slate-500">USER-GENERATED — becomes searchable immediately.</p>
          <input className="input" placeholder="Title" required value={newDoc.title}
            onChange={(e) => setNewDoc({ ...newDoc, title: e.target.value })} />
          <textarea className="input min-h-[100px]" placeholder="Content" required value={newDoc.content}
            onChange={(e) => setNewDoc({ ...newDoc, content: e.target.value })} />
          <input className="input" placeholder="Domain" value={newDoc.domain}
            onChange={(e) => setNewDoc({ ...newDoc, domain: e.target.value })} />
          <input className="input" placeholder="Tags (comma-separated)" value={newDoc.tags}
            onChange={(e) => setNewDoc({ ...newDoc, tags: e.target.value })} />
          <button className="btn-uni" type="submit">Index document</button>
        </form>
      </div>
    </div>
  );
}

function Stat({ label, value }) {
  return (
    <div className="rounded-lg bg-slate-50 border p-3">
      <p className="text-[11px] uppercase text-slate-500">{label}</p>
      <p className="font-semibold mt-1 break-all">{value}</p>
    </div>
  );
}
