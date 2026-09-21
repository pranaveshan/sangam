import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { challengesAPI } from '../utils/api';
import StatusBadge from '../components/shared/StatusBadge';
import DemoBadge from '../components/shared/DemoBadge';
import AIAnalysisPanel from '../components/shared/AIAnalysisPanel';
import RagPanel from '../components/shared/RagPanel';
import LifecycleTracker from '../components/shared/LifecycleTracker';
import { formatNumber, provenanceLabel } from '../utils/formatters';

export default function ChallengeDetail() {
  const { id } = useParams();
  const [challenge, setChallenge] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [matches, setMatches] = useState([]);
  const [rag, setRag] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    (async () => {
      try {
        const { data } = await challengesAPI.get(id);
        setChallenge(data);
        if (data.ai_analysis) {
          setAnalysis(data.ai_analysis);
        }
        const re = await challengesAPI.reanalyze(id);
        setAnalysis(re.data.ai_analysis);
        setMatches(re.data.university_matches || []);
        setRag(re.data.rag || null);
      } catch (e) {
        setError(e.message);
      }
    })();
  }, [id]);

  if (error) return <p className="p-8 text-rose-700">{error}</p>;
  if (!challenge) return <p className="p-8 text-slate-600">Loading challenge…</p>;

  return (
    <div className="max-w-5xl mx-auto px-4 py-8 space-y-6">
      <Link to="/dashboard" className="text-sm text-blue-700 hover:underline">← Workspace</Link>
      <div className="panel p-6">
        <div className="flex flex-wrap justify-between gap-3">
          <div>
            <h1 className="font-display text-3xl font-bold">{challenge.title}</h1>
            <p className="text-slate-600 mt-2">{challenge.location} · {challenge.district}</p>
          </div>
          <div className="flex flex-col items-end gap-2">
            <StatusBadge status={challenge.status} />
            <DemoBadge label={provenanceLabel(challenge)} tone={challenge.is_demo ? 'amber' : 'green'} />
          </div>
        </div>
        <div className="mt-4">
          <LifecycleTracker current={challenge.status} />
        </div>
        <p className="mt-4 text-slate-800 whitespace-pre-wrap">{challenge.description}</p>
        <div className="mt-4 grid sm:grid-cols-3 gap-3 text-sm">
          <Info label="People affected" value={formatNumber(challenge.people_affected)} />
          <Info label="Urgency" value={challenge.urgency} />
          <Info label="Domain" value={challenge.domain || challenge.category} />
        </div>
        <p className="mt-4 text-sm"><span className="font-semibold">Community impact:</span> {challenge.community_impact}</p>
      </div>

      {analysis && (
        <AIAnalysisPanel analysis={analysis} matches={matches} />
      )}

      {rag && <RagPanel rag={rag} />}

      <div className="flex gap-3">
        <button className="btn-gov" onClick={async () => {
          await challengesAPI.validate(challenge.id, { action: 'validate' });
          const { data } = await challengesAPI.get(id);
          setChallenge(data);
        }}>
          Validate (Gov)
        </button>
        <Link className="btn-secondary" to="/dashboard">Continue in workspace</Link>
      </div>
    </div>
  );
}

function Info({ label, value }) {
  return (
    <div className="rounded-lg bg-slate-50 border p-3">
      <p className="text-[11px] uppercase text-slate-500">{label}</p>
      <p className="font-semibold mt-1">{value}</p>
    </div>
  );
}
