import { Link } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { useI18n } from '../context/i18n';
import { challengesAPI } from '../utils/api';
import DemoBadge from '../components/shared/DemoBadge';

const JOURNEY = [
  'A person',
  'Has a problem',
  'Tells SANGAM',
  'SANGAM understands',
  'Right people discover it',
  'They collaborate',
  'A solution is built',
  'Community tests it',
  'Solution improves',
];

const STATUS_LABEL = {
  submitted: 'Reported',
  under_review: 'Understanding',
  validated: 'Validated',
  matched: 'Matched',
  university_accepted: 'Team forming',
  team_formed: 'Research',
  industry_collaboration: 'Research',
  prototype: 'Prototype',
  testing: 'Testing',
  pilot: 'Pilot',
  completed: 'Impact',
};

export default function Home() {
  const { t } = useI18n();
  const [problems, setProblems] = useState([]);

  useEffect(() => {
    challengesAPI.list()
      .then((r) => setProblems((r.data || []).slice(0, 6)))
      .catch(() => setProblems([]));
  }, []);

  return (
    <div>
      <section className="relative overflow-hidden min-h-[88vh] flex items-end md:items-center">
        <div
          className="absolute inset-0"
          style={{
            background:
              'linear-gradient(145deg, #0a1628 0%, #123a5c 48%, #0d5c56 100%)',
          }}
        />
        <div
          className="absolute inset-0 opacity-40"
          style={{
            backgroundImage:
              'radial-gradient(ellipse at 15% 20%, rgba(255,255,255,0.18), transparent 42%), radial-gradient(ellipse at 85% 70%, rgba(194,65,12,0.28), transparent 45%)',
          }}
        />
        <div
          className="absolute inset-0 opacity-[0.12]"
          style={{
            backgroundImage:
              'url("data:image/svg+xml,%3Csvg width=\'60\' height=\'60\' viewBox=\'0 0 60 60\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cg fill=\'none\' fill-rule=\'evenodd\'%3E%3Cg fill=\'%23ffffff\' fill-opacity=\'1\'%3E%3Cpath d=\'M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z\'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")',
          }}
        />

        <div className="relative w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 md:py-24 text-white">
          <p className="font-display text-5xl sm:text-6xl md:text-7xl font-bold tracking-tight">
            {t('brand')}
          </p>
          <h1 className="mt-5 max-w-2xl font-display text-2xl sm:text-3xl md:text-4xl font-semibold leading-snug text-white/95">
            {t('tagline')}
          </h1>
          <p className="mt-4 max-w-xl text-base sm:text-lg text-white/80 leading-relaxed">
            {t('heroSupport')}
          </p>

          <div className="mt-10 flex flex-col sm:flex-row flex-wrap gap-3">
            <Link
              to="/report?mode=speak"
              className="inline-flex items-center justify-center gap-3 min-h-[56px] px-6 rounded-xl bg-white text-sangam-ink font-semibold text-base hover:bg-sangam-sand transition focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white"
            >
              <span className="text-xl" aria-hidden>🎙️</span>
              {t('cta.speak')}
            </Link>
            <Link
              to="/report?mode=show"
              className="inline-flex items-center justify-center gap-3 min-h-[56px] px-6 rounded-xl border-2 border-white/50 text-white font-semibold text-base hover:bg-white/10 transition focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white"
            >
              <span className="text-xl" aria-hidden>📸</span>
              {t('cta.show')}
            </Link>
            <Link
              to="/explore"
              className="inline-flex items-center justify-center gap-3 min-h-[56px] px-6 rounded-xl border border-white/30 text-white/95 font-semibold text-base hover:bg-white/10 transition"
            >
              <span className="text-xl" aria-hidden>🔎</span>
              {t('cta.explore')}
            </Link>
          </div>
        </div>
      </section>

      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-14">
        <div className="flex flex-wrap items-end justify-between gap-4 mb-8">
          <div>
            <h2 className="font-display text-3xl font-bold text-sangam-ink">
              {t('home.problemsAroundUs')}
            </h2>
            <p className="text-slate-600 mt-2 max-w-2xl">{t('home.problemsAroundUsHint')}</p>
          </div>
          <Link to="/explore" className="btn-secondary">{t('cta.explore')}</Link>
        </div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {problems.map((p) => (
            <article key={p.id} className="panel p-5 flex flex-col gap-3">
              <div className="flex items-start justify-between gap-2">
                <h3 className="font-display text-lg font-semibold leading-snug">{p.title}</h3>
                {p.is_demo && <DemoBadge label={t('home.demoData')} tone="amber" />}
              </div>
              <p className="text-sm text-slate-600 line-clamp-3">{p.description}</p>
              <p className="text-xs text-slate-500">
                {t('home.status')}:{' '}
                <span className="font-semibold text-slate-800">
                  {STATUS_LABEL[p.status] || p.status}
                </span>
              </p>
              {p.required_expertise?.length > 0 && (
                <div>
                  <p className="text-xs font-semibold text-slate-500 mb-1.5">{t('home.lookingFor')}</p>
                  <div className="flex flex-wrap gap-1.5">
                    {p.required_expertise.slice(0, 4).map((e) => (
                      <span key={e} className="badge bg-teal-50 text-teal-900 border border-teal-100">
                        {e}
                      </span>
                    ))}
                  </div>
                </div>
              )}
              <Link to={`/explore/${p.id}`} className="text-sm font-semibold text-sangam-uni mt-auto">
                {t('explore.viewDetails')} →
              </Link>
            </article>
          ))}
          {problems.length === 0 && (
            <p className="text-slate-500 col-span-full">{t('explore.empty')}</p>
          )}
        </div>
      </section>

      <section className="border-y border-slate-200/80 bg-white/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-14">
          <h2 className="font-display text-3xl font-bold mb-2">{t('home.journeyTitle')}</h2>
          <p className="text-slate-600 mb-8">{t('home.journeyHint')}</p>
          <ol className="flex flex-wrap gap-2 md:gap-0 md:flex-nowrap items-stretch">
            {JOURNEY.map((step, i) => (
              <li key={step} className="flex items-center gap-2 flex-1 min-w-[140px]">
                <div className="panel px-3 py-3 text-center w-full">
                  <span className="text-[10px] font-bold text-slate-400 tracking-wider">{i + 1}</span>
                  <p className="text-sm font-semibold text-sangam-ink mt-1 leading-snug">{step}</p>
                </div>
                {i < JOURNEY.length - 1 && (
                  <span className="hidden md:inline text-slate-300 text-lg px-1" aria-hidden>→</span>
                )}
              </li>
            ))}
          </ol>
          <div className="mt-8">
            <Link to="/how-it-works" className="btn-primary">{t('nav.howItWorks')}</Link>
          </div>
        </div>
      </section>

      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-14">
        <h2 className="font-display text-2xl font-bold mb-4">{t('home.joinTitle')}</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {[
            { key: 'student', to: '/login/ssc' },
            { key: 'researcher', to: '/login/university' },
            { key: 'industry', to: '/login/csr' },
            { key: 'volunteer', to: '/login/citizen' },
          ].map((r) => (
            <Link
              key={r.key}
              to={r.to}
              className="panel p-5 text-center hover:shadow-md transition min-h-[88px] flex items-center justify-center font-semibold text-sangam-ink"
            >
              {t(`home.roles.${r.key}`)}
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}
