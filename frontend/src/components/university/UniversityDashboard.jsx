import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { challengesAPI, projectsAPI, universitiesAPI } from '../../utils/api';
import StatusBadge from '../shared/StatusBadge';
import DemoBadge from '../shared/DemoBadge';
import useStore from '../../context/store';

export default function UniversityDashboard() {
  const { currentUser } = useStore();
  const [universities, setUniversities] = useState([]);
  const [selectedUni, setSelectedUni] = useState(null);
  const [challenges, setChallenges] = useState([]);
  const [projects, setProjects] = useState([]);
  const [domainFilter, setDomainFilter] = useState('');
  const [accepting, setAccepting] = useState(null);
  const [form, setForm] = useState({ project_name: '', goal: '', proposal: '' });

  const load = async (uniId) => {
    const [u, c, p] = await Promise.all([
      universitiesAPI.list(),
      challengesAPI.list(),
      projectsAPI.list(uniId ? { university_id: uniId } : {}),
    ]);
    setUniversities(u.data);
    const uni = uniId
      ? u.data.find((x) => x.id === uniId)
      : u.data.find((x) => x.short_name === 'DTU-DEMO') || u.data[0];
    setSelectedUni(uni);
    setChallenges(
      c.data.filter((ch) =>
        ['validated', 'matched', 'under_review'].includes(ch.status)
      )
    );
    setProjects(p.data.filter((pr) => !uni || pr.university_id === uni.id));
  };

  useEffect(() => { load(); }, []);

  const filtered = challenges.filter((c) =>
    !domainFilter || (c.domain || '').toLowerCase().includes(domainFilter.toLowerCase())
  );

  const startAccept = (c) => {
    setAccepting(c);
    setForm({
      project_name: c.domain?.includes('Water') ? 'AquaGuard' : `${c.category} Response Team`,
      goal: `Address: ${c.title}`,
      proposal: `Multidisciplinary proposal for ${c.domain || c.category}. Faculty mentorship and student team to be assigned.`,
    });
  };

  const submitAccept = async () => {
    if (!selectedUni || !accepting) return;
    const analysis = accepting.ai_analysis || {};
    await projectsAPI.accept(accepting.id, {
      university_id: selectedUni.id,
      project_name: form.project_name,
      goal: form.goal,
      proposal: form.proposal,
      match_explanation:
        analysis.recommended_action
          ? `Matched because the institution has relevant ${accepting.required_expertise?.slice(0, 2).join(' + ') || 'domain'} expertise.`
          : `Matched to ${selectedUni.name} based on structured expertise overlap (DEMO).`,
      match_score: 85,
    });
    setAccepting(null);
    await load(selectedUni.id);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap justify-between gap-3">
        <div>
          <h2 className="font-display text-2xl font-bold text-sangam-uni">University Workspace</h2>
          <p className="text-sm text-slate-600 mt-1">
            {selectedUni?.name || 'Select institution'} · {currentUser?.name || 'University user'}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <DemoBadge label="Demo institutions" />
          <select
            className="input py-1.5 text-sm"
            value={selectedUni?.id || ''}
            onChange={(e) => load(Number(e.target.value))}
          >
            {universities.map((u) => (
              <option key={u.id} value={u.id}>{u.short_name}</option>
            ))}
          </select>
        </div>
      </div>

      {selectedUni && (
        <div className="panel p-4 text-sm">
          <p className="font-semibold">{selectedUni.name}</p>
          <p className="text-slate-600 mt-1">{selectedUni.notes}</p>
          <p className="mt-2"><span className="font-medium">Departments:</span> {(selectedUni.departments || []).join(', ')}</p>
          <p><span className="font-medium">Research:</span> {(selectedUni.research_areas || []).join(', ')}</p>
        </div>
      )}

      <div className="flex gap-2 items-center">
        <label className="text-sm font-medium">Filter by domain</label>
        <input
          className="input max-w-xs py-1.5"
          placeholder="e.g. Water"
          value={domainFilter}
          onChange={(e) => setDomainFilter(e.target.value)}
        />
      </div>

      <div className="grid lg:grid-cols-2 gap-4">
        <div className="panel p-4">
          <h3 className="font-semibold mb-3">Assignable / matched challenges</h3>
          <div className="space-y-3 max-h-[480px] overflow-y-auto">
            {filtered.map((c) => (
              <div key={c.id} className="border rounded-lg p-3">
                <div className="flex justify-between gap-2">
                  <Link to={`/challenges/${c.id}`} className="font-medium hover:underline">{c.title}</Link>
                  <StatusBadge status={c.status} />
                </div>
                <p className="text-sm text-slate-600 mt-1">{c.domain} · {c.district}</p>
                {c.ai_analysis?.recommended_action && (
                  <p className="text-xs text-teal-800 mt-2">
                    AI: {c.ai_analysis.recommended_action}
                    {c.required_expertise?.length ? ` · Expertise: ${c.required_expertise.slice(0, 3).join(', ')}` : ''}
                  </p>
                )}
                <button className="btn-uni text-xs mt-3" onClick={() => startAccept(c)}>
                  Accept challenge
                </button>
              </div>
            ))}
            {!filtered.length && <p className="text-sm text-slate-500">No challenges match filter.</p>}
          </div>
        </div>

        <div className="panel p-4">
          <h3 className="font-semibold mb-3">University projects</h3>
          <div className="space-y-2">
            {projects.map((p) => (
              <Link key={p.id} to={`/projects/${p.id}`} className="block border rounded-lg p-3 hover:bg-teal-50/40">
                <div className="flex justify-between">
                  <span className="font-medium">{p.name}</span>
                  <StatusBadge status={p.status} />
                </div>
                <p className="text-sm text-slate-600">{p.team_name || 'No team yet'} · {p.match_explanation?.slice(0, 100)}…</p>
                {p.is_demo && <DemoBadge />}
              </Link>
            ))}
            {!projects.length && <p className="text-sm text-slate-500">No projects yet.</p>}
          </div>
        </div>
      </div>

      {accepting && (
        <div className="fixed inset-0 bg-slate-900/40 z-50 flex items-center justify-center p-4">
          <div className="panel p-6 max-w-lg w-full space-y-3">
            <h3 className="font-display text-xl font-bold">Accept: {accepting.title}</h3>
            <input className="input" placeholder="Project name" value={form.project_name}
              onChange={(e) => setForm({ ...form, project_name: e.target.value })} />
            <textarea className="input min-h-[80px]" placeholder="Goal" value={form.goal}
              onChange={(e) => setForm({ ...form, goal: e.target.value })} />
            <textarea className="input min-h-[80px]" placeholder="Solution proposal" value={form.proposal}
              onChange={(e) => setForm({ ...form, proposal: e.target.value })} />
            <div className="flex gap-2 justify-end">
              <button className="btn-secondary" onClick={() => setAccepting(null)}>Cancel</button>
              <button className="btn-uni" onClick={submitAccept}>Create project</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
