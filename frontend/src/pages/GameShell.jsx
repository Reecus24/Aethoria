import { useState, useEffect } from 'react';
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import axios from '../utils/axios';
import { 
  Home, Dumbbell, Skull, Swords, Scroll, Package, ShoppingCart, 
  Store, Landmark, Users, Dice6, Map, CircleDollarSign, Trophy,
  Hospital, LockKeyhole, Target, Castle, MessageSquare, Award,
  Settings, LogOut, Menu, X, Crown, Heart, Zap, User, Bot
} from 'lucide-react';
import { toast } from 'sonner';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export const GameShell = () => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [gameState, setGameState] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user) {
      navigate('/');
      return;
    }
    fetchGameState();
    const interval = setInterval(fetchGameState, 30000); // Update every 30s
    return () => clearInterval(interval);
  }, [user]);

  const fetchGameState = async () => {
    try {
      const res = await axios.get(`${API}/game/state`);
      setGameState(res.data);
      setLoading(false);
    } catch (err) {
      console.error('Failed to fetch game state:', err);
      setLoading(false);
    }
  };

  const navItems = [
    { path: '/game', icon: Home, label: 'Dashboard', exact: true, paths: ['knight', 'shadow', 'noble'] },
    { path: '/game/character', icon: User, label: 'Character', paths: ['knight', 'shadow', 'noble'] },
    { path: '/game/training', icon: Dumbbell, label: 'Training Grounds', paths: ['knight', 'shadow', 'noble'] },
    { path: '/game/crimes', icon: Skull, label: 'Dark Deeds', paths: ['shadow'] },
    { path: '/game/combat', icon: Swords, label: 'Combat', paths: ['knight', 'shadow', 'noble'] },
    { path: '/game/quests', icon: Scroll, label: 'Quests', paths: ['knight', 'shadow', 'noble'] },
    { path: '/game/inventory', icon: Package, label: 'Inventory', paths: ['knight', 'shadow', 'noble'] },
    { path: '/game/shop', icon: Store, label: 'Armour Shop', paths: ['knight', 'shadow', 'noble'] },
    { path: '/game/market', icon: ShoppingCart, label: 'Markets', paths: ['noble'] },
    { path: '/game/bank', icon: Landmark, label: 'Royal Bank', paths: ['noble', 'knight'] },
    { path: '/game/guilds', icon: Users, label: 'Guilds & Orders', paths: ['knight', 'shadow', 'noble'] },
    { path: '/game/tavern', icon: Dice6, label: 'Tavern', paths: ['knight', 'shadow', 'noble'] },
    { path: '/game/travel', icon: Map, label: 'Realm Map', paths: ['knight', 'shadow', 'noble'] },
    { path: '/game/hunting', icon: Target, label: 'Creature Hunting', paths: ['knight', 'shadow'] },
    { path: '/game/properties', icon: Castle, label: 'Strongholds', paths: ['noble'] },
    { path: '/game/bounties', icon: CircleDollarSign, label: "Hunter's Contracts", paths: ['shadow', 'knight'] },
    { path: '/game/hospital', icon: Hospital, label: "Healer's Sanctuary", paths: ['knight', 'shadow', 'noble'] },
    { path: '/game/dungeon', icon: LockKeyhole, label: 'The Dungeon', paths: ['knight', 'shadow', 'noble'] },
    { path: '/game/achievements', icon: Award, label: 'Royal Honours', paths: ['knight', 'shadow', 'noble'] },
    { path: '/game/messages', icon: MessageSquare, label: 'Messages', paths: ['knight', 'shadow', 'noble'] },
    { path: '/game/gazette', icon: Trophy, label: 'Royal Gazette', paths: ['knight', 'shadow', 'noble'] },
    { path: '/game/bot-testing', icon: Bot, label: '🤖 Bot-Tests', paths: ['knight', 'shadow', 'noble'] },
  ];

  // Filter navigation based on user's path
  const userPath = gameState?.user?.path || 'knight';
  const filteredNavItems = navItems.filter(item => item.paths.includes(userPath));

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: 'var(--aeth-stone-0)' }}>
        <div className="text-center">
          <div className="animate-spin w-12 h-12 border-4 border-t-transparent rounded-full mx-auto mb-4" style={{ borderColor: 'var(--aeth-gold)', borderTopColor: 'transparent' }}></div>
          <p style={{ color: 'var(--aeth-parchment)', fontFamily: "'Cinzel', serif" }}>Loading Realm...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex" style={{ backgroundColor: 'var(--aeth-stone-0)' }}>
      {/* Sidebar */}
      <aside
        className="fixed left-0 top-0 h-full z-40 transition-transform duration-300"
        style={{
          width: sidebarOpen ? '260px' : '0px',
          backgroundColor: 'var(--aeth-stone-1)',
          borderRight: '1px solid var(--aeth-iron)',
          transform: sidebarOpen ? 'translateX(0)' : 'translateX(-100%)'
        }}
      >
        <div className="h-full overflow-y-auto p-4" style={{ paddingTop: '80px' }}>
          <nav className="space-y-1">
            {filteredNavItems.map(item => {
              const Icon = item.icon;
              const isActive = item.exact ? location.pathname === item.path : location.pathname.startsWith(item.path);
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className="flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm transition-all"
                  style={{
                    backgroundColor: isActive ? 'rgba(214,162,77,0.15)' : 'transparent',
                    color: isActive ? 'var(--aeth-gold)' : 'var(--aeth-parchment-dim)',
                    fontFamily: "'IBM Plex Sans', sans-serif",
                    fontWeight: isActive ? 600 : 400,
                    borderLeft: isActive ? '3px solid var(--aeth-gold)' : '3px solid transparent'
                  }}
                  data-testid={`nav-${item.path.split('/').pop()}`}
                >
                  <Icon size={18} />
                  {item.label}
                </Link>
              );
            })}
          </nav>
        </div>
      </aside>

      {/* Main Content */}
      <div
        className="flex-1 transition-all duration-300"
        style={{ marginLeft: sidebarOpen ? '260px' : '0px' }}
      >
        {/* Topbar */}
        <header
          className="fixed top-0 right-0 h-16 z-50 flex items-center justify-between px-6"
          style={{
            left: sidebarOpen ? '260px' : '0px',
            backgroundColor: 'var(--aeth-stone-1)',
            borderBottom: '1px solid var(--aeth-iron)',
            transition: 'left 0.3s'
          }}
        >
          <div className="flex items-center gap-4">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-2 rounded-lg"
              style={{ color: 'var(--aeth-gold)' }}
              data-testid="sidebar-toggle"
            >
              {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
            </button>
            <h1
              className="text-lg font-bold"
              style={{ color: 'var(--aeth-parchment)', fontFamily: "'Cinzel', serif" }}
            >
              Realm of Aethoria
            </h1>
          </div>

          {/* HUD Stats */}
          {gameState && (
            <div className="flex items-center gap-6">
              {/* Gold */}
              <div className="flex items-center gap-2 text-sm" data-testid="hud-gold">
                <Crown size={16} style={{ color: 'var(--aeth-gold)' }} />
                <span style={{ color: 'var(--aeth-gold)', fontFamily: "'Azeret Mono', monospace", fontWeight: 600 }}>
                  {gameState.resources.gold.toLocaleString()}
                </span>
              </div>

              {/* Energy */}
              <div className="flex items-center gap-2 text-sm" data-testid="hud-energy">
                <Zap size={16} style={{ color: '#FFC107' }} />
                <span style={{ color: 'var(--aeth-parchment)', fontFamily: "'Azeret Mono', monospace" }}>
                  {gameState.resources.energy}/{gameState.resources.energy_max}
                </span>
              </div>

              {/* HP */}
              <div className="flex items-center gap-2 text-sm" data-testid="hud-hp">
                <Heart size={16} style={{ color: '#E57373' }} />
                <span style={{ color: 'var(--aeth-parchment)', fontFamily: "'Azeret Mono', monospace" }}>
                  {gameState.resources.hp}/{gameState.resources.hp_max}
                </span>
              </div>

              {/* Level */}
              <div
                className="px-3 py-1 rounded-full text-xs font-semibold"
                style={{
                  backgroundColor: 'rgba(214,162,77,0.15)',
                  color: 'var(--aeth-gold)',
                  border: '1px solid rgba(214,162,77,0.3)',
                  fontFamily: "'Cinzel', serif"
                }}
                data-testid="hud-level"
              >
                Lvl {gameState.user.level}
              </div>

              {/* User menu */}
              <button
                onClick={logout}
                className="p-2 rounded-lg transition-colors"
                style={{ color: 'var(--aeth-parchment-dim)' }}
                data-testid="logout-btn"
                title="Abmelden"
              >
                <LogOut size={18} />
              </button>
            </div>
          )}
        </header>

        {/* Content Area */}
        <main
          className="pt-20 px-6 pb-8"
          style={{ minHeight: '100vh' }}
        >
          <Outlet context={{ gameState, refreshGameState: fetchGameState }} />
        </main>
      </div>
    </div>
  );
};