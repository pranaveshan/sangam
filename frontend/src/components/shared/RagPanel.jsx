import DemoBadge from './DemoBadge';

export default function RagPanel({ rag }) {
  if (!rag) return null;
  const sources = rag.sources || [];

  return (
    <div className="panel p-6 space-y-4 border-l-4 border-l-teal-700">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h3 className="font-display text-xl font-bold">RAG Assistant</h3>
          <p className="text-sm text-slate-600 mt-1">
            Retrieval-Augmented guidance from SANGAM knowledge + live platform data.
          </p>
        </div>
        <div className="flex gap-2">
          <DemoBadge label="Local RAG" tone="blue" />
          <DemoBadge label={rag.generation_mode === 'local' ? 'Local synthesis' : 'LLM + retrieved context'} tone="slate" />
        </div>
      </div>

      <div className="rounded-lg bg-teal-50 border border-teal-200 p-4 text-sm whitespace-pre-wrap text-teal-950">
        {rag.answer}
      </div>

      <div>
        <h4 className="text-sm font-semibold mb-2">Retrieved sources ({sources.length})</h4>
        <div className="space-y-2">
          {sources.map((s) => (
            <div key={s.chunk_id} className="rounded-lg border border-slate-200 bg-slate-50 p-3 text-sm">
              <div className="flex flex-wrap justify-between gap-2">
                <p className="font-medium">{s.title}</p>
                <span className="badge bg-white border border-slate-300">{s.score}%</span>
              </div>
              <p className="text-xs text-slate-500 mt-1">
                {s.source_type} · {s.domain} · {s.provenance}
              </p>
              <p className="text-slate-700 mt-2">{s.text}</p>
            </div>
          ))}
          {!sources.length && (
            <p className="text-sm text-slate-500">No sources above relevance threshold.</p>
          )}
        </div>
      </div>

      <p className="text-xs text-slate-500 border-t pt-3">
        {rag.disclaimer}
        {rag.stats && (
          <> · Indexed docs: {rag.stats.documents_indexed}, chunks: {rag.stats.chunks_indexed}</>
        )}
      </p>
    </div>
  );
}
