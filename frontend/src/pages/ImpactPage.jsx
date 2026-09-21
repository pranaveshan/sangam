import { useEffect, useState } from 'react';
import { adminAPI } from '../utils/api';
import DemoBadge from '../components/shared/DemoBadge';
import { formatNumber } from '../utils/formatters';

export default function ImpactPage() {
  const [impact, setImpact] = useState(null);

  useEffect(() => {
    adminAPI.impact().then((r) => setImpact(r.data)).catch(() => {});
  }, []);

  if (!impact) return <p className="p-8">Loading impact…</p>;

  const items = [
    ['People affected (reported)', formatNumber(impact.people_affected)],
    ['Communities reached', impact.communities_reached],
    ['Projects completed', impact.projects_completed],
    ['Pilots deployed', impact.pilots_deployed],
    ['University teams', impact.university_teams],
    ['Industry partners (catalogue)', impact.industry_partners],
    ['Domains addressed', impact.domains_addressed],
    ['Districts covered', impact.districts_covered],
    ['Community feedback', impact.community_feedback],
    ['Average rating', impact.average_rating ?? '—'],
    ['Solution adoption signals', impact.solution_adoption],
  ];

  return (
    <div className="max-w-5xl mx-auto px-4 py-10">
      <div className="flex justify-between gap-3 mb-6">
        <div>
          <h1 className="font-display text-3xl font-bold">Impact Dashboard</h1>
          <p className="text-sm text-slate-600 mt-2">{impact.data_label}</p>
        </div>
        <DemoBadge />
      </div>
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {items.map(([label, value]) => (
          <div key={label} className="panel p-4">
            <p className="text-[11px] uppercase tracking-wide text-slate-500">{label}</p>
            <p className="text-2xl font-bold mt-2">{value}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
