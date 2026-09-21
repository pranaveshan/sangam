import { formatStatus } from '../../utils/formatters';

const COLORS = {
  submitted: 'bg-slate-100 text-slate-700',
  under_review: 'bg-amber-100 text-amber-900',
  validated: 'bg-sky-100 text-sky-900',
  matched: 'bg-indigo-100 text-indigo-900',
  university_accepted: 'bg-teal-100 text-teal-900',
  team_formed: 'bg-cyan-100 text-cyan-900',
  industry_collaboration: 'bg-violet-100 text-violet-900',
  prototype: 'bg-orange-100 text-orange-900',
  testing: 'bg-fuchsia-100 text-fuchsia-900',
  pilot: 'bg-emerald-100 text-emerald-900',
  completed: 'bg-green-200 text-green-900',
  consolidated: 'bg-stone-200 text-stone-800',
  rejected: 'bg-rose-100 text-rose-900',
};

export default function StatusBadge({ status }) {
  return (
    <span className={`badge ${COLORS[status] || 'bg-slate-100 text-slate-700'}`}>
      {formatStatus(status)}
    </span>
  );
}
