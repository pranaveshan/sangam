import { Link, NavLink, useNavigate } from 'react-router-dom';
import useStore, { ROLE_META } from '../../context/store';
import { useI18n } from '../../context/i18n';
import DemoBadge from './DemoBadge';

export default function Header() {
  const { isAuthenticated, currentRole, currentUser, currentPortal, logout } = useStore();
  const { t, lang, setLang, languages } = useI18n();
  const navigate = useNavigate();
  const meta = ROLE_META[currentRole] || ROLE_META.citizen;
  const color = currentPortal?.color || meta.color;

  const onLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className="sticky top-0 z-40 border-b border-slate-200/80 bg-white/90 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3 flex flex-wrap items-center gap-3 justify-between">
        <Link to="/" className="flex items-center gap-3 focus-visible:outline focus-visible:outline-2 focus-visible:outline-teal-700 rounded-lg">
          <div
            className="w-10 h-10 rounded-lg flex items-center justify-center text-white font-display text-xl font-bold"
            style={{ background: isAuthenticated ? color : '#0f172a' }}
            aria-hidden
          >
            S
          </div>
          <div>
            <div className="font-display text-xl font-bold leading-none">{t('brand')}</div>
            <div className="text-[11px] text-slate-500 mt-0.5">
              {isAuthenticated
                ? (currentPortal?.title || meta.portalTitle)
                : 'Community innovation network'}
            </div>
          </div>
        </Link>

        <nav className="flex flex-wrap items-center gap-1 text-sm" aria-label="Main">
          <NavLink to="/" className={navCls} end>{t('nav.home')}</NavLink>
          <NavLink to="/explore" className={navCls}>{t('nav.explore')}</NavLink>
          <NavLink to="/how-it-works" className={navCls}>{t('nav.howItWorks')}</NavLink>
          <NavLink to="/projects" className={navCls}>{t('nav.projects')}</NavLink>
          <NavLink to="/about" className={navCls}>{t('nav.about')}</NavLink>
          <NavLink to="/report" className={navCls}>{t('nav.report')}</NavLink>
          {isAuthenticated && (
            <>
              <NavLink to="/dashboard" className={navCls}>{t('nav.workspace')}</NavLink>
              {(currentRole === 'government' || currentRole === 'citizen' || currentRole === 'industry' || currentRole === 'university') && (
                <NavLink to="/impact" className={navCls}>{t('nav.impact')}</NavLink>
              )}
            </>
          )}
        </nav>

        <div className="flex items-center gap-2 flex-wrap">
          <label className="sr-only" htmlFor="lang-select">Language</label>
          <select
            id="lang-select"
            className="text-sm border border-slate-300 rounded-lg px-2 py-1.5 bg-white min-h-[40px]"
            value={lang}
            onChange={(e) => setLang(e.target.value)}
          >
            {languages.map((l) => (
              <option key={l.code} value={l.code}>{l.native}</option>
            ))}
          </select>

          <DemoBadge label="Demo Auth" />
          {isAuthenticated ? (
            <>
              <span
                className="hidden sm:inline badge border text-white"
                style={{ background: color, borderColor: color }}
              >
                {meta.label}
              </span>
              <span className="hidden md:inline text-xs text-slate-600 max-w-[140px] truncate">
                {currentUser?.name}
              </span>
              <button type="button" className="btn-secondary text-xs py-1.5 min-h-[40px]" onClick={onLogout}>
                {t('nav.logout')}
              </button>
            </>
          ) : (
            <Link to="/login" className="btn-primary text-xs py-1.5 min-h-[40px]">{t('nav.signIn')}</Link>
          )}
        </div>
      </div>
    </header>
  );
}

function navCls({ isActive }) {
  return `px-3 py-2 rounded-md min-h-[40px] inline-flex items-center ${
    isActive ? 'bg-slate-100 font-semibold' : 'text-slate-600 hover:bg-slate-50'
  }`;
}
