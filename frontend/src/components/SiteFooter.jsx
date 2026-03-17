import { Shield, Sword } from 'lucide-react';

export const SiteFooter = ({ onJoin, onLogin }) => {
  return (
    <footer
      data-testid="site-footer"
      style={{
        backgroundColor: 'var(--aeth-stone-1)',
        borderTop: '1px solid var(--aeth-iron)',
      }}
    >
      {/* Final CTA band */}
      <div
        className="py-14 px-4"
        style={{
          background: 'radial-gradient(900px 300px at 50% 50%, rgba(214,162,77,0.06), transparent)',
          borderBottom: '1px solid var(--aeth-iron)',
        }}
      >
        <div className="max-w-2xl mx-auto text-center">
          <h2
            className="mb-3 font-cinzel"
            style={{
              fontFamily: "'Cinzel', serif",
              fontSize: '2rem',
              fontWeight: 700,
              color: 'var(--aeth-parchment)',
              letterSpacing: '0.04em',
            }}
          >
            Your Legend Awaits
          </h2>
          <p
            className="text-base mb-8 leading-relaxed"
            style={{ color: 'var(--aeth-parchment-dim)', fontFamily: "'IBM Plex Sans', sans-serif" }}
          >
            Thousands of adventurers are forging their destiny right now.
            Will you rise to glory — or fade into shadow?
          </p>
          <div className="flex flex-wrap gap-4 justify-center">
            <button
              onClick={onJoin}
              className="btn-gold px-10 py-3 rounded-lg text-base"
              data-testid="footer-join-button"
            >
              Begin Your Legend
            </button>
            <button
              onClick={onLogin}
              className="btn-iron px-10 py-3 rounded-lg text-base"
              data-testid="footer-login-button"
            >
              Enter the Gate
            </button>
          </div>
        </div>
      </div>

      {/* Footer links */}
      <div className="max-w-6xl mx-auto px-4 py-10">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8 mb-8">
          {/* Brand */}
          <div>
            <div className="flex items-center gap-2 mb-3">
              <Shield size={16} style={{ color: 'var(--aeth-gold)' }} />
              <span
                style={{
                  fontFamily: "'Cinzel', serif",
                  color: 'var(--aeth-parchment)',
                  fontWeight: 700,
                  letterSpacing: '0.05em',
                }}
              >
                Realm of Aethoria
              </span>
            </div>
            <p
              className="text-sm"
              style={{ color: 'var(--aeth-iron)', fontFamily: "'IBM Plex Sans', sans-serif", lineHeight: 1.6 }}
            >
              The Dark Medieval Fantasy RPG. Free to play. Forever.
            </p>
          </div>

          {/* Game */}
          <div>
            <h4
              className="text-xs font-semibold uppercase tracking-widest mb-3"
              style={{ color: 'var(--aeth-gold)', fontFamily: "'Cinzel', serif" }}
            >
              The Realm
            </h4>
            <ul className="space-y-2">
              {['About Aethoria', 'Game Features', 'Hall of Legends', 'The Chronicles'].map((l) => (
                <li key={l}>
                  <a
                    href="#"
                    className="text-sm"
                    style={{
                      color: 'var(--aeth-parchment-dim)',
                      textDecoration: 'none',
                      fontFamily: "'IBM Plex Sans', sans-serif",
                      transition: 'color 0.2s ease',
                    }}
                    onMouseEnter={(e) => { e.currentTarget.style.color = 'var(--aeth-gold)'; }}
                    onMouseLeave={(e) => { e.currentTarget.style.color = 'var(--aeth-parchment-dim)'; }}
                  >
                    {l}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          {/* Paths */}
          <div>
            <h4
              className="text-xs font-semibold uppercase tracking-widest mb-3"
              style={{ color: 'var(--aeth-gold)', fontFamily: "'Cinzel', serif" }}
            >
              Paths
            </h4>
            <ul className="space-y-2">
              {['The Knight', 'The Shadow', 'The Noble', 'New Adventurers'].map((l) => (
                <li key={l}>
                  <a
                    href="#"
                    className="text-sm"
                    style={{
                      color: 'var(--aeth-parchment-dim)',
                      textDecoration: 'none',
                      fontFamily: "'IBM Plex Sans', sans-serif",
                      transition: 'color 0.2s ease',
                    }}
                    onMouseEnter={(e) => { e.currentTarget.style.color = 'var(--aeth-gold)'; }}
                    onMouseLeave={(e) => { e.currentTarget.style.color = 'var(--aeth-parchment-dim)'; }}
                  >
                    {l}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          {/* Legal */}
          <div>
            <h4
              className="text-xs font-semibold uppercase tracking-widest mb-3"
              style={{ color: 'var(--aeth-gold)', fontFamily: "'Cinzel', serif" }}
            >
              Legal
            </h4>
            <ul className="space-y-2">
              {['Privacy Policy', 'Cookie Policy', 'Terms of Service', 'Support'].map((l) => (
                <li key={l}>
                  <a
                    href="#"
                    className="text-sm"
                    style={{
                      color: 'var(--aeth-parchment-dim)',
                      textDecoration: 'none',
                      fontFamily: "'IBM Plex Sans', sans-serif",
                      transition: 'color 0.2s ease',
                    }}
                    onMouseEnter={(e) => { e.currentTarget.style.color = 'var(--aeth-gold)'; }}
                    onMouseLeave={(e) => { e.currentTarget.style.color = 'var(--aeth-parchment-dim)'; }}
                  >
                    {l}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Bottom bar */}
        <div
          className="pt-6 flex flex-col sm:flex-row items-center justify-between gap-4"
          style={{ borderTop: '1px solid var(--aeth-iron)' }}
        >
          <p
            className="text-xs"
            style={{ color: 'var(--aeth-iron)', fontFamily: "'Azeret Mono', monospace" }}
          >
            © 2004–2026 Realm of Aethoria Ltd. All rights reserved.
          </p>
          <div className="flex items-center gap-2">
            <Sword size={12} style={{ color: 'var(--aeth-iron)' }} />
            <span
              className="text-xs"
              style={{ color: 'var(--aeth-iron)', fontFamily: "'Azeret Mono', monospace" }}
            >
              Forged in the Dark Ages · Server Uptime: 99.9%
            </span>
          </div>
        </div>
      </div>
    </footer>
  );
};
