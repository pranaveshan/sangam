import DemoBadge from './DemoBadge';

export default function AIAnalysisPanel({ analysis, matches = [], labels = {} }) {
  if (!analysis) return null;

  return (
    <div className="panel p-6 space-y-5 border-l-4 border-l-sangam-citizen">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h3 className="font-display text-xl font-bold">AI Analysis</h3>
          <p className="text-sm text-slate-600 mt-1">
            Local prototype intelligence — not an external LLM unless connected.
          </p>
        </div>
        <DemoBadge label="Prototype AI (local)" tone="blue" />
      </div>

      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-3">
        <Metric label="Domain" value={analysis.domain} />
        <Metric label="Subdomain" value={analysis.subdomain} />
        <Metric label="Priority" value={`${analysis.priority} (${analysis.priority_score})`} />
        <Metric label="Estimated Impact" value={analysis.estimated_impact} />
      </div>

      <div>
        <h4 className="text-sm font-semibold mb-2">Required Expertise</h4>
        <div className="flex flex-wrap gap-2">
          {(analysis.required_expertise || []).map((e) => (
            <span key={e} className="badge bg-blue-50 text-blue-900 border border-blue-200">{e}</span>
          ))}
        </div>
      </div>

      <div>
        <h4 className="text-sm font-semibold mb-2">
          Similar Reports: {analysis.similar_reports ?? analysis.similar_challenges?.length ?? 0}
        </h4>
        <div className="space-y-2">
          {(analysis.similar_challenges || []).map((s) => (
            <div key={s.id} className="rounded-lg border border-slate-200 p-3 text-sm bg-slate-50">
              <div className="flex justify-between gap-2">
                <p className="font-medium">{s.title}</p>
                <span className="badge bg-white border border-slate-300">{s.similarity}%</span>
              </div>
              <p className="text-slate-600 mt-1">{s.location} · {s.district}</p>
              <p className="text-sangam-accent mt-1 font-medium">{s.recommended_action}</p>
            </div>
          ))}
          {!analysis.similar_challenges?.length && (
            <p className="text-sm text-slate-500">No similar reports above threshold.</p>
          )}
        </div>
      </div>

      <div>
        <h4 className="text-sm font-semibold mb-2">Priority Factors (transparent scoring)</h4>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-slate-500 border-b">
                <th className="py-2 pr-3">Factor</th>
                <th className="py-2 pr-3">Value</th>
                <th className="py-2 pr-3">Weight</th>
                <th className="py-2">Contribution</th>
              </tr>
            </thead>
            <tbody>
              {(analysis.priority_factors || []).map((f) => (
                <tr key={f.factor} className="border-b border-slate-100">
                  <td className="py-2 pr-3 font-medium">{f.factor}</td>
                  <td className="py-2 pr-3 text-slate-600">{f.value}</td>
                  <td className="py-2 pr-3">{(f.weight * 100).toFixed(0)}%</td>
                  <td className="py-2">{f.contribution}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="rounded-lg bg-blue-50 border border-blue-200 p-3">
        <p className="text-sm font-semibold text-blue-950">Recommended Action</p>
        <p className="text-blue-900 mt-1">{analysis.recommended_action}</p>
      </div>

      {matches?.length > 0 && (
        <div>
          <div className="flex items-center gap-2 mb-2">
            <h4 className="text-sm font-semibold">University Matches</h4>
            <DemoBadge label="Demo institutions" />
          </div>
          <div className="space-y-2">
            {matches.map((m) => (
              <div key={m.university_id} className="rounded-lg border border-teal-200 bg-teal-50/50 p-3 text-sm">
                <div className="flex justify-between gap-2">
                  <p className="font-semibold text-teal-950">{m.university_name}</p>
                  <span className="badge bg-white border border-teal-300">Score {m.score}</span>
                </div>
                <p className="text-teal-900 mt-1">{m.explanation}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      <p className="text-xs text-slate-500 border-t pt-3">
        Methods: {analysis.classification_method} · {analysis.duplicate_method} · {analysis.matching_method}.{' '}
        {analysis.disclaimer}
        {labels?.ai ? ` · ${labels.ai}` : ''}
      </p>
    </div>
  );
}

function Metric({ label, value }) {
  return (
    <div className="rounded-lg bg-slate-50 border border-slate-200 p-3">
      <p className="text-[11px] uppercase tracking-wide text-slate-500">{label}</p>
      <p className="font-semibold mt-1 text-sm">{value || '—'}</p>
    </div>
  );
}
