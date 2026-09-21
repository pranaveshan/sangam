import useStore, { ROLE_META } from '../context/store';
import CitizenDashboard from '../components/citizen/CitizenDashboard';
import GovernmentDashboard from '../components/government/GovernmentDashboard';
import UniversityDashboard from '../components/university/UniversityDashboard';
import StudentDashboard from '../components/student/StudentDashboard';
import IndustryDashboard from '../components/industry/IndustryDashboard';
import DemoBadge from '../components/shared/DemoBadge';

export default function DashboardIndex() {
  const { currentRole, currentUser, currentPortal } = useStore();
  const meta = ROLE_META[currentRole] || ROLE_META.citizen;
  const color = currentPortal?.color || meta.color;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-4">
      <div
        className="rounded-xl px-5 py-4 text-white flex flex-wrap justify-between gap-3 items-center"
        style={{ background: `linear-gradient(120deg, ${color}, #0f172a)` }}
      >
        <div>
          <p className="text-xs uppercase tracking-widest text-white/70">Signed in portal</p>
          <h1 className="font-display text-2xl font-bold">{currentPortal?.title || meta.portalTitle}</h1>
          <p className="text-sm text-white/85 mt-1">
            {currentUser?.name}
            {currentUser?.organization ? ` · ${currentUser.organization}` : ''}
            {currentUser?.district ? ` · ${currentUser.district}` : ''}
          </p>
        </div>
        <DemoBadge label="Role-locked workspace" />
      </div>

      {currentRole === 'citizen' && <CitizenDashboard />}
      {currentRole === 'government' && <GovernmentDashboard />}
      {currentRole === 'university' && <UniversityDashboard />}
      {currentRole === 'student' && <StudentDashboard />}
      {currentRole === 'industry' && <IndustryDashboard />}
      {!currentRole && (
        <p className="text-slate-600">No role selected. Please sign in again.</p>
      )}
    </div>
  );
}
