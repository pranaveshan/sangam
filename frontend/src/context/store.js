import { create } from 'zustand';
import { persist } from 'zustand/middleware';

const ROLE_META = {
  citizen: {
    label: 'Citizen',
    portalTitle: 'Citizen Portal',
    slug: 'citizen',
    accent: 'citizen',
    color: '#1d4ed8',
    nav: ['dashboard', 'submit', 'rag', 'impact'],
  },
  government: {
    label: 'Admin / Government',
    portalTitle: 'Admin Portal',
    slug: 'admin',
    accent: 'gov',
    color: '#a16207',
    nav: ['dashboard', 'impact', 'rag', 'demo'],
  },
  university: {
    label: 'University',
    portalTitle: 'University Portal',
    slug: 'university',
    accent: 'uni',
    color: '#0f766e',
    nav: ['dashboard', 'rag', 'impact'],
  },
  student: {
    label: 'Student / SSC',
    portalTitle: 'Student / SSC Portal',
    slug: 'ssc',
    accent: 'student',
    color: '#047857',
    nav: ['dashboard', 'rag'],
  },
  industry: {
    label: 'Industry / CSR',
    portalTitle: 'Industry / CSR Portal',
    slug: 'csr',
    accent: 'industry',
    color: '#334155',
    nav: ['dashboard', 'impact', 'rag'],
  },
};

const useStore = create(
  persist(
    (set, get) => ({
      isAuthenticated: false,
      authToken: null,
      currentRole: null,
      currentUser: null,
      currentPortal: null,
      demoUsers: [],
      lastSubmission: null,

      setDemoUsers: (users) => set({ demoUsers: users }),

      loginSuccess: ({ token, user, portal }) =>
        set({
          isAuthenticated: true,
          authToken: token,
          currentUser: user,
          currentRole: user.role,
          currentPortal: portal,
        }),

      logout: () =>
        set({
          isAuthenticated: false,
          authToken: null,
          currentUser: null,
          currentRole: null,
          currentPortal: null,
        }),

      /** Demo-only quick switch kept for judges who are already logged in as admin tooling — prefer logout+login */
      setRole: (role) => {
        const users = get().demoUsers;
        const match = users.find((u) => u.role === role);
        if (!get().isAuthenticated) return;
        set({ currentRole: role, currentUser: match || get().currentUser });
      },

      setLastSubmission: (payload) => set({ lastSubmission: payload }),
      roleMeta: () => ROLE_META[get().currentRole] || ROLE_META.citizen,
    }),
    { name: 'sangam-auth-session-v2' }
  )
);

export { ROLE_META };
export default useStore;
