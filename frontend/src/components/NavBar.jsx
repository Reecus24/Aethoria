import { Shield } from 'lucide-react';

export const NavBar = ({ onJoin, onLogin }) => {
  return (
    <nav
      className="relative z-40 px-4 sm:px-6 lg:px-8"
      style={{
        backgroundColor: 'var(--aeth-stone-1)',
        borderBottom: '1px solid var(--aeth-iron)',
      }}
    >
      <div className="max-w-7xl mx-auto flex items-center justify-between h-14">
        {/* Logo */}
        <div className="flex items-center gap-2">
          <Shield size={18} style={{ color: 'var(--aeth-gold)' }} />
          <span
            style={{
              fontFamily: "'Cinzel', serif",
              fontSize: '1rem',
              fontWeight: 700,
              color: 'var(--aeth-parchment)',
              letterSpacing: '0.08em',
            }}
          >
            Realm of Aethoria
          </span>
        </div>

        {/* Nav links (desktop) */}
        <div className="hidden md:flex items-center gap-6">
          {['Features', 'Paths', 'Leaderboard', 'Chronicles'].map((link) => (
            <a
              key={link}
              href={`#${link.toLowerCase()}`}
              className="text-sm"
              style={{
                color: 'var(--aeth-parchment-dim)',
                textDecoration: 'none',
                fontFamily: "'Cinzel', serif",
                letterSpacing: '0.04em',
                transition: 'color 0.2s ease',
              }}
              onMouseEnter={(e) => { e.currentTarget.style.color = 'var(--aeth-gold)'; }}
              onMouseLeave={(e) => { e.currentTarget.style.color = 'var(--aeth-parchment-dim)'; }}
            >
              {link}
            </a>
          ))}
        </div>

        {/* Auth buttons */}
        <div className="flex items-center gap-3">
          <button
            data-testid="open-login-modal-button"
            onClick={onLogin}
            className="btn-iron px-4 py-1.5 rounded-lg text-sm"
          >
            Login
          </button>
          <button
            data-testid="open-register-modal-button"
            onClick={onJoin}
            className="btn-gold px-4 py-1.5 rounded-lg text-sm"
          >
            Join
          </button>
        </div>
      </div>
    </nav>
  );
};
