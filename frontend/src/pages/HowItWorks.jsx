import { useI18n } from '../context/i18n';

export default function HowItWorks() {
  const { t } = useI18n();
  const steps = t('how.steps') || [];

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-12">
      <h1 className="font-display text-4xl font-bold text-sangam-ink">{t('how.title')}</h1>
      <p className="mt-3 text-lg text-slate-600">{t('how.subtitle')}</p>

      <ol className="mt-12 space-y-6">
        {(Array.isArray(steps) ? steps : []).map((step, i) => (
          <li key={step.title} className="flex gap-5">
            <div
              className="shrink-0 w-12 h-12 rounded-xl flex items-center justify-center font-display text-xl font-bold text-white"
              style={{
                background: i % 2 === 0 ? '#0f766e' : '#123a5c',
              }}
              aria-hidden
            >
              {i + 1}
            </div>
            <div className="panel flex-1 p-5">
              <h2 className="font-display text-xl font-semibold">{step.title}</h2>
              <p className="mt-2 text-slate-600">{step.body}</p>
            </div>
          </li>
        ))}
      </ol>
    </div>
  );
}
