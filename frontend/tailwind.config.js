/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        sangam: {
          ink: '#0f172a',
          mist: '#e8eef6',
          sand: '#f3efe6',
          citizen: '#1d4ed8',
          gov: '#a16207',
          uni: '#0f766e',
          student: '#047857',
          industry: '#334155',
          accent: '#c2410c',
        },
      },
      fontFamily: {
        display: ['"Source Serif 4"', 'Georgia', 'serif'],
        sans: ['"IBM Plex Sans"', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        panel: '0 1px 2px rgba(15,23,42,0.06), 0 8px 24px rgba(15,23,42,0.06)',
      },
    },
  },
  plugins: [],
};
