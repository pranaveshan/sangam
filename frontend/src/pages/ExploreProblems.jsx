import { useEffect, useMemo, useState } from 'react';
import { Link, useParams, useNavigate } from 'react-router-dom';
import { useI18n } from '../context/i18n';
import { challengesAPI, problemsAPI } from '../utils/api';
import DemoBadge from '../components/shared/DemoBadge';
import useStore from '../context/store';

const ROLE_LINKS = [
  { key: 'student', to: '/login/ssc' },
  { key: 'researcher', to: '/login/university' },
  { key: 'industry', to: '/login/csr' },
  { key: 'volunteer', to: '/login/citizen' },
];

export default function ExploreProblems() {
  const { t } = useI18n();
  const { id } = useParams();
  const navigate = useNavigate();
  const { isAuthenticated } = useStore();
  const [problems, setProblems] = useState([]);
  const [detail, setDetail] = useState(null);
  const [matches, setMatches] = useState([]);
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    challengesAPI.list()
      .then((r) => setProblems(r.data || []))
      .catch(() => setProblems([]))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (!id) {
      setDetail(null);
      setMatches([]);
      return;
    }
    challengesAPI.get(id)
      .then((r) => setDetail(r.data))
      .catch(() => setDetail(null));
    problemsAPI.match(id)
      .then((r) => setMatches(r.data?.matches || r.data || []))
      .catch(() => setMatches([]));
  }, [id]);

  const categories = useMemo(() => {
    const set = new Set(problems.map((p) => p.domain || p.category).filter(Boolean));
    return Array.from(set).sort();
  }, [problems]);

  const filtered = problems.filter((p) => {
    const q = search.toLowerCase();
    const hay = `${p.title} ${p.description} ${p.location} ${p.domain || ''}`.toLowerCase();
    const catOk = !category || p.domain === category || p.category === category;
    return catOk && (!q || hay.includes(q));
  });

  if (id && detail) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-10">
        <button type="button" className="btn-secondary mb-6" onClick={() => navigate('/explore')}>
          ← {t('nav.explore')}
        </button>
        <div className="flex flex-wrap items-start gap-3 mb-4">
          <h1 className="font-display text-3xl font-bold flex-1">{detail.title}</h1>
          {detail.is_demo && <DemoBadge label={t('common.demoData')} tone="amber" />}
        </div>
        <p className="text-slate-700 leading-relaxed whitespace-pre-wrap">{detail.description}</p>
        <dl className="mt-6 grid sm:grid-cols-2 gap-4 text-sm">
          <div className="panel p-4">
            <dt className="text-slate-500 font-medium">{t('report.category')}</dt>
            <dd className="mt-1 font-semibold">{detail.domain || detail.category}</dd>
          </div>
          <div className="panel p-4">
            <dt className="text-slate-500 font-medium">{t('home.status')}</dt>
            <dd className="mt-1 font-semibold">{detail.status}</dd>
          </div>
          <div className="panel p-4 sm:col-span-2">
            <dt className="text-slate-500 font-medium">{t('report.location')}</dt>
            <dd className="mt-1 font-semibold">{detail.location}{detail.district ? `, ${detail.district}` : ''}</dd>
          </div>
        </dl>

        {detail.required_expertise?.length > 0 && (
          <div className="mt-6">
            <h2 className="font-semibold mb-2">{t('report.expertise')}</h2>
            <div className="flex flex-wrap gap-2">
              {detail.required_expertise.map((e) => (
                <span key={e} className="badge bg-teal-50 text-teal-900 border border-teal-100">{e}</span>
              ))}
            </div>
          </div>
        )}

        {matches.length > 0 && (
          <div className="mt-8">
            <h2 className="font-display text-xl font-bold mb-3">{t('report.collaborators')}</h2>
            <ul className="space-y-3">
              {matches.map((m) => (
                <li key={m.university_id || m.university_name} className="panel p-4">
                  <div className="flex flex-wrap gap-2 items-center">
                    <p className="font-semibold">{m.university_name}</p>
                    {(m.is_demo || m.provenance === 'demo') && (
                      <DemoBadge label={t('common.demoData')} tone="amber" />
                    )}
                  </div>
                  <p className="text-sm text-slate-600 mt-2">
                    <span className="font-medium">{t('report.whyMatch')} </span>
                    {m.explanation}
                  </p>
                </li>
              ))}
            </ul>
          </div>
        )}

        <div className="mt-10 panel p-5">
          <h2 className="font-display text-lg font-bold">{t('explore.join')}</h2>
          <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-2">
            {ROLE_LINKS.map((r) => (
              <Link key={r.key} to={r.to} className="btn-secondary text-center text-sm">
                {t(`home.roles.${r.key}`)}
              </Link>
            ))}
          </div>
          {isAuthenticated && (
            <Link to={`/challenges/${detail.id}`} className="btn-primary mt-4 inline-flex">
              {t('explore.viewDetails')}
            </Link>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-10">
      <h1 className="font-display text-4xl font-bold">{t('explore.title')}</h1>
      <p className="mt-2 text-slate-600">{t('explore.subtitle')}</p>

      <div className="mt-8 flex flex-col sm:flex-row gap-3">
        <label className="flex-1">
          <span className="sr-only">{t('explore.search')}</span>
          <input
            className="input min-h-[48px]"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder={t('explore.search')}
          />
        </label>
        <label>
          <span className="sr-only">{t('explore.filterCategory')}</span>
          <select
            className="input min-h-[48px]"
            value={category}
            onChange={(e) => setCategory(e.target.value)}
          >
            <option value="">{t('explore.allCategories')}</option>
            {categories.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
        </label>
      </div>

      {loading ? (
        <p className="mt-10 text-slate-500">{t('common.loading')}</p>
      ) : (
        <div className="mt-8 grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {filtered.map((p) => (
            <Link
              key={p.id}
              to={`/explore/${p.id}`}
              className="panel p-5 hover:shadow-md transition block focus-visible:ring-2 focus-visible:ring-teal-600"
            >
              <div className="flex gap-2 items-start justify-between">
                <h2 className="font-display text-lg font-semibold">{p.title}</h2>
                {p.is_demo && <DemoBadge label={t('common.demoData')} tone="amber" />}
              </div>
              <p className="text-sm text-slate-600 mt-2 line-clamp-3">{p.description}</p>
              <p className="text-xs text-slate-500 mt-3">{p.domain || p.category} · {p.status}</p>
            </Link>
          ))}
          {filtered.length === 0 && (
            <p className="text-slate-500 col-span-full">{t('explore.empty')}</p>
          )}
        </div>
      )}
    </div>
  );
}
