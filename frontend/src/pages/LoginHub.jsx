import { Link } from 'react-router-dom';
import DemoBadge from '../components/shared/DemoBadge';

const PORTALS = [
  {
    slug: 'citizen',
    title: 'Citizen Portal',
    desc: 'Report challenges and share community feedback after pilots.',
    color: '#1d4ed8',
    creds: 'citizen.demo@sangam.local / citizen123',
  },
  {
    slug: 'admin',
    title: 'Admin / Government',
    desc: 'Validate reports, consolidate duplicates, track district impact.',
    color: '#a16207',
    creds: 'gov.demo@sangam.local / admin123',
  },
  {
    slug: 'university',
    title: 'University Portal',
    desc: 'Review AI matches, accept challenges, assign mentors.',
    color: '#0f766e',
    creds: 'uni.demo@sangam.local / uni123',
  },
  {
    slug: 'ssc',
    title: 'Student / SSC Portal',
    desc: 'Student & Scholar Cell — form AquaGuard teams, update milestones.',
    color: '#047857',
    creds: 'student.demo@sangam.local / student123',
  },
  {
    slug: 'csr',
    title: 'Industry / CSR Portal',
    desc: 'Offer mentorship and technology support (no real payments).',
    color: '#334155',
    creds: 'industry.demo@sangam.local / csr123',
  },
];

export default function LoginHub() {
  return (
    <div className="max-w-6xl mx-auto px-4 py-10">
      <div className="text-center mb-10">
        <h1 className="font-display text-4xl font-bold">Choose your SANGAM portal</h1>
        <p className="text-slate-600 mt-3 max-w-2xl mx-auto">
          Each stakeholder has a separate login and workspace. Demo credentials are shown on each portal card.
        </p>
        <div className="mt-3 flex justify-center"><DemoBadge label="Demo Auth — not production security" /></div>
      </div>

      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {PORTALS.map((p) => (
          <Link
            key={p.slug}
            to={`/login/${p.slug}`}
            className="panel p-5 hover:shadow-md transition border-t-4 block"
            style={{ borderTopColor: p.color }}
          >
            <h2 className="font-display text-xl font-bold" style={{ color: p.color }}>{p.title}</h2>
            <p className="text-sm text-slate-600 mt-2">{p.desc}</p>
            <p className="text-xs text-slate-500 mt-4 font-mono bg-slate-50 border rounded-lg p-2">
              {p.creds}
            </p>
            <span className="inline-block mt-4 text-sm font-semibold" style={{ color: p.color }}>
              Sign in →
            </span>
          </Link>
        ))}
      </div>
    </div>
  );
}
