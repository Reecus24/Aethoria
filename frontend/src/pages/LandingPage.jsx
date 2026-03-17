import { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from '../utils/axios';
import { toast } from 'sonner';

import { useAuth } from '../contexts/AuthContext';
import { NavBar } from '../components/NavBar';
import { EventTicker } from '../components/EventTicker';
import { HeroSection } from '../components/HeroSection';
import { AboutSection } from '../components/AboutSection';
import { OnlineCounter } from '../components/OnlineCounter';
import { FeaturesSection } from '../components/FeaturesSection';
import { LeaderboardSection } from '../components/LeaderboardSection';
import { ReviewsSection } from '../components/ReviewsSection';
import { PathsSection } from '../components/PathsSection';
import { GamePreviewSection } from '../components/GamePreviewSection';
import { KingdomsSection } from '../components/KingdomsSection';
import { NewsSection } from '../components/NewsSection';
import { SiteFooter } from '../components/SiteFooter';
import { LoginModal, RegisterModal } from '../components/AuthModals';
import { CharacterDashboard } from '../components/CharacterDashboard';
import { BackToTop } from '../components/BackToTop';
import {
  FeaturesSkeletonSection,
  LeaderboardSkeleton,
  ReviewsSkeleton,
  NewsSkeleton,
} from '../components/SkeletonLoaders';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// Placeholder ticker events shown immediately before API loads (generic messages only, no fake character names)
const PLACEHOLDER_TICKER = [
  { event: 'Das Reich von Aethoria erwacht... Trete bei und schreibe Geschichte!', type: 'quest' },
  { event: 'Neue Abenteurer betreten täglich das Reich — sei einer von ihnen!', type: 'quest' },
  { event: 'Die Heldenhalle wartet auf deinen Namen — beginne deine Legende jetzt!', type: 'combat' },
];

export default function LandingPage() {
  const { user, loading: authLoading } = useAuth();
  const navigate = useNavigate();
  const [landingData, setLandingData] = useState(null);
  const [dataLoading, setDataLoading] = useState(true);
  const [loginOpen, setLoginOpen] = useState(false);
  const [registerOpen, setRegisterOpen] = useState(false);
  const [dashboardOpen, setDashboardOpen] = useState(false);

  // Redirect to game if already logged in
  useEffect(() => {
    if (user && !authLoading) {
      navigate('/game');
    }
  }, [user, authLoading, navigate]);

  const fetchLanding = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/landing`);
      setLandingData(res.data);
    } catch (err) {
      console.error('Failed to load landing data:', err);
      toast.error('Could not connect to the Realm. Please try again.', {
        style: { backgroundColor: 'rgba(142,29,44,0.9)', border: '1px solid rgba(142,29,44,0.6)', color: '#fff' },
      });
    } finally {
      setDataLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchLanding();
  }, [fetchLanding]);

  const handleLoginSuccess = (data) => {
    toast.success(data.message, { duration: 5000, icon: '⚔️' });
    // Navigation now handled directly in AuthModals for reliability
  };

  const handleRegisterSuccess = (data) => {
    toast.success(data.message, { duration: 6000, icon: '🏰' });
    // Navigation now handled directly in AuthModals for reliability
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
      {/* Event Ticker - show placeholder immediately, replace with real data when loaded */}
      <EventTicker
        events={landingData?.ticker && landingData.ticker.length > 0 ? landingData.ticker : PLACEHOLDER_TICKER}
      />

      {/* Navigation */}
      <NavBar
        onLogin={handleOpenLogin}
        onJoin={handleOpenRegister}
        onOpenDashboard={() => setDashboardOpen(true)}
      />

      {/* Hero */}
      <HeroSection onLogin={handleOpenLogin} onJoin={handleOpenRegister} />

      {/* Online Counter */}
      {!dataLoading && <OnlineCounter online={landingData?.online} />}

      {/* About */}
      <AboutSection
        stats={{
          features: landingData?.features?.length || 42,
          kingdoms: landingData?.kingdoms?.length || 11,
        }}
      />

      {/* Features */}
      {dataLoading ? <FeaturesSkeletonSection /> : <FeaturesSection features={landingData?.features || []} />}

      {/* Leaderboard */}
      {dataLoading ? <LeaderboardSkeleton /> : <LeaderboardSection leaderboard={landingData?.leaderboard || []} />}

      {/* Reviews */}
      {dataLoading ? (
        <ReviewsSkeleton />
      ) : (
        <ReviewsSection reviews={landingData?.reviews || []} onReviewSubmitted={fetchLanding} />
      )}

      {/* Paths */}
      <PathsSection paths={landingData?.paths || []} />

      {/* Game Preview terminal */}
      <GamePreviewSection />

      {/* 11 Kingdoms */}
      <KingdomsSection kingdoms={landingData?.kingdoms || []} />

      {/* News */}
      {dataLoading ? <NewsSkeleton /> : <NewsSection news={landingData?.news || []} />}

      {/* Footer */}
      <SiteFooter onLogin={handleOpenLogin} onJoin={handleOpenRegister} />

      {/* Floating Back to Top */}
      <BackToTop />

      {/* Auth Modals */}
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

      {/* Character Dashboard */}
      <CharacterDashboard open={dashboardOpen && !!user} onClose={() => setDashboardOpen(false)} />
    </div>
  );
}
