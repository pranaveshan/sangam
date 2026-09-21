import { useEffect, useState } from 'react';
import { HashRouter, Routes, Route, Navigate, Link } from 'react-router-dom';
import Header from './components/shared/Header';
import Footer from './components/shared/Footer';
import ProtectedRoute from './components/shared/ProtectedRoute';
import Home from './pages/Home';
import DashboardIndex from './pages/DashboardIndex';
import ChallengeDetail from './pages/ChallengeDetail';
import ProjectWorkspace from './pages/ProjectWorkspace';
import ImpactPage from './pages/ImpactPage';
import DemoGuide from './pages/DemoGuide';
import RagAssistantPage from './pages/RagAssistantPage';
import LoginHub from './pages/LoginHub';
import PortalLogin from './pages/PortalLogin';
import HowItWorks from './pages/HowItWorks';
import About from './pages/About';
import ExploreProblems from './pages/ExploreProblems';
import ProjectsPage from './pages/ProjectsPage';
import ReportFlow from './pages/ReportFlow';
import { I18nProvider, useI18n } from './context/i18n';
import useStore from './context/store';
import { demoAPI, healthAPI, problemsAPI } from './utils/api';
import { isOnline, listPendingReports, removePendingReport } from './utils/offlineQueue';
import './styles/globals.css';

function OfflineBanner() {
  const { t } = useI18n();
  const [online, setOnline] = useState(isOnline());
  const [pending, setPending] = useState(0);

  useEffect(() => {
    const sync = async () => {
      setOnline(navigator.onLine);
      try {
        const items = await listPendingReports();
        setPending(items.length);
        if (navigator.onLine && items.length) {
          for (const item of items) {
            try {
              const form = new FormData();
              form.append('title', item.edits?.problem_title || item.text?.slice(0, 80) || 'Offline report');
              form.append('description', item.edits?.summary || item.text || '');
              form.append('category', item.edits?.category || 'Community');
              form.append('location', item.edits?.location || item.location || 'Not specified');
              form.append('district', 'Unknown');
              form.append('community_impact', item.edits?.social_impact || 'To be assessed');
              form.append('people_affected', String(parseInt(item.people, 10) || 0));
              form.append('language', item.lang || 'en');
              form.append('original_transcript', item.text || '');
              form.append('submitted_with_assistance', String(Boolean(item.assisted)));
              await problemsAPI.create(form);
              await removePendingReport(item.id);
            } catch {
              /* keep queued */
            }
          }
          const left = await listPendingReports();
          setPending(left.length);
        }
      } catch {
        /* ignore */
      }
    };
    sync();
    window.addEventListener('online', sync);
    window.addEventListener('offline', sync);
    return () => {
      window.removeEventListener('online', sync);
      window.removeEventListener('offline', sync);
    };
  }, []);

  if (online && pending === 0) return null;
  return (
    <div className="bg-amber-100 border-b border-amber-200 text-amber-950 text-sm px-4 py-2 text-center" role="status">
      {!online ? t('offline.banner') : `${t('report.pendingSync')}: ${pending}`}
    </div>
  );
}

function AppShell() {
  const { setDemoUsers, isAuthenticated } = useStore();
  const { t } = useI18n();
  const [apiOk, setApiOk] = useState(null);

  useEffect(() => {
    healthAPI.check()
      .then(() => setApiOk(true))
      .catch(() => setApiOk(false));
    demoAPI.users()
      .then((r) => setDemoUsers(r.data))
      .catch(() => {});
  }, [setDemoUsers]);

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <OfflineBanner />
      {apiOk === false && (
        <div className="bg-rose-100 border-b border-rose-200 text-rose-900 text-sm px-4 py-2 text-center">
          Backend unreachable at http://localhost:8100 — start the FastAPI server to enable live data.
        </div>
      )}
      <main className="flex-grow">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/explore" element={<ExploreProblems />} />
          <Route path="/explore/:id" element={<ExploreProblems />} />
          <Route path="/how-it-works" element={<HowItWorks />} />
          <Route path="/about" element={<About />} />
          <Route path="/projects" element={<ProjectsPage />} />
          <Route path="/report" element={<ReportFlow />} />
          <Route path="/login" element={<LoginHub />} />
          <Route path="/login/:portalSlug" element={<PortalLogin />} />
          <Route path="/demo" element={<DemoGuide />} />

          <Route path="/dashboard" element={
            <ProtectedRoute>
              <DashboardIndex />
            </ProtectedRoute>
          } />
          <Route path="/challenge/submit" element={
            <ProtectedRoute roles={['citizen']}>
              <Navigate to="/report" replace />
            </ProtectedRoute>
          } />
          <Route path="/challenges/:id" element={
            <ProtectedRoute>
              <ChallengeDetail />
            </ProtectedRoute>
          } />
          <Route path="/projects/:id" element={
            <ProtectedRoute>
              <ProjectWorkspace />
            </ProtectedRoute>
          } />
          <Route path="/impact" element={
            <ProtectedRoute roles={['government', 'citizen', 'industry', 'university']}>
              <ImpactPage />
            </ProtectedRoute>
          } />
          <Route path="/rag" element={
            <ProtectedRoute>
              <RagAssistantPage />
            </ProtectedRoute>
          } />

          <Route path="/portals" element={<Navigate to="/login" replace />} />
          <Route path="*" element={
            <div className="max-w-xl mx-auto px-4 py-16 text-center">
              <h1 className="font-display text-3xl font-bold">Page not found</h1>
              <Link to={isAuthenticated ? '/dashboard' : '/'} className="btn-primary mt-6 inline-flex">
                {isAuthenticated ? t('nav.workspace') : t('nav.home')}
              </Link>
            </div>
          } />
        </Routes>
      </main>
      <Footer />
    </div>
  );
}

export default function App() {
  return (
    <HashRouter>
      <I18nProvider>
        <AppShell />
      </I18nProvider>
    </HashRouter>
  );
}
