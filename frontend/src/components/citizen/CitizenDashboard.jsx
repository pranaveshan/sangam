import { Link } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { challengesAPI, projectsAPI } from '../../utils/api';
import StatusBadge from '../shared/StatusBadge';
import DemoBadge from '../shared/DemoBadge';

export default function CitizenDashboard() {
  const [mine, setMine] = useState([]);
  const [pilots, setPilots] = useState([]);

  useEffect(() => {
    challengesAPI.list().then((r) => setMine(r.data.slice(0, 8))).catch(() => {});
    projectsAPI.list().then((r) =>
      setPilots(r.data.filter((p) => ['pilot', 'testing', 'completed'].includes(p.status)))
    ).catch(() => {});
  }, []);

  return (
    <div className="space-y-8">
      <div className="flex flex-wrap justify-between gap-4 items-start">
        <div>
          <h2 className="font-display text-2xl font-bold text-sangam-citizen">Citizen Hub</h2>
          <p className="text-sm text-slate-600 mt-1">
            Speak, show, or type a community problem — then track how it moves toward solutions.
          </p>
        </div>
        <Link to="/report" className="btn-primary min-h-[48px]">
          Tell us what happened
        </Link>
      </div>

      <div className="panel p-6 flex flex-col sm:flex-row gap-4 items-center">
        <div className="flex-1">
          <h3 className="font-display text-lg font-semibold">Report without a long form</h3>
          <p className="text-sm text-slate-600 mt-1">
            Use your voice, a photo, or a short description. Confirm what we understood before submitting.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Link to="/report?mode=speak" className="btn-primary">🎙️ Speak</Link>
          <Link to="/report?mode=show" className="btn-secondary">📸 Show</Link>
          <Link to="/report?mode=type" className="btn-secondary">✍️ Type</Link>
        </div>
      </div>

      <div className="grid lg:grid-cols-2 gap-4">
        <div className="panel p-4">
          <h3 className="font-semibold mb-3">Recent challenges</h3>
          <div className="space-y-2">
            {mine.map((c) => (
              <Link key={c.id} to={`/challenges/${c.id}`} className="block border rounded-lg p-3 hover:bg-blue-50/40">
                <div className="flex justify-between gap-2">
                  <span className="font-medium">{c.title}</span>
                  <StatusBadge status={c.status} />
                </div>
                <div className="mt-1 flex gap-2">{c.is_demo ? <DemoBadge /> : <DemoBadge label="User-generated" tone="green" />}</div>
              </Link>
            ))}
          </div>
        </div>
        <div className="panel p-4">
          <h3 className="font-semibold mb-3">Pilots open for community feedback</h3>
          <div className="space-y-2">
            {pilots.map((p) => (
              <Link key={p.id} to={`/projects/${p.id}#feedback`} className="block border rounded-lg p-3 hover:bg-blue-50/40">
                <div className="font-medium">{p.name}</div>
                <p className="text-sm text-slate-600">{p.pilot_location || p.district}</p>
                <StatusBadge status={p.status} />
              </Link>
            ))}
            {!pilots.length && <p className="text-sm text-slate-500">No pilots yet.</p>}
          </div>
        </div>
      </div>
    </div>
  );
}
