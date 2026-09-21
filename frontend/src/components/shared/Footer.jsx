import { Link } from 'react-router-dom';

export default function Footer() {
  return (
    <footer className="border-t border-slate-200 bg-white/70 mt-auto">
      <div className="max-w-7xl mx-auto px-4 py-6 text-sm text-slate-600 flex flex-wrap gap-4 justify-between items-center">
        <p>
          <strong className="text-sangam-ink">SANGAM</strong> — a community innovation network for SIH26043.
          AI makes reporting easier; it is not the product.
        </p>
        <div className="flex flex-wrap gap-4 items-center text-xs">
          <Link to="/how-it-works" className="hover:underline">How it works</Link>
          <Link to="/about" className="hover:underline">About</Link>
          <Link to="/demo" className="hover:underline">Demo guide</Link>
          <span className="font-semibold text-amber-800">Demo Data</span>
          <span className="font-semibold text-blue-800">Real Functionality</span>
        </div>
      </div>
    </footer>
  );
}
