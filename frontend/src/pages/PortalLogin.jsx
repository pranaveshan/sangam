import { useEffect, useMemo, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { authAPI } from '../utils/api';
import useStore from '../context/store';
import DemoBadge from '../components/shared/DemoBadge';

const PORTAL_MAP = {
  citizen: {
    role: 'citizen',
    title: 'Citizen Portal',
    blurb: 'Report societal challenges from your community and follow pilots.',
    color: '#1d4ed8',
    email: 'citizen.demo@sangam.local',
    password: 'citizen123',
  },
  admin: {
    role: 'government',
    title: 'Admin / Government Portal',
    blurb: 'District innovation officers validate challenges and track impact.',
    color: '#a16207',
    email: 'gov.demo@sangam.local',
    password: 'admin123',
  },
  government: {
    role: 'government',
    title: 'Admin / Government Portal',
    blurb: 'District innovation officers validate challenges and track impact.',
    color: '#a16207',
    email: 'gov.demo@sangam.local',
    password: 'admin123',
  },
  university: {
    role: 'university',
    title: 'University Portal',
    blurb: 'Faculty coordinators accept AI-matched challenges and guide teams.',
    color: '#0f766e',
    email: 'uni.demo@sangam.local',
    password: 'uni123',
  },
  ssc: {
    role: 'student',
    title: 'Student / SSC Portal',
    blurb: 'Student & Scholar Cell — build prototypes, update milestones, ship pilots.',
    color: '#047857',
    email: 'student.demo@sangam.local',
    password: 'student123',
  },
  student: {
    role: 'student',
    title: 'Student / SSC Portal',
    blurb: 'Student & Scholar Cell — build prototypes, update milestones, ship pilots.',
    color: '#047857',
    email: 'student.demo@sangam.local',
    password: 'student123',
  },
  csr: {
    role: 'industry',
    title: 'Industry / CSR Portal',
    blurb: 'Partners offer mentorship and resources. No real financial transactions.',
    color: '#334155',
    email: 'industry.demo@sangam.local',
    password: 'csr123',
  },
  industry: {
    role: 'industry',
    title: 'Industry / CSR Portal',
    blurb: 'Partners offer mentorship and resources. No real financial transactions.',
    color: '#334155',
    email: 'industry.demo@sangam.local',
    password: 'csr123',
  },
};

export default function PortalLogin() {
  const { portalSlug } = useParams();
  const navigate = useNavigate();
  const { loginSuccess, isAuthenticated, currentRole, logout } = useStore();
  const portal = useMemo(() => PORTAL_MAP[portalSlug], [portalSlug]);

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (portal) {
      setEmail(portal.email);
      setPassword(portal.password);
    }
  }, [portal]);

  useEffect(() => {
    if (isAuthenticated && currentRole === portal?.role) {
      navigate('/dashboard', { replace: true });
    }
  }, [isAuthenticated, currentRole, portal, navigate]);

  if (!portal) {
    return (
      <div className="max-w-md mx-auto px-4 py-16 text-center">
        <h1 className="font-display text-2xl font-bold">Unknown portal</h1>
        <Link to="/login" className="btn-primary mt-6 inline-flex">All portals</Link>
      </div>
    );
  }

  const submit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      if (isAuthenticated && currentRole !== portal.role) {
        logout();
      }
      const { data } = await authAPI.login({
        email,
        password,
        portal: portalSlug,
      });
      loginSuccess({
        token: data.token,
        user: data.user,
        portal: data.portal,
      });
      navigate('/dashboard', { replace: true });
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[70vh] flex items-center justify-center px-4 py-10">
      <div className="w-full max-w-md">
        <div
          className="rounded-t-xl px-6 py-5 text-white"
          style={{ background: `linear-gradient(135deg, ${portal.color}, #0f172a)` }}
        >
          <p className="text-xs uppercase tracking-[0.18em] text-white/70">SANGAM sign-in</p>
          <h1 className="font-display text-2xl font-bold mt-1">{portal.title}</h1>
          <p className="text-sm text-white/85 mt-2">{portal.blurb}</p>
        </div>

        <form onSubmit={submit} className="panel rounded-t-none p-6 space-y-4 border-t-0">
          <div className="flex justify-between items-center">
            <DemoBadge label="Demo credentials prefilled" />
            <Link to="/login" className="text-xs text-slate-500 hover:underline">Other portals</Link>
          </div>

          {error && (
            <div className="rounded-lg border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-800">
              {String(error)}
            </div>
          )}

          <div>
            <label className="label">Email</label>
            <input className="input" type="email" required value={email} onChange={(e) => setEmail(e.target.value)} />
          </div>
          <div>
            <label className="label">Password</label>
            <input className="input" type="password" required value={password} onChange={(e) => setPassword(e.target.value)} />
          </div>

          <button
            type="submit"
            className="btn w-full text-white"
            style={{ background: portal.color }}
            disabled={loading}
          >
            {loading ? 'Signing in…' : `Enter ${portal.title}`}
          </button>

          <p className="text-[11px] text-slate-500 leading-relaxed">
            Prototype authentication for SIH26043. Not production SSO. Each portal only accepts its own role account.
          </p>
        </form>
      </div>
    </div>
  );
}
