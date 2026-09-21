import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell,
  CartesianGrid,
} from 'recharts';
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { adminAPI, challengesAPI, demoAPI, projectsAPI, dashboardAIAPI } from '../../utils/api';
import StatusBadge from '../shared/StatusBadge';
import DemoBadge from '../shared/DemoBadge';
import { formatNumber } from '../../utils/formatters';

const PIE_COLORS = ['#1d4ed8', '#0f766e', '#a16207', '#c2410c', '#334155', '#047857', '#0e7490'];

export default function GovernmentDashboard() {
  const [stats, setStats] = useState(null);
  const [pending, setPending] = useState([]);
  const [aiSummary, setAiSummary] = useState(null);
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(null);

  const load = async () => {
    try {
      const [s, c, ai] = await Promise.all([
        adminAPI.stats(),
        challengesAPI.list(),
        dashboardAIAPI.summary().catch(() => ({ data: null })),
      ]);
      setStats(s.data);
      setAiSummary(ai.data);
      setPending(
        c.data.filter((x) => ['submitted', 'under_review'].includes(x.status))
      );
      setError(null);
    } catch (e) {
      setError(e.message);
    }
  };

  useEffect(() => { load(); }, []);

  const act = async (id, action, consolidate_into_id) => {
    setBusy(id);
    try {
      await challengesAPI.validate(id, { action, consolidate_into_id });
      await load();
    } catch (e) {
      alert(e.response?.data?.detail || e.message);
    } finally {
      setBusy(null);
    }
  };

  const resetDemo = async () => {
    if (!confirm('Reset database and restore AquaGuard demo journey?')) return;
    await demoAPI.reset();
    await load();
  };

  if (error) {
    return <p className="text-rose-700">Failed to load admin stats: {error}</p>;
  }
  if (!stats) return <p className="text-slate-600">Loading government dashboard…</p>;

  const domainData = Object.entries(stats.domain_distribution || {}).map(([name, value]) => ({ name, value }));
  const statusData = Object.entries(stats.status_distribution || {}).map(([name, value]) => ({ name, value }));
  const lifecycleData = Object.entries(stats.lifecycle_counts || {}).map(([name, value]) => ({ name, value }));
  const districtData = Object.entries(stats.district_distribution || {}).map(([name, value]) => ({ name, value }));

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap justify-between gap-3">
        <div>
          <h2 className="font-display text-2xl font-bold">Government / Admin Dashboard</h2>
          <p className="text-sm text-slate-600 mt-1">{stats.data_label}</p>
        </div>
        <div className="flex gap-2">
          <DemoBadge />
          <button className="btn-secondary text-xs" onClick={resetDemo}>Reset Demo Data</button>
        </div>
      </div>

      {aiSummary && (
        <div className="panel p-4 text-sm">
          <p className="font-semibold">Insights from live data</p>
          <p className="mt-2 text-slate-700">{aiSummary.summary}</p>
          <ul className="list-disc ml-5 mt-2 text-slate-600">
            {(aiSummary.highlights || []).map((h) => <li key={h}>{h}</li>)}
          </ul>
          <p className="text-xs text-slate-500 mt-2">{aiSummary.disclaimer}</p>
        </div>
      )}

      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-3">
        <Stat label="Total challenges" value={stats.total_challenges} />
        <Stat label="Pending validation" value={stats.pending_validation} />
        <Stat label="Validated" value={stats.validated_challenges} />
        <Stat label="Active projects" value={stats.active_projects} />
        <Stat label="Completed pilots" value={stats.completed_pilots} />
        <Stat label="University participation" value={stats.university_participation} />
        <Stat label="Industry participation" value={stats.industry_participation} />
        <Stat label="People affected" value={formatNumber(stats.people_affected_total)} />
        <Stat label="Communities reached" value={stats.communities_reached} />
        <Stat label="Avg community rating" value={stats.average_community_rating ?? '—'} />
      </div>

      <div className="grid lg:grid-cols-2 gap-4">
        <ChartPanel title="Projects by domain / domain distribution">
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={domainData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="name" tick={{ fontSize: 10 }} interval={0} angle={-25} textAnchor="end" height={70} />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="value" fill="#1d4ed8" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartPanel>
        <ChartPanel title="Challenge status distribution">
          <ResponsiveContainer width="100%" height={240}>
            <PieChart>
              <Pie data={statusData} dataKey="value" nameKey="name" outerRadius={90} label={({ name }) => name}>
                {statusData.map((_, i) => <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />)}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </ChartPanel>
        <ChartPanel title="Project lifecycle">
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={lifecycleData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="name" tick={{ fontSize: 10 }} />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="value" fill="#0f766e" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartPanel>
        <ChartPanel title="District distribution">
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={districtData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="name" tick={{ fontSize: 11 }} />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="value" fill="#a16207" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartPanel>
      </div>

      <div className="panel p-4">
        <div className="flex justify-between mb-3">
          <h3 className="font-semibold">District map visualization</h3>
          <DemoBadge label="Demo geo points" />
        </div>
        <div className="h-72 rounded-xl overflow-hidden border border-slate-200">
          <MapContainer center={[26.2, 73.0]} zoom={6} scrollWheelZoom={false} style={{ height: '100%', width: '100%' }}>
            <TileLayer
              attribution='&copy; OpenStreetMap'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            {(stats.geo_points || []).map((p) => (
              <CircleMarker
                key={p.id}
                center={[p.lat, p.lng]}
                radius={8}
                pathOptions={{ color: p.is_demo ? '#a16207' : '#1d4ed8', fillOpacity: 0.7 }}
              >
                <Popup>
                  <strong>{p.title}</strong><br />
                  {p.district} · {p.status}<br />
                  {p.is_demo ? 'Demo Data' : 'User data'}
                </Popup>
              </CircleMarker>
            ))}
          </MapContainer>
        </div>
      </div>

      <div className="panel p-4">
        <h3 className="font-semibold mb-3">Pending validation queue</h3>
        <div className="space-y-3">
          {pending.map((c) => (
            <div key={c.id} className="border border-slate-200 rounded-lg p-3 flex flex-wrap justify-between gap-3">
              <div>
                <Link to={`/challenges/${c.id}`} className="font-medium hover:underline">{c.title}</Link>
                <p className="text-sm text-slate-600">{c.district} · {c.domain || c.category}</p>
                <div className="mt-1 flex gap-2 items-center">
                  <StatusBadge status={c.status} />
                  {c.is_demo && <DemoBadge />}
                </div>
              </div>
              <div className="flex flex-wrap gap-2">
                <button className="btn-gov text-xs" disabled={busy === c.id} onClick={() => act(c.id, 'validate')}>
                  Validate
                </button>
                <button className="btn-secondary text-xs" disabled={busy === c.id} onClick={() => act(c.id, 'reject')}>
                  Reject
                </button>
              </div>
            </div>
          ))}
          {!pending.length && <p className="text-sm text-slate-500">No pending challenges.</p>}
        </div>
      </div>

      <ActiveProjects />
    </div>
  );
}

function ActiveProjects() {
  const [projects, setProjects] = useState([]);
  useEffect(() => {
    projectsAPI.list().then((r) => setProjects(r.data)).catch(() => {});
  }, []);
  return (
    <div className="panel p-4">
      <h3 className="font-semibold mb-3">Project progress</h3>
      <div className="space-y-2">
        {projects.map((p) => (
          <Link key={p.id} to={`/projects/${p.id}`} className="block border rounded-lg p-3 hover:bg-slate-50">
            <div className="flex justify-between gap-2">
              <span className="font-medium">{p.name}</span>
              <StatusBadge status={p.status} />
            </div>
            <p className="text-sm text-slate-600">{p.challenge_title}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}

function Stat({ label, value }) {
  return (
    <div className="panel p-3">
      <p className="text-[11px] uppercase tracking-wide text-slate-500">{label}</p>
      <p className="text-xl font-bold mt-1">{value}</p>
    </div>
  );
}

function ChartPanel({ title, children }) {
  return (
    <div className="panel p-4">
      <div className="flex justify-between mb-2">
        <h3 className="font-semibold text-sm">{title}</h3>
        <DemoBadge label="Live DB stats" tone="slate" />
      </div>
      {children}
    </div>
  );
}
