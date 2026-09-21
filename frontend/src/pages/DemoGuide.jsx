import { Link } from 'react-router-dom';
import DemoBadge from '../components/shared/DemoBadge';

const STEPS = [
  { title: 'Open SANGAM homepage', action: 'Citizen-first hero: Speak / Show / Explore', path: '/' },
  { title: 'Switch language (e.g. Telugu)', action: 'Use the language selector in the header', path: '/' },
  { title: 'Tell us what happened', action: 'Tap Speak — use mic or type a community problem', path: '/report?mode=speak' },
  { title: 'Confirm understanding', action: 'Review “Here’s what we understood” → Listen / Correct / Confirm', path: '/report' },
  { title: 'Related reports + collaborators', action: 'After submit, see related reports and DEMO DATA matches', path: '/explore' },
  { title: 'University accepts', action: 'Login University → accept matched challenge', path: '/login/university' },
  { title: 'AI project plan suggestion', action: 'Open project → Suggest plan → Approve as official', path: '/login/ssc' },
  { title: 'Lifecycle + community feedback', action: 'Update milestones → submit feedback → see theme analysis', path: '/login/citizen' },
  { title: 'Admin impact', action: 'Admin dashboard insights from live DB aggregates', path: '/login/admin' },
];

export default function DemoGuide() {
  return (
    <div className="max-w-4xl mx-auto px-4 py-10 space-y-6">
      <div>
        <h1 className="font-display text-3xl font-bold">Judge Demo Guide (~3 minutes)</h1>
        <p className="text-slate-600 mt-2">
          Voice-first citizen report → confirm understanding → related problems → expertise match →
          project plan → feedback → impact. Demo organizations are always labeled.
        </p>
        <div className="mt-3"><DemoBadge label="Demo Auth · DEMO DATA labeled" /></div>
      </div>

      <div className="panel p-4 text-sm overflow-x-auto">
        <p className="font-semibold mb-2">Demo credentials (portal logins)</p>
        <table className="w-full text-left">
          <thead>
            <tr className="text-slate-500 border-b">
              <th className="py-1 pr-3">Portal</th>
              <th className="py-1 pr-3">Email</th>
              <th className="py-1">Password</th>
            </tr>
          </thead>
          <tbody className="font-mono text-xs">
            <tr className="border-b"><td className="py-1">Citizen</td><td>citizen.demo@sangam.local</td><td>citizen123</td></tr>
            <tr className="border-b"><td className="py-1">Admin</td><td>gov.demo@sangam.local</td><td>admin123</td></tr>
            <tr className="border-b"><td className="py-1">University</td><td>uni.demo@sangam.local</td><td>uni123</td></tr>
            <tr className="border-b"><td className="py-1">Student/SSC</td><td>student.demo@sangam.local</td><td>student123</td></tr>
            <tr><td className="py-1">Industry/CSR</td><td>industry.demo@sangam.local</td><td>csr123</td></tr>
          </tbody>
        </table>
      </div>

      <ol className="space-y-3">
        {STEPS.map((s, i) => (
          <li key={i} className="panel p-4 flex flex-wrap justify-between gap-3">
            <div>
              <p className="text-xs uppercase tracking-wide text-slate-500">Step {i + 1}</p>
              <p className="font-semibold mt-1">{s.title}</p>
              <p className="text-sm text-slate-600 mt-1">{s.action}</p>
            </div>
            <Link to={s.path} className="btn-primary text-xs h-fit">
              Open
            </Link>
          </li>
        ))}
      </ol>

      <div className="panel p-4 text-sm space-y-2">
        <p><strong>Telugu sample (type if mic unavailable):</strong></p>
        <p className="font-mono text-xs bg-slate-50 p-3 rounded-lg">
          వర్షం పడిన తర్వాత మా పొలంలో నీళ్లు నిలిచిపోతున్నాయి. పంట పాడవుతోంది.
        </p>
        <p className="text-slate-600">Or English: “After heavy rain, water stays in our farmland and the crop is getting damaged.”</p>
        <Link to="/login" className="text-blue-700 underline">All portals</Link>
      </div>
    </div>
  );
}
