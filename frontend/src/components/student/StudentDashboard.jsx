import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { projectsAPI } from '../../utils/api';
import StatusBadge from '../shared/StatusBadge';
import DemoBadge from '../shared/DemoBadge';
import LifecycleTracker from '../shared/LifecycleTracker';

export default function StudentDashboard() {
  const [projects, setProjects] = useState([]);
  const [selected, setSelected] = useState(null);
  const [teamForm, setTeamForm] = useState({
    team_name: 'AquaGuard',
    members: 'Arjun Mehta|Team Lead\nSana Qureshi|Environmental Eng.\nVikram Singh|Civil / Field Ops\nMeera Iyer|Data & Dashboard',
    mentors: 'Dr. Ananya Rao|Environmental Engineering\nProf. Kabir Desai|Electronics & IoT',
  });

  const load = async () => {
    const { data } = await projectsAPI.list();
    setProjects(data);
    if (!selected && data.length) setSelected(data[0]);
    else if (selected) {
      const fresh = data.find((p) => p.id === selected.id);
      if (fresh) setSelected(fresh);
    }
  };

  useEffect(() => { load(); }, []);

  const saveTeam = async () => {
    if (!selected) return;
    const team_members = teamForm.members
      .split('\n')
      .filter(Boolean)
      .map((line) => {
        const [name, role] = line.split('|');
        return { name: name?.trim(), role: role?.trim() || 'Member' };
      });
    const faculty_mentors = teamForm.mentors
      .split('\n')
      .filter(Boolean)
      .map((line) => {
        const [name, department] = line.split('|');
        return { name: name?.trim(), department: department?.trim() || 'Faculty' };
      });
    const { data } = await projectsAPI.updateTeam(selected.id, {
      team_name: teamForm.team_name,
      team_members,
      faculty_mentors,
    });
    setSelected(data);
    await load();
  };

  const toggleMilestone = async (m) => {
    const next = m.status === 'completed' ? 'pending' : 'completed';
    const { data } = await projectsAPI.updateMilestone(selected.id, m.id, { status: next });
    setSelected(data);
    await load();
  };

  const advance = async (status) => {
    const { data } = await projectsAPI.updateStatus(selected.id, { status });
    setSelected(data);
    await load();
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="font-display text-2xl font-bold text-sangam-student">Student / Research Team</h2>
        <p className="text-sm text-slate-600 mt-1">Form teams, assign mentors, update milestones and prototype status.</p>
      </div>

      <div className="grid lg:grid-cols-3 gap-4">
        <div className="panel p-4 lg:col-span-1">
          <h3 className="font-semibold mb-3">Projects</h3>
          <div className="space-y-2">
            {projects.map((p) => (
              <button
                key={p.id}
                type="button"
                onClick={() => setSelected(p)}
                className={`w-full text-left border rounded-lg p-3 ${selected?.id === p.id ? 'border-emerald-500 bg-emerald-50' : ''}`}
              >
                <div className="font-medium">{p.name}</div>
                <StatusBadge status={p.status} />
                {p.is_demo && <span className="ml-2"><DemoBadge /></span>}
              </button>
            ))}
          </div>
        </div>

        {selected && (
          <div className="panel p-4 lg:col-span-2 space-y-4">
            <div className="flex flex-wrap justify-between gap-2">
              <div>
                <h3 className="font-display text-xl font-bold">{selected.name}</h3>
                <p className="text-sm text-slate-600">{selected.goal}</p>
              </div>
              <Link to={`/projects/${selected.id}`} className="btn-secondary text-xs">Full workspace</Link>
            </div>
            <LifecycleTracker current={selected.status} />

            <div>
              <h4 className="font-semibold text-sm mb-2">Team formation</h4>
              <input className="input mb-2" value={teamForm.team_name}
                onChange={(e) => setTeamForm({ ...teamForm, team_name: e.target.value })} placeholder="Team name" />
              <label className="label">Members (Name|Role per line)</label>
              <textarea className="input min-h-[90px] mb-2" value={teamForm.members}
                onChange={(e) => setTeamForm({ ...teamForm, members: e.target.value })} />
              <label className="label">Faculty mentors (Name|Dept per line)</label>
              <textarea className="input min-h-[70px] mb-2" value={teamForm.mentors}
                onChange={(e) => setTeamForm({ ...teamForm, mentors: e.target.value })} />
              <button className="btn-primary" onClick={saveTeam}>Save team & mentors</button>
            </div>

            <div>
              <h4 className="font-semibold text-sm mb-2">Milestones</h4>
              <ul className="space-y-2">
                {(selected.milestones || []).map((m) => (
                  <li key={m.id} className="flex items-center justify-between border rounded-lg px-3 py-2 text-sm">
                    <span>{m.order_index}. {m.title}</span>
                    <button
                      type="button"
                      className={`badge border ${m.status === 'completed' ? 'bg-emerald-100 border-emerald-300' : 'bg-slate-50 border-slate-200'}`}
                      onClick={() => toggleMilestone(m)}
                    >
                      {m.status}
                    </button>
                  </li>
                ))}
              </ul>
            </div>

            <div className="flex flex-wrap gap-2">
              {['prototype', 'testing', 'pilot', 'completed'].map((s) => (
                <button key={s} type="button" className="btn-secondary text-xs" onClick={() => advance(s)}>
                  Set {s}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
