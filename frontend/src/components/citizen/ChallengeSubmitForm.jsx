import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { challengesAPI } from '../../utils/api';
import useStore from '../../context/store';
import AIAnalysisPanel from '../shared/AIAnalysisPanel';
import RagPanel from '../shared/RagPanel';
import DemoBadge from '../shared/DemoBadge';

const CATEGORIES = [
  'Education', 'Healthcare', 'Agriculture', 'Water', 'Environment', 'Energy',
  'Urban Development', 'Accessibility', 'Public Administration', 'Rural Livelihoods',
  'Disaster Management',
];

const FLOOD_PREFILL = {
  title: 'Flooding has damaged drinking-water infrastructure in a rural community',
  description:
    'Recent monsoon flooding has damaged drinking-water infrastructure in a rural community near Barmer. Pipelines are ruptured, storage tanks are silted, and residents report turbid water from remaining taps and handpumps. Communities need low-cost monitoring and temporary safe-water guidance while infrastructure is restored.',
  category: 'Water',
  location: 'Gram Panchayat Rohili, Barmer Rural',
  district: 'Barmer',
  state: 'Rajasthan',
  community_impact:
    'Unsafe drinking water risk for flood-affected households; women and children travel farther for tanker water.',
  people_affected: '5200',
  urgency: 'high',
  severity: 'high',
  geographic_spread: 'district',
  contact_name: 'Priya Sharma',
  contact_email: 'citizen.demo@sangam.local',
  contact_phone: '+91-90000-00001',
  video_url: '',
};

export default function ChallengeSubmitForm() {
  const navigate = useNavigate();
  const { currentUser, setLastSubmission } = useStore();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [photo, setPhoto] = useState(null);
  const [document, setDocument] = useState(null);
  const [form, setForm] = useState({ ...FLOOD_PREFILL });

  const onChange = (e) => setForm((f) => ({ ...f, [e.target.name]: e.target.value }));

  const submit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const fd = new FormData();
      Object.entries(form).forEach(([k, v]) => fd.append(k, v ?? ''));
      fd.append('people_affected', String(parseInt(form.people_affected, 10) || 0));
      if (currentUser?.id) fd.append('reporter_id', String(currentUser.id));
      if (photo) fd.append('photo', photo);
      if (document) fd.append('document', document);

      const { data } = await challengesAPI.createForm(fd);
      setResult(data);
      setLastSubmission(data);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Submission failed');
    } finally {
      setLoading(false);
    }
  };

  if (result) {
    return (
      <div className="space-y-6">
        <div className="panel p-6">
          <div className="flex flex-wrap justify-between gap-3">
            <div>
              <p className="text-xs uppercase tracking-wide text-blue-700 font-semibold">Submitted</p>
              <h2 className="font-display text-2xl font-bold mt-1">{result.challenge.title}</h2>
              <p className="text-sm text-slate-600 mt-2">
                Challenge #{result.challenge.id} · Status: {result.challenge.status}
              </p>
            </div>
            <DemoBadge label="User-generated (real functionality)" tone="green" />
          </div>
        </div>
        <AIAnalysisPanel
          analysis={result.ai_analysis}
          matches={result.university_matches}
          labels={result.data_labels}
        />
        {result.rag && <RagPanel rag={result.rag} />}
        <div className="flex flex-wrap gap-3">
          <button className="btn-primary" onClick={() => navigate(`/challenges/${result.challenge.id}`)}>
            View Challenge
          </button>
          <button className="btn-secondary" onClick={() => navigate('/dashboard')}>
            Open Workspace
          </button>
          <button className="btn-secondary" onClick={() => setResult(null)}>
            Submit Another
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="panel p-6 md:p-8">
      <div className="flex flex-wrap justify-between gap-3 mb-6">
        <div>
          <h2 className="font-display text-2xl font-bold">Report a Societal Challenge</h2>
          <p className="text-sm text-slate-600 mt-1">
            Citizen module — submission persists to the database and triggers local AI analysis.
          </p>
        </div>
        <button type="button" className="btn-secondary text-xs" onClick={() => setForm({ ...FLOOD_PREFILL })}>
          Load flood demo text
        </button>
      </div>

      {error && (
        <div className="mb-4 rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800">
          {typeof error === 'string' ? error : JSON.stringify(error)}
        </div>
      )}

      <form onSubmit={submit} className="space-y-5">
        <Field label="Challenge title *">
          <input className="input" name="title" value={form.title} onChange={onChange} required minLength={8} />
        </Field>
        <Field label="Detailed description *">
          <textarea className="input min-h-[120px]" name="description" value={form.description} onChange={onChange} required />
        </Field>
        <div className="grid md:grid-cols-2 gap-4">
          <Field label="Category *">
            <select className="input" name="category" value={form.category} onChange={onChange} required>
              {CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
          </Field>
          <Field label="Urgency *">
            <select className="input" name="urgency" value={form.urgency} onChange={onChange}>
              {['low', 'medium', 'high', 'critical'].map((u) => <option key={u} value={u}>{u}</option>)}
            </select>
          </Field>
          <Field label="Location *">
            <input className="input" name="location" value={form.location} onChange={onChange} required />
          </Field>
          <Field label="District *">
            <input className="input" name="district" value={form.district} onChange={onChange} required />
          </Field>
          <Field label="People affected *">
            <input className="input" type="number" min="0" name="people_affected" value={form.people_affected} onChange={onChange} required />
          </Field>
          <Field label="Severity">
            <select className="input" name="severity" value={form.severity} onChange={onChange}>
              {['low', 'medium', 'high', 'critical'].map((u) => <option key={u} value={u}>{u}</option>)}
            </select>
          </Field>
          <Field label="Geographic spread">
            <select className="input" name="geographic_spread" value={form.geographic_spread} onChange={onChange}>
              {['local', 'district', 'multi-district', 'state'].map((u) => <option key={u} value={u}>{u}</option>)}
            </select>
          </Field>
          <Field label="State">
            <input className="input" name="state" value={form.state} onChange={onChange} />
          </Field>
        </div>
        <Field label="Community impact *">
          <textarea className="input min-h-[80px]" name="community_impact" value={form.community_impact} onChange={onChange} required />
        </Field>
        <div className="grid md:grid-cols-3 gap-4">
          <Field label="Contact name">
            <input className="input" name="contact_name" value={form.contact_name} onChange={onChange} />
          </Field>
          <Field label="Contact email">
            <input className="input" type="email" name="contact_email" value={form.contact_email} onChange={onChange} />
          </Field>
          <Field label="Contact phone">
            <input className="input" name="contact_phone" value={form.contact_phone} onChange={onChange} />
          </Field>
        </div>
        <div className="grid md:grid-cols-3 gap-4">
          <Field label="Optional photo">
            <input type="file" accept="image/*" onChange={(e) => setPhoto(e.target.files?.[0] || null)} />
          </Field>
          <Field label="Optional document">
            <input type="file" accept=".pdf,.doc,.docx,.txt" onChange={(e) => setDocument(e.target.files?.[0] || null)} />
          </Field>
          <Field label="Optional video URL">
            <input className="input" name="video_url" value={form.video_url} onChange={onChange} placeholder="https://..." />
          </Field>
        </div>
        <button type="submit" className="btn-primary" disabled={loading}>
          {loading ? 'Analyzing & submitting…' : 'Submit Challenge'}
        </button>
      </form>
    </div>
  );
}

function Field({ label, children }) {
  return (
    <div>
      <label className="label">{label}</label>
      {children}
    </div>
  );
}
