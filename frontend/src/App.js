import { useEffect, useState, useCallback } from 'react';
import '@/App.css';
import axios from 'axios';
import { Toaster } from '@/components/ui/sonner';
import { toast } from 'sonner';

import { NavBar } from './components/NavBar';
import { EventTicker } from './components/EventTicker';
import { HeroSection } from './components/HeroSection';
import { AboutSection } from './components/AboutSection';
import { OnlineCounter } from './components/OnlineCounter';
import { FeaturesSection } from './components/FeaturesSection';
import { LeaderboardSection } from './components/LeaderboardSection';
import { ReviewsSection } from './components/ReviewsSection';
import { PathsSection } from './components/PathsSection';
import { NewsSection } from './components/NewsSection';
import { SiteFooter } from './components/SiteFooter';
import { LoginModal, RegisterModal } from './components/AuthModals';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function App() {
  const [landingData, setLandingData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [loginOpen, setLoginOpen] = useState(false);
  const [registerOpen, setRegisterOpen] = useState(false);
  const [user, setUser] = useState(null);

  const fetchLanding = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/landing`);
      setLandingData(res.data);
    } catch (err) {
      console.error('Failed to load landing data:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchLanding();
  }, [fetchLanding]);

  const handleLoginSuccess = (data) => {
    setUser(data);
    toast.success(`⚔️ ${data.message}`);
  };

  const handleRegisterSuccess = (data) => {
    setUser(data);
    toast.success(`🏰 ${data.message}`);
  };

  const handleOpenLogin = () => {
    setRegisterOpen(false);
    setLoginOpen(true);
  };

  const handleOpenRegister = () => {
    setLoginOpen(false);
    setRegisterOpen(true);
  };

  return (
    <div className="App" style={{ backgroundColor: 'var(--aeth-stone-0)', minHeight: '100vh' }}>
      {/* Toast notifications */}
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            backgroundColor: 'var(--aeth-stone-2)',
            border: '1px solid var(--aeth-gold)',
            color: 'var(--aeth-parchment)',
            fontFamily: "'IBM Plex Sans', sans-serif",
          },
        }}
      />

      {/* Authenticated user banner */}
      {user && (
        <div
          className="text-center py-2 text-sm"
          style={{
            backgroundColor: 'rgba(214,162,77,0.12)',
            borderBottom: '1px solid rgba(214,162,77,0.3)',
            color: 'var(--aeth-gold)',
            fontFamily: "'Cinzel', serif",
            letterSpacing: '0.04em',
          }}
        >
          ⚔️ Welcome, {user.username} — Level {user.level} {user.title} — Your legend continues
        </div>
      )}

      {/* Event Ticker */}
      <EventTicker events={landingData?.ticker || []} />

      {/* Navigation */}
      <NavBar onLogin={handleOpenLogin} onJoin={handleOpenRegister} />

      {/* Hero */}
      <HeroSection onLogin={handleOpenLogin} onJoin={handleOpenRegister} />

      {/* Online Counter */}
      {!loading && <OnlineCounter online={landingData?.online} />}

      {/* About */}
      <AboutSection />

      {/* Features */}
      <FeaturesSection features={landingData?.features || []} />

      {/* Leaderboard */}
      <LeaderboardSection leaderboard={landingData?.leaderboard || []} />

      {/* Reviews */}
      <ReviewsSection reviews={landingData?.reviews || []} />

      {/* Paths */}
      <PathsSection paths={landingData?.paths || []} />

      {/* News */}
      <NewsSection news={landingData?.news || []} />

      {/* Footer */}
      <SiteFooter onLogin={handleOpenLogin} onJoin={handleOpenRegister} />

      {/* Modals */}
      <LoginModal
        open={loginOpen}
        onClose={() => setLoginOpen(false)}
        onSwitchToRegister={handleOpenRegister}
        onSuccess={handleLoginSuccess}
      />
      <RegisterModal
        open={registerOpen}
        onClose={() => setRegisterOpen(false)}
        onSwitchToLogin={handleOpenLogin}
        onSuccess={handleRegisterSuccess}
      />
    </div>
  );
}
