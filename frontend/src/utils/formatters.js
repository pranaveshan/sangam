export const LIFECYCLE = [
  'submitted',
  'under_review',
  'validated',
  'matched',
  'university_accepted',
  'team_formed',
  'industry_collaboration',
  'prototype',
  'testing',
  'pilot',
  'completed',
];

export function formatStatus(status) {
  if (!status) return '—';
  return status
    .split('_')
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ');
}

export function formatNumber(n) {
  if (n == null) return '0';
  return Number(n).toLocaleString('en-IN');
}

export function provenanceLabel(item) {
  if (!item) return 'Unknown';
  if (item.is_demo || item.provenance === 'demo') return 'Demo Data';
  if (item.provenance === 'user') return 'User-generated';
  return item.provenance || 'Prototype';
}
