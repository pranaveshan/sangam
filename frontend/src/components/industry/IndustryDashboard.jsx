import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { challengesAPI, industryAPI, projectsAPI } from '../../utils/api';
import StatusBadge from '../shared/StatusBadge';
import DemoBadge from '../shared/DemoBadge';
import useStore from '../../context/store';

const SUPPORT_TYPES = [
  'mentorship',
  'technology',
  'equipment',
  'sponsorship',
  'collaboration_request',
];

export default function IndustryDashboard() {
  const { currentUser } = useStore();
  const [partners, setPartners] = useState([]);
  const [partnerId, setPartnerId] = useState(null);
  const [challenges, setChallenges] = useState([]);
  const [projects, setProjects] = useState([]);
  const [offer, setOffer] = useState({ project_id: '', support_type: 'mentorship', details: '' });

  const load = async () => {
    const [p, c, pr] = await Promise.all([
      industryAPI.partners(),
      challengesAPI.list(),
      projectsAPI.list(),
    ]);
    setPartners(p.data);
    const preferred =
      p.data.find((x) => x.name.includes('HydroSense')) || p.data[0];
    setPartnerId(preferred?.id || null);
    setChallenges(
      c.data.filter((x) =>
        ['validated', 'matched', 'university_accepted', 'team_formed', 'industry_collaboration', 'prototype', 'testing', 'pilot'].includes(x.status)
      )
    );
    setProjects(pr.data);
  };

  useEffect(() => { load(); }, []);

  const partner = partners.find((p) => p.id === partnerId);

  const submitOffer = async (e) => {
    e.preventDefault();
    if (!offer.project_id || !partnerId) return;
    await projectsAPI.addCollaboration(Number(offer.project_id), {
      partner_id: partnerId,
      support_type: offer.support_type,
      details:
        offer.details ||
        `${partner?.name} offers ${offer.support_type}. DEMO / PROTOTYPE — No real financial transactions.`,
    });
    setOffer({ project_id: '', support_type: 'mentorship', details: '' });
    await load();
  };

  const supported = projects.filter((p) =>
    (p.collaborations || []).some((c) => c.partner_id === partnerId)
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap justify-between gap-3">
        <div>
          <h2 className="font-display text-2xl font-bold text-sangam-industry">Industry / CSR Partner</h2>
          <p className="text-sm text-slate-600 mt-1">
            Browse validated challenges, support university proposals, track collaborations.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <DemoBadge label="Demo partners — no real payments" />
          <select className="input py-1.5 text-sm" value={partnerId || ''} onChange={(e) => setPartnerId(Number(e.target.value))}>
            {partners.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
          </select>
        </div>
      </div>

      {partner && (
        <div className="panel p-4 text-sm">
          <p className="font-semibold">{partner.name}</p>
          <p className="text-slate-600">{partner.description}</p>
          <p className="mt-1 text-amber-800 font-medium">{partner.notes}</p>
          <p className="mt-2">Support types: {(partner.support_types || []).join(', ')}</p>
        </div>
      )}

      <div className="grid lg:grid-cols-2 gap-4">
        <div className="panel p-4">
          <h3 className="font-semibold mb-3">Validated / active challenges</h3>
          <div className="space-y-2 max-h-80 overflow-y-auto">
            {challenges.map((c) => (
              <Link key={c.id} to={`/challenges/${c.id}`} className="block border rounded-lg p-3 hover:bg-slate-50">
                <div className="flex justify-between gap-2">
                  <span className="font-medium">{c.title}</span>
                  <StatusBadge status={c.status} />
                </div>
                <p className="text-sm text-slate-600">{c.domain} · {c.district}</p>
              </Link>
            ))}
          </div>
        </div>

        <div className="panel p-4">
          <h3 className="font-semibold mb-3">University proposals / projects</h3>
          <div className="space-y-2 max-h-80 overflow-y-auto">
            {projects.map((p) => (
              <Link key={p.id} to={`/projects/${p.id}`} className="block border rounded-lg p-3 hover:bg-slate-50">
                <div className="flex justify-between">
                  <span className="font-medium">{p.name}</span>
                  <StatusBadge status={p.status} />
                </div>
                <p className="text-sm text-slate-600 line-clamp-2">{p.proposal || p.goal}</p>
              </Link>
            ))}
          </div>
        </div>
      </div>

      <div className="panel p-4">
        <h3 className="font-semibold mb-3">Offer support / request collaboration</h3>
        <p className="text-xs text-amber-800 mb-3">
          REAL FUNCTIONALITY for recording offers · DEMO DATA for partner identity · FUTURE INTEGRATION for payments
        </p>
        <form onSubmit={submitOffer} className="grid md:grid-cols-2 gap-3">
          <select className="input" required value={offer.project_id}
            onChange={(e) => setOffer({ ...offer, project_id: e.target.value })}>
            <option value="">Select project</option>
            {projects.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
          </select>
          <select className="input" value={offer.support_type}
            onChange={(e) => setOffer({ ...offer, support_type: e.target.value })}>
            {SUPPORT_TYPES.map((s) => <option key={s} value={s}>{s}</option>)}
          </select>
          <textarea className="input md:col-span-2 min-h-[70px]" placeholder="Details (optional)"
            value={offer.details} onChange={(e) => setOffer({ ...offer, details: e.target.value })} />
          <button className="btn-industry" type="submit">Submit offer</button>
        </form>
      </div>

      <div className="panel p-4">
        <h3 className="font-semibold mb-3">Supported projects ({currentUser?.organization || partner?.name})</h3>
        {supported.length === 0 && <p className="text-sm text-slate-500">No active support recorded for this partner yet.</p>}
        <div className="space-y-2">
          {supported.map((p) => (
            <div key={p.id} className="border rounded-lg p-3">
              <Link to={`/projects/${p.id}`} className="font-medium hover:underline">{p.name}</Link>
              <ul className="mt-2 text-sm space-y-1">
                {(p.collaborations || [])
                  .filter((c) => c.partner_id === partnerId)
                  .map((c) => (
                    <li key={c.id} className="text-slate-700">
                      {c.support_type} · {c.status} · <span className="text-amber-800">{c.financial_note}</span>
                    </li>
                  ))}
              </ul>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
