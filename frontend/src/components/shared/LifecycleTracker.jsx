import { LIFECYCLE, formatStatus } from '../../utils/formatters';

export default function LifecycleTracker({ current }) {
  const idx = Math.max(0, LIFECYCLE.indexOf(current));
  return (
    <div className="w-full overflow-x-auto pb-2">
      <ol className="flex min-w-[720px] gap-1">
        {LIFECYCLE.map((stage, i) => {
          const done = i < idx;
          const active = i === idx;
          return (
            <li key={stage} className="flex-1">
              <div
                className={`h-2 rounded-full mb-2 ${
                  active ? 'bg-sangam-accent' : done ? 'bg-emerald-500' : 'bg-slate-200'
                }`}
              />
              <p
                className={`text-[10px] leading-tight ${
                  active ? 'font-bold text-sangam-accent' : done ? 'text-emerald-700' : 'text-slate-400'
                }`}
              >
                {formatStatus(stage)}
              </p>
            </li>
          );
        })}
      </ol>
    </div>
  );
}
