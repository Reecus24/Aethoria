import { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import axios from '../utils/axios';
import { motion } from 'framer-motion';
import { User, Sword, Shield, Zap, Target, Crown, MapPin, Calendar } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { toast } from 'sonner';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function CharacterPage() {
  const { gameState, refreshGameState } = useOutletContext();
  const [charData, setCharData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (gameState) {
      // Map equipped items from gameState.equipment array
      const equippedItems = {};
      const equipmentArray = gameState.equipment || [];
      
      for (const item of equipmentArray) {
        if (item && item.slot) {
          equippedItems[item.slot] = item;
        }
      }
      
      setCharData({
        name: gameState.user?.username,
        title: gameState.user?.path_label,
        level: gameState.user?.level,
        xp_current: gameState.resources?.xp,
        xp_required: gameState.resources?.xp_required,
        strength: gameState.stats?.strength,
        dexterity: gameState.stats?.dexterity,
        speed: gameState.stats?.speed,
        defense: gameState.stats?.defense,
        equipment: equippedItems,
        location: gameState.location?.kingdom_name || 'Hauptstadt',
        days_in_realm: gameState.user?.days_in_realm,
        combat_wins: gameState.user?.combat_wins || 0,
        combat_losses: gameState.user?.combat_losses || 0,
        crimes_success: gameState.user?.crimes_success || 0,
        crimes_failed: gameState.user?.crimes_failed || 0,
        gold_earned: gameState.user?.gold_earned || 0,
        gold_spent: gameState.user?.gold_spent || 0,
      });
      setLoading(false);
    }
  }, [gameState]);

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto">
        <div className="animate-pulse space-y-6">
          <div className="h-32 bg-[color:var(--aeth-stone-2)] rounded-[var(--radius-card)]"></div>
          <div className="h-64 bg-[color:var(--aeth-stone-2)] rounded-[var(--radius-card)]"></div>
        </div>
      </div>
    );
  }

  const stats = [
    { id: 'strength', label: 'Stärke', value: charData?.strength || 0, total: gameState?.stats?.total_strength, icon: Sword, color: '#E57373' },
    { id: 'dexterity', label: 'Geschicklichkeit', value: charData?.dexterity || 0, icon: Target, color: '#FFB74D' },
    { id: 'speed', label: 'Geschwindigkeit', value: charData?.speed || 0, icon: Zap, color: '#64B5F6' },
    { id: 'defense', label: 'Verteidigung', value: charData?.defense || 0, total: gameState?.stats?.total_defense, icon: Shield, color: '#81C784' },
  ];

  const xpProgress = charData?.xp_current || 0;
  const xpRequired = charData?.xp_required || 100;
  const xpPercent = (xpProgress / xpRequired) * 100;

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header Card */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        <Card className="border-[color:var(--game-border-subtle)] bg-[color:var(--aeth-stone-2)] shadow-[var(--shadow-elev-1)]">
          <CardContent className="pt-6">
            <div className="flex flex-col md:flex-row gap-6">
              {/* Avatar */}
              <div className="flex-shrink-0">
                <div
                  className="w-32 h-32 rounded-full border-4 flex items-center justify-center"
                  style={{ borderColor: 'var(--aeth-gold)', backgroundColor: 'var(--aeth-stone-1)' }}
                  data-testid="character-avatar"
                >
                  <User size={64} style={{ color: 'var(--aeth-gold)' }} />
                </div>
              </div>

              {/* Character Info */}
              <div className="flex-1 space-y-4">
                <div>
                  <h1
                    className="text-3xl font-bold mb-1"
                    style={{ color: 'var(--aeth-gold)', fontFamily: "'Cinzel', serif" }}
                    data-testid="character-name"
                  >
                    {charData?.name || 'Unbekannter Abenteurer'}
                  </h1>
                  <p className="text-sm" style={{ color: 'var(--aeth-parchment-dim)' }}>
                    {charData?.title || 'Neuling'}
                  </p>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div>
                    <p className="text-xs mb-1" style={{ color: 'var(--aeth-parchment-dim)' }}>Level</p>
                    <div className="flex items-center gap-2">
                      <Crown size={18} style={{ color: 'var(--aeth-gold)' }} />
                      <span
                        className="text-xl font-bold font-mono-az"
                        style={{ color: 'var(--aeth-parchment)' }}
                        data-testid="character-level"
                      >
                        {charData?.level || 1}
                      </span>
                    </div>
                  </div>

                  <div>
                    <p className="text-xs mb-1" style={{ color: 'var(--aeth-parchment-dim)' }}>Pfad</p>
                    <Badge
                      variant="outline"
                      className="border-[color:var(--aeth-gold)] text-[color:var(--aeth-gold)]"
                      data-testid="character-path"
                    >
                      {charData?.title || 'Ungewählt'}
                    </Badge>
                  </div>

                  <div>
                    <p className="text-xs mb-1" style={{ color: 'var(--aeth-parchment-dim)' }}>Königreich</p>
                    <div className="flex items-center gap-2">
                      <MapPin size={16} style={{ color: 'var(--aeth-parchment)' }} />
                      <span className="text-sm" style={{ color: 'var(--aeth-parchment)' }} data-testid="character-location">
                        {charData?.location || 'Hauptstadt'}
                      </span>
                    </div>
                  </div>

                  <div>
                    <p className="text-xs mb-1" style={{ color: 'var(--aeth-parchment-dim)' }}>Tage im Reich</p>
                    <div className="flex items-center gap-2">
                      <Calendar size={16} style={{ color: 'var(--aeth-parchment)' }} />
                      <span
                        className="text-sm font-mono-az"
                        style={{ color: 'var(--aeth-parchment)' }}
                        data-testid="character-days"
                      >
                        {charData?.days_in_realm || 0}
                      </span>
                    </div>
                  </div>
                </div>

                {/* XP Bar */}
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <p className="text-xs" style={{ color: 'var(--aeth-parchment-dim)' }}>Erfahrung</p>
                    <p className="text-xs font-mono-az" style={{ color: 'var(--aeth-parchment)' }} data-testid="character-xp">
                      {xpProgress} / {xpRequired} XP
                    </p>
                  </div>
                  <Progress value={xpPercent} className="h-2" data-testid="character-xp-progress" />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
        {stats.map((stat, idx) => (
          <motion.div
            key={stat.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: idx * 0.05 }}
          >
            <Card className="border-[color:var(--game-border-subtle)] bg-[color:var(--aeth-stone-2)] shadow-[var(--shadow-elev-1)]">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-sm font-cinzel" style={{ color: 'var(--aeth-parchment)' }}>
                    {stat.label}
                  </CardTitle>
                  <stat.icon size={20} style={{ color: stat.color }} />
                </div>
              </CardHeader>
              <CardContent>
                <p
                  className="text-3xl font-bold font-mono-az"
                  style={{ color: 'var(--aeth-gold)' }}
                  data-testid={`character-stat-${stat.id}`}
                >
                  {stat.value}
                  {stat.total && stat.total !== stat.value && (
                    <span className="text-lg ml-2" style={{ color: 'var(--aeth-parchment-dim)' }}>
                      (+{stat.total - stat.value})
                    </span>
                  )}
                </p>
                {stat.total && stat.total !== stat.value && (
                  <p className="text-xs mt-1" style={{ color: 'var(--aeth-parchment-dim)' }}>
                    Gesamt: {stat.total}
                  </p>
                )}
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>

      {/* Equipment Section */}
      <Card className="border-[color:var(--game-border-subtle)] bg-[color:var(--aeth-stone-2)] shadow-[var(--shadow-elev-1)]">
        <CardHeader>
          <CardTitle className="font-cinzel" style={{ color: 'var(--aeth-parchment)' }}>
            Ausrüstung
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {['weapon', 'armor', 'helmet', 'shield'].map((slot) => (
              <div
                key={slot}
                className="border border-[color:var(--game-border-subtle)] rounded-lg p-4 text-center"
                style={{ backgroundColor: 'var(--aeth-stone-1)' }}
                data-testid={`equipment-slot-${slot}`}
              >
                <p className="text-xs mb-2" style={{ color: 'var(--aeth-parchment-dim)' }}>
                  {slot === 'weapon' && 'Waffe'}
                  {slot === 'armor' && 'Rüstung'}
                  {slot === 'helmet' && 'Helm'}
                  {slot === 'shield' && 'Schild'}
                </p>
                {charData?.equipment?.[slot] ? (
                  <p className="text-sm font-semibold" style={{ color: 'var(--aeth-parchment)' }}>
                    {charData.equipment[slot].name}
                  </p>
                ) : (
                  <p className="text-xs italic" style={{ color: 'var(--aeth-parchment-dim)' }}>
                    Leer
                  </p>
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Additional Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="border-[color:var(--game-border-subtle)] bg-[color:var(--aeth-stone-2)]">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-cinzel" style={{ color: 'var(--aeth-parchment)' }}>
              Kampfstatistik
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="flex justify-between">
              <span className="text-xs" style={{ color: 'var(--aeth-parchment-dim)' }}>Siege</span>
              <span className="text-sm font-mono-az" style={{ color: 'var(--aeth-parchment)' }}>
                {charData?.combat_wins || 0}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-xs" style={{ color: 'var(--aeth-parchment-dim)' }}>Niederlagen</span>
              <span className="text-sm font-mono-az" style={{ color: 'var(--aeth-parchment)' }}>
                {charData?.combat_losses || 0}
              </span>
            </div>
          </CardContent>
        </Card>

        <Card className="border-[color:var(--game-border-subtle)] bg-[color:var(--aeth-stone-2)]">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-cinzel" style={{ color: 'var(--aeth-parchment)' }}>
              Verbrechen
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="flex justify-between">
              <span className="text-xs" style={{ color: 'var(--aeth-parchment-dim)' }}>Erfolgreich</span>
              <span className="text-sm font-mono-az" style={{ color: 'var(--aeth-parchment)' }}>
                {charData?.crimes_success || 0}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-xs" style={{ color: 'var(--aeth-parchment-dim)' }}>Gescheitert</span>
              <span className="text-sm font-mono-az" style={{ color: 'var(--aeth-parchment)' }}>
                {charData?.crimes_failed || 0}
              </span>
            </div>
          </CardContent>
        </Card>

        <Card className="border-[color:var(--game-border-subtle)] bg-[color:var(--aeth-stone-2)]">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-cinzel" style={{ color: 'var(--aeth-parchment)' }}>
              Reichtum
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="flex justify-between">
              <span className="text-xs" style={{ color: 'var(--aeth-parchment-dim)' }}>Gold verdient</span>
              <span className="text-sm font-mono-az" style={{ color: 'var(--aeth-gold)' }}>
                {(charData?.gold_earned || 0).toLocaleString()}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-xs" style={{ color: 'var(--aeth-parchment-dim)' }}>Gold ausgegeben</span>
              <span className="text-sm font-mono-az" style={{ color: 'var(--aeth-parchment)' }}>
                {(charData?.gold_spent || 0).toLocaleString()}
              </span>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
