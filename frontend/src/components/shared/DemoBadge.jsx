export default function DemoBadge({ label = 'Demo Data', tone = 'amber' }) {
  const tones = {
    amber: 'bg-amber-100 text-amber-900 border-amber-300',
    blue: 'bg-blue-100 text-blue-900 border-blue-300',
    slate: 'bg-slate-100 text-slate-800 border-slate-300',
    green: 'bg-emerald-100 text-emerald-900 border-emerald-300',
  };
  return (
    <span className={`badge border ${tones[tone] || tones.amber}`}>{label}</span>
  );
}
