import { useI18n } from '../context/i18n';
import { Link } from 'react-router-dom';

export default function About() {
  const { t } = useI18n();

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 py-12">
      <h1 className="font-display text-4xl font-bold text-sangam-ink">{t('about.title')}</h1>
      <p className="mt-6 text-lg text-slate-700 leading-relaxed">{t('about.body')}</p>
      <div className="mt-8 panel p-6 space-y-4">
        <p className="text-slate-700">{t('about.privacy')}</p>
        <p className="text-slate-700">{t('about.honesty')}</p>
      </div>
      <div className="mt-8 flex flex-wrap gap-3">
        <Link to="/report" className="btn-primary">{t('cta.speak')}</Link>
        <Link to="/explore" className="btn-secondary">{t('cta.explore')}</Link>
      </div>
    </div>
  );
}
