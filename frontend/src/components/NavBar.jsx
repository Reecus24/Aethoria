import { useState, useEffect } from 'react';
import { Menu, X, Shield, User } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

export const NavBar = ({ onJoin, onLogin, onOpenDashboard }) => {
  const { user, logout } = useAuth();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 60);
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  const navLinks = [
    { label: 'Features', href: '#features' },
    { label: 'Paths', href: '#paths' },
    { label: 'Leaderboard', href: '#leaderboard' },
    { label: 'Chronicles', href: '#chronicles' },
  ];

  const linkStyle = {
    color: 'var(--aeth-parchment-dim)',
    textDecoration: 'none',
    fontFamily: "'Cinzel', serif",
    letterSpacing: '0.04em',
    transition: 'color 0.2s ease',
    fontSize: '0.85rem',
  };

  return (
    <nav
      className="z-40"
      style={{
        backgroundColor: scrolled ? 'rgba(14,12,11,0.96)' : 'var(--aeth-stone-1)',
        borderBottom: '1px solid var(--aeth-iron)',
        backdropFilter: scrolled ? 'blur(8px)' : 'none',
        transition: 'background-color 0.3s ease',
        position: 'sticky',
        top: 0,
      }}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between h-14">
        {/* Logo */}
        <a href="#" className="flex items-center gap-2" style={{ textDecoration: 'none' }}>
          <Shield size={18} style={{ color: 'var(--aeth-gold)' }} />
          <span style={{ fontFamily: "'Cinzel', serif", fontSize: '1rem', fontWeight: 700, color: 'var(--aeth-parchment)', letterSpacing: '0.08em' }}>
            Realm of Aethoria
          </span>
        </a>

        {/* Desktop nav links */}
        <div className="hidden md:flex items-center gap-6">
          {navLinks.map((link) => (
            <a key={link.label} href={link.href} style={linkStyle}
              onMouseEnter={(e) => { e.currentTarget.style.color = 'var(--aeth-gold)'; }}
              onMouseLeave={(e) => { e.currentTarget.style.color = 'var(--aeth-parchment-dim)'; }}
            >{link.label}</a>
          ))}
        </div>

        {/* Auth section */}
        <div className="flex items-center gap-2">
          {user ? (
            // Logged-in state
            <>
              <button
                data-testid="character-dashboard-button"
                onClick={onOpenDashboard}
                className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm"
                style={{
                  backgroundColor: 'rgba(214,162,77,0.1)',
                  border: '1px solid rgba(214,162,77,0.35)',
                  color: 'var(--aeth-gold)',
                  fontFamily: "'Cinzel', serif",
                  letterSpacing: '0.04em',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                  fontSize: '0.8rem',
                }}
                onMouseEnter={(e) => { e.currentTarget.style.backgroundColor = 'rgba(214,162,77,0.18)'; }}
                onMouseLeave={(e) => { e.currentTarget.style.backgroundColor = 'rgba(214,162,77,0.1)'; }}
              >
                <User size={14} />
                {user.username}
              </button>
              <button
                data-testid="logout-button"
                onClick={logout}
                className="btn-iron px-3 py-1.5 rounded-lg text-sm hidden sm:block"
              >
                Logout
              </button>
            </>
          ) : (
            // Guest state
            <>
              <button data-testid="open-login-modal-button" onClick={onLogin} className="btn-iron px-4 py-1.5 rounded-lg text-sm hidden sm:block">Login</button>
              <button data-testid="open-register-modal-button" onClick={onJoin} className="btn-gold px-4 py-1.5 rounded-lg text-sm">Join</button>
            </>
          )}
          {/* Hamburger */}
          <button
            className="md:hidden p-1.5 rounded-lg"
            onClick={() => setMobileOpen(o => !o)}
            aria-label="Toggle menu"
            style={{ backgroundColor: 'var(--aeth-iron-2)', border: '1px solid var(--aeth-iron)', color: 'var(--aeth-parchment-dim)', cursor: 'pointer' }}
          >
            {mobileOpen ? <X size={18} /> : <Menu size={18} />}
          </button>
        </div>
      </div>

      {/* Mobile menu */}
      {mobileOpen && (
        <div className="md:hidden px-4 pb-4 pt-2 flex flex-col gap-3" style={{ backgroundColor: 'var(--aeth-stone-1)', borderTop: '1px solid var(--aeth-iron)' }}>
          {navLinks.map((link) => (
            <a key={link.label} href={link.href} style={{ ...linkStyle, fontSize: '0.9rem', padding: '0.5rem 0' }} onClick={() => setMobileOpen(false)}
              onMouseEnter={(e) => { e.currentTarget.style.color = 'var(--aeth-gold)'; }}
              onMouseLeave={(e) => { e.currentTarget.style.color = 'var(--aeth-parchment-dim)'; }}
            >{link.label}</a>
          ))}
          <div className="flex gap-3 pt-2" style={{ borderTop: '1px solid var(--aeth-iron)' }}>
            {user ? (
              <>
                <button onClick={() => { setMobileOpen(false); onOpenDashboard(); }} className="btn-iron flex-1 py-2 rounded-lg text-sm">
                  ⚔ {user.username}
                </button>
                <button onClick={() => { setMobileOpen(false); logout(); }} className="btn-iron flex-1 py-2 rounded-lg text-sm">Logout</button>
              </>
            ) : (
              <>
                <button onClick={() => { setMobileOpen(false); onLogin(); }} className="btn-iron flex-1 py-2 rounded-lg text-sm">Login</button>
                <button onClick={() => { setMobileOpen(false); onJoin(); }} className="btn-gold flex-1 py-2 rounded-lg text-sm">Join the Realm</button>
              </>
            )}
          </div>
        </div>
      )}
    </nav>
  );
};
