import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useI18n } from '../context/i18n';
import { projectsAPI } from '../utils/api';
import DemoBadge from '../components/shared/DemoBadge';
import useStore from '../context/store';

export default function ProjectsPage() {
  const { t } = useI18n();
  const { isAuthenticated } = useStore();
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    projectsAPI.list()
      .then((r) => setProjects(r.data || []))
      .catch(() => setProjects([]))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-10">
      <h1 className="font-display text-4xl font-bold">{t('projects.title')}</h1>
      <p className="mt-2 text-slate-600">{t('projects.subtitle')}</p>

      {loading && <p className="mt-8 text-slate-500">{t('common.loading')}</p>}

      <div className="mt-8 grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
        {projects.map((p) => (
          <article key={p.id} className="panel p-5">
            <div className="flex gap-2 items-start justify-between">
              <h2 className="font-display text-lg font-semibold">{p.name}</h2>
              {p.is_demo && <DemoBadge label={t('common.demoData')} tone="amber" />}
            </div>
            <p className="text-sm text-slate-600 mt-2 line-clamp-3">{p.goal}</p>
            <p className="text-xs font-semibold text-teal-800 mt-3">{p.status}</p>
            {isAuthenticated ? (
              <Link to={`/projects/${p.id}`} className="text-sm font-semibold text-sangam-uni mt-4 inline-block">
                Open workspace →
              </Link>
            ) : (
              <Link to="/login" className="text-sm font-semibold text-sangam-uni mt-4 inline-block">
                {t('nav.signIn')} →
              </Link>
            )}
          </article>
        ))}
      </div>
      {!loading && projects.length === 0 && (
        <p className="mt-8 text-slate-500">{t('projects.empty')}</p>
      )}
    </div>
  );
}
