import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'sonner';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import '@/App.css';

// Landing Page Components
import LandingPage from './pages/LandingPage';

// Game Pages
import { GameShell } from './pages/GameShell';
import GameDashboard from './pages/GameDashboard';
import TrainingPage from './pages/TrainingPage';
import CrimesPage from './pages/CrimesPage';
import CombatPage from './pages/CombatPage';
import QuestsPage from './pages/QuestsPage';
import InventoryPage from './pages/InventoryPage';
import ShopPage from './pages/ShopPage';
import MarketPage from './pages/MarketPage';
import BankPage from './pages/BankPage';
import GuildsPage from './pages/GuildsPage';
import TavernPage from './pages/TavernPage';
import MapPage from './pages/MapPage';
import HuntingPage from './pages/HuntingPage';
import BountiesPage from './pages/BountiesPage';
import PropertiesPage from './pages/PropertiesPage';
import MailPage from './pages/MailPage';
import HospitalPage from './pages/HospitalPage';
import DungeonPage from './pages/DungeonPage';
import AchievementsPage from './pages/AchievementsPage';
import GazettePage from './pages/GazettePage';
import CharacterPage from './pages/CharacterPage';
import BotTestingPage from './pages/BotTestingPage';

// Protected Route wrapper
function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: 'var(--aeth-stone-0)' }}>
        <div className="text-center">
          <div
            className="animate-spin w-12 h-12 border-4 border-t-transparent rounded-full mx-auto mb-4"
            style={{ borderColor: 'var(--aeth-gold)', borderTopColor: 'transparent' }}
          ></div>
          <p style={{ color: 'var(--aeth-parchment)', fontFamily: "'Cinzel', serif" }}>Loading...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/" replace />;
  }

  return children;
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <Toaster
          position="top-center"
          toastOptions={{
            style: {
              backgroundColor: 'var(--aeth-stone-2)',
              border: '1px solid var(--aeth-gold)',
              color: 'var(--aeth-parchment)',
              fontFamily: "'IBM Plex Sans', sans-serif",
              boxShadow: '0 8px 32px rgba(0,0,0,0.6)',
            },
          }}
          richColors
        />

        <Routes>
          {/* Public Landing Page */}
          <Route path="/" element={<LandingPage />} />

          {/* Protected Game Routes */}
          <Route
            path="/game"
            element={
              <ProtectedRoute>
                <GameShell />
              </ProtectedRoute>
            }
          >
            <Route index element={<GameDashboard />} />
            <Route path="character" element={<CharacterPage />} />
            <Route path="training" element={<TrainingPage />} />
            <Route path="crimes" element={<CrimesPage />} />
            <Route path="combat" element={<CombatPage />} />
            <Route path="quests" element={<QuestsPage />} />
            <Route path="inventory" element={<InventoryPage />} />
            <Route path="shop" element={<ShopPage />} />
            <Route path="market" element={<MarketPage />} />
            <Route path="bank" element={<BankPage />} />
            <Route path="guilds" element={<GuildsPage />} />
            <Route path="tavern" element={<TavernPage />} />
            <Route path="travel" element={<MapPage />} />
            <Route path="hunting" element={<HuntingPage />} />
            <Route path="bounties" element={<BountiesPage />} />
            <Route path="properties" element={<PropertiesPage />} />
            <Route path="messages" element={<MailPage />} />
            <Route path="hospital" element={<HospitalPage />} />
            <Route path="dungeon" element={<DungeonPage />} />
            <Route path="achievements" element={<AchievementsPage />} />
            <Route path="gazette" element={<GazettePage />} />
            <Route path="bot-testing" element={<BotTestingPage />} />
          </Route>

          {/* Fallback */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
