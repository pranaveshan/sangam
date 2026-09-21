import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { projectsAPI, projectAIAPI } from '../utils/api';
import StatusBadge from '../components/shared/StatusBadge';
import DemoBadge from '../components/shared/DemoBadge';
import LifecycleTracker from '../components/shared/LifecycleTracker';
import useStore from '../context/store';
import { formatNumber } from '../utils/formatters';

export default function ProjectWorkspace() {
  const { id } = useParams();
  const { currentUser } = useStore();
  const [project, setProject] = useState(null);
  const [plan, setPlan] = useState(null);
  const [feedbackAnalysis, setFeedbackAnalysis] = useState(null);
  const [feedback, setFeedback] = useState({
    rating: 4,
    feedback: '',
    problem_improvement: '',
    deployment_confirmed: true,
  });
  const [msg, setMsg] = useState('');
  const [busy, setBusy] = useState(false);

  const load = async () => {
    const { data } = await projectsAPI.get(id);
    setProject(data);
  };

  useEffect(() => { load(); }, [id]);

  if (!project) return <p className="p-8">Loading project…</p>;

  const submitFeedback = async (e) => {
    e.preventDefault();
    await projectsAPI.addFeedback(project.id, {
      ...feedback,
      rating: Number(feedback.rating),
      user_id: currentUser?.id,
    });
    setMsg('Feedback saved (user-generated).');
    try {
      const { data } = await projectAIAPI.analyzeFeedback(project.id, {
        feedback: feedback.feedback,
        rating: Number(feedback.rating),
      });
      setFeedbackAnalysis(data);
    } catch {
      /* analysis optional */
    }
    setFeedback({ rating: 4, feedback: '', problem_improvement: '', deployment_confirmed: true });
    await load();
  };

  const toggleMilestone = async (m) => {
    await projectsAPI.updateMilestone(project.id, m.id, {
      status: m.status === 'completed' ? 'pending' : 'completed',
    });
    await load();
  };

  const suggestPlan = async () => {
    setBusy(true);
    try {
      const { data } = await projectAIAPI.plan(project.id);
      setPlan(data);
    } catch (e) {
      setMsg(e.response?.data?.detail || 'Could not generate plan suggestion.');
    } finally {
      setBusy(false);
    }
  };

  const approvePlan = async () => {
    setBusy(true);
    try {
      await projectAIAPI.approvePlan(project.id, {});
      setMsg('Official plan approved by human reviewer.');
      await load();
    } catch (e) {
      setMsg(e.response?.data?.detail || 'Approve failed.');
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-4 py-8 space-y-6">
      <Link to="/dashboard" className="text-sm text-blue-700 hover:underline">← Workspace</Link>

      <div className="panel p-6">
        <div className="flex flex-wrap justify-between gap-3">
          <div>
            <p className="text-xs uppercase tracking-wide text-teal-700 font-semibold">Project workspace</p>
            <h1 className="font-display text-3xl font-bold mt-1">{project.name}</h1>
            <p className="text-slate-600 mt-2">{project.goal}</p>
          </div>
          <div className="flex flex-col items-end gap-2">
            <StatusBadge status={project.status} />
            {project.is_demo ? <DemoBadge /> : <DemoBadge label="User project" tone="green" />}
          </div>
        </div>
        <div className="mt-4"><LifecycleTracker current={project.status} /></div>
        {project.match_explanation && (
          <p className="mt-4 text-sm rounded-lg bg-teal-50 border border-teal-200 p-3">
            <strong>Match:</strong> {project.match_explanation}
            {project.match_score != null && ` (score ${project.match_score})`}
          </p>
        )}
        {project.proposal && (
          <div className="mt-4 text-sm">
            <p className="font-semibold">Solution proposal</p>
            <p className="text-slate-700 mt-1 whitespace-pre-wrap">{project.proposal}</p>
          </div>
        )}
      </div>

      <div className="panel p-4 space-y-3">
        <div className="flex flex-wrap justify-between gap-3 items-center">
          <h3 className="font-semibold">Solution copilot</h3>
          <button type="button" className="btn-secondary text-sm" onClick={suggestPlan} disabled={busy}>
            Suggest a project plan
          </button>
        </div>
        {plan && (
          <div className="border border-amber-200 bg-amber-50 rounded-lg p-4 text-sm space-y-2">
            <DemoBadge label={plan.label || 'AI SUGGESTION'} tone="amber" />
            <p className="text-amber-900 text-xs">{plan.disclaimer}</p>
            <p className="font-semibold mt-2">Research questions</p>
            <ul className="list-disc ml-5">
              {(plan.research_questions || []).map((q) => <li key={q}>{q}</li>)}
            </ul>
            <p className="font-semibold mt-2">Milestones</p>
            <ul className="list-disc ml-5">
              {(plan.milestones || []).map((m) => (
                <li key={m.title}>{m.title} — {m.stage}</li>
              ))}
            </ul>
            <button type="button" className="btn-primary mt-3" onClick={approvePlan} disabled={busy}>
              Approve as official plan
            </button>
          </div>
        )}
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        <div className="panel p-4">
          <h3 className="font-semibold mb-2">Team: {project.team_name || 'Not formed'}</h3>
          <ul className="text-sm space-y-1">
            {(project.team_members || []).map((m, i) => (
              <li key={i}>{m.name} — {m.role}</li>
            ))}
          </ul>
          <h4 className="font-semibold mt-4 mb-2 text-sm">Faculty mentors</h4>
          <ul className="text-sm space-y-1">
            {(project.faculty_mentors || []).map((m, i) => (
              <li key={i}>{m.name} — {m.department || m.expertise}</li>
            ))}
          </ul>
        </div>
        <div className="panel p-4">
          <h3 className="font-semibold mb-2">Industry collaboration</h3>
          {(project.collaborations || []).length === 0 && (
            <p className="text-sm text-slate-500">No collaborations yet.</p>
          )}
          {(project.collaborations || []).map((c) => (
            <div key={c.id} className="border rounded-lg p-3 mb-2 text-sm">
              <p className="font-medium">{c.partner_name} · {c.support_type}</p>
              <p className="text-slate-600">{c.details}</p>
              <p className="text-amber-800 text-xs mt-1">{c.financial_note}</p>
            </div>
          ))}
          <div className="mt-3 text-sm grid grid-cols-2 gap-2">
            <div className="bg-slate-50 rounded-lg p-2">People impacted: <strong>{formatNumber(project.people_impacted)}</strong></div>
            <div className="bg-slate-50 rounded-lg p-2">Communities: <strong>{project.communities_reached}</strong></div>
          </div>
          {project.pilot_location && (
            <p className="text-sm mt-3"><strong>Pilot:</strong> {project.pilot_location}</p>
          )}
        </div>
      </div>

      <div className="panel p-4">
        <h3 className="font-semibold mb-3">Milestones</h3>
        <ul className="space-y-2">
          {(project.milestones || []).map((m) => (
            <li key={m.id} className="flex justify-between items-center border rounded-lg px-3 py-2 text-sm">
              <span>{m.order_index}. {m.title}</span>
              <button type="button" className="btn-secondary text-xs py-1" onClick={() => toggleMilestone(m)}>
                {m.status}
              </button>
            </li>
          ))}
        </ul>
      </div>

      <div id="feedback" className="panel p-4">
        <h3 className="font-semibold mb-2">Community feedback</h3>
        <p className="text-sm text-slate-600 mb-3">
          Average rating: {project.average_rating ?? '—'} · {(project.feedback || []).length} responses
        </p>
        <div className="space-y-2 mb-4">
          {(project.feedback || []).map((f) => (
            <div key={f.id} className="border rounded-lg p-3 text-sm">
              <div className="flex justify-between">
                <span className="font-medium">Rating {f.rating}/5</span>
                {f.is_demo ? <DemoBadge /> : <DemoBadge label="User feedback" tone="green" />}
              </div>
              <p className="mt-1">{f.feedback}</p>
              {f.problem_improvement && (
                <p className="text-slate-600 mt-1">Improvement: {f.problem_improvement}</p>
              )}
              {f.deployment_confirmed && (
                <p className="text-emerald-700 text-xs mt-1">Deployment confirmed</p>
              )}
            </div>
          ))}
        </div>
        {feedbackAnalysis && (
          <div className="mb-4 border border-slate-200 rounded-lg p-3 text-sm bg-slate-50">
            <p className="font-semibold">Feedback themes (analysis)</p>
            <p className="text-xs text-slate-500 mt-1">{feedbackAnalysis.disclaimer}</p>
            <ul className="list-disc ml-5 mt-2">
              {(feedbackAnalysis.themes || []).map((theme) => <li key={theme}>{theme}</li>)}
            </ul>
            {(feedbackAnalysis.suggested_improvements || []).length > 0 && (
              <>
                <p className="font-semibold mt-2">Suggested improvements</p>
                <ul className="list-disc ml-5">
                  {feedbackAnalysis.suggested_improvements.map((item) => <li key={item}>{item}</li>)}
                </ul>
              </>
            )}
          </div>
        )}
        <form onSubmit={submitFeedback} className="space-y-3 border-t pt-4">
          <h4 className="font-medium text-sm">Submit feedback (after pilot)</h4>
          {msg && <p className="text-emerald-700 text-sm">{msg}</p>}
          <select className="input" value={feedback.rating}
            onChange={(e) => setFeedback({ ...feedback, rating: e.target.value })}>
            {[1, 2, 3, 4, 5].map((n) => <option key={n} value={n}>{n} stars</option>)}
          </select>
          <textarea className="input min-h-[70px]" required placeholder="Feedback (type or paste voice transcript)"
            value={feedback.feedback} onChange={(e) => setFeedback({ ...feedback, feedback: e.target.value })} />
          <textarea className="input min-h-[60px]" placeholder="Problem improvement observed"
            value={feedback.problem_improvement}
            onChange={(e) => setFeedback({ ...feedback, problem_improvement: e.target.value })} />
          <label className="flex items-center gap-2 text-sm">
            <input type="checkbox" checked={feedback.deployment_confirmed}
              onChange={(e) => setFeedback({ ...feedback, deployment_confirmed: e.target.checked })} />
            Confirm deployment / solution observed on ground
          </label>
          <button className="btn-primary" type="submit">Submit community feedback</button>
        </form>
      </div>
    </div>
  );
}
