import { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import axios from '../utils/axios';
import { motion } from 'framer-motion';
import { Crosshair, Heart, Coins, Zap } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { toast } from 'sonner';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function HuntingPage() {
  const { gameState, refreshGameState } = useOutletContext();
  const [creatures, setCreatures] = useState([]);
  const [loading, setLoading] = useState(true);
  const [hunting, setHunting] = useState(false);

  const fetchCreatures = async () => {
    try {
      const res = await axios.get(`${API}/game/hunting/creatures`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
      });
      setCreatures(res.data.creatures || []);
    } catch (err) {
      toast.error('Fehler beim Laden der Kreaturen');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCreatures();
  }, []);

  const handleHunt = async (creatureId) => {
    const creature = creatures.find((c) => c.id === creatureId);
    if (!creature) return;

    if (gameState?.resources?.energy < creature.energy_cost) {
      toast.error(`Nicht genug Energie (benötigt: ${creature.energy_cost})`);
      return;
    }

    if (gameState.character.level < creature.min_level) {
      toast.error(`Level ${creature.min_level} erforderlich`);
      return;
    }

    setHunting(true);
    try {
      const res = await axios.post(
        `${API}/game/hunting/hunt`,
        { creature_id: creatureId },
        { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } }
      );
      
      if (res.data.success) {
        toast.success(`${res.data.message} • +${res.data.rewards.gold} Gold, +${res.data.rewards.xp} XP`, {
          icon: '🎯',
          duration: 5000,
        });
      } else {
        toast.error(res.data.message, { icon: '💀' });
      }
      refreshGameState();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Fehler bei der Jagd');
    } finally {
      setHunting(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto">
        <div className="animate-pulse space-y-4">
          <div className="h-32 bg-[color:var(--aeth-stone-2)] rounded-[var(--radius-card)]"></div>
        </div>
      </div>
    );
  }

  const canHunt = gameState?.character?.level >= 15;

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="mb-8">
        <h1
          className="text-3xl font-bold mb-2"
          style={{ color: 'var(--aeth-parchment)', fontFamily: "'Cinzel', serif" }}
        >
          Jagdgründe
        </h1>
        <p style={{ color: 'var(--aeth-parchment-dim)' }}>
          Jage wilde Kreaturen für Gold und Erfahrung • Freigeschaltet ab Level 15
        </p>
      </div>

      {!canHunt && (
        <Card className="border-[color:var(--aeth-blood)] bg-[color:var(--aeth-stone-2)]">
          <CardContent className="pt-6 text-center">
            <Crosshair size={48} className="mx-auto mb-4" style={{ color: 'var(--aeth-blood)' }} />
            <p className="font-semibold mb-2" style={{ color: 'var(--aeth-parchment)' }}>
              Jagdgründe gesperrt
            </p>
            <p className="text-sm" style={{ color: 'var(--aeth-parchment-dim)' }}>
              Du musst Level 15 erreichen, um jagen zu können. (Aktuell: Level {gameState?.character?.level || 1})
            </p>
          </CardContent>
        </Card>
      )}

      {canHunt && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {creatures.map((creature, idx) => (
            <motion.div
              key={creature.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.05 }}
            >
              <Card className="border-[color:var(--game-border-subtle)] bg-[color:var(--aeth-stone-2)] hover:border-[color:var(--aeth-gold)] transition-colors">
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <div>
                      <CardTitle className="font-cinzel" style={{ color: 'var(--aeth-parchment)' }}>
                        {creature.name}
                      </CardTitle>
                      <CardDescription style={{ color: 'var(--aeth-parchment-dim)' }}>
                        {creature.description}
                      </CardDescription>
                    </div>
                    <Badge
                      variant="outline"
                      style={{
                        borderColor: creature.difficulty === 'easy' ? '#81C784' : creature.difficulty === 'medium' ? '#FFB74D' : '#E57373',
                        color: creature.difficulty === 'easy' ? '#81C784' : creature.difficulty === 'medium' ? '#FFB74D' : '#E57373',
                      }}
                    >
                      {creature.difficulty === 'easy' ? 'Leicht' : creature.difficulty === 'medium' ? 'Mittel' : 'Schwer'}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* Stats */}
                  <div className="grid grid-cols-2 gap-3 text-sm">
                    <div className="flex items-center gap-2">
                      <Heart size={16} style={{ color: '#E57373' }} />
                      <span style={{ color: 'var(--aeth-parchment-dim)' }}>Leben:</span>
                      <span className="font-mono-az" style={{ color: 'var(--aeth-parchment)' }}>
                        {creature.hp}
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Zap size={16} style={{ color: '#FFB74D' }} />
                      <span style={{ color: 'var(--aeth-parchment-dim)' }}>Energie:</span>
                      <span className="font-mono-az" style={{ color: 'var(--aeth-parchment)' }}>
                        {creature.energy_cost}
                      </span>
                    </div>
                  </div>

                  {/* Rewards */}
                  <div className="space-y-2">
                    <p className="text-xs font-semibold" style={{ color: 'var(--aeth-parchment)' }}>Belohnungen:</p>
                    <div className="flex gap-4 text-sm">
                      <span style={{ color: 'var(--aeth-gold)' }}>
                        <Coins size={14} className="inline mr-1" />
                        {creature.gold_reward} Gold
                      </span>
                      <span style={{ color: 'var(--aeth-parchment)' }}>
                        +{creature.xp_reward} XP
                      </span>
                    </div>
                  </div>

                  <Button
                    onClick={() => handleHunt(creature.id)}
                    disabled={
                      hunting ||
                      (gameState?.resources?.energy || 0) < creature.energy_cost ||
                      (gameState?.character?.level || 0) < creature.min_level
                    }
                    className="btn-gold w-full"
                    data-testid={`hunt-${creature.id}-button`}
                  >
                    <Crosshair size={18} className="mr-2" />
                    Jagen
                  </Button>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      )}

      {canHunt && creatures.length === 0 && (
        <Card className="border-[color:var(--game-border-subtle)] bg-[color:var(--aeth-stone-2)]">
          <CardContent className="py-12 text-center">
            <Crosshair size={48} className="mx-auto mb-4" style={{ color: 'var(--aeth-parchment-dim)' }} />
            <p style={{ color: 'var(--aeth-parchment-dim)' }}>
              Keine Kreaturen in dieser Region. Reise zu einem anderen Königreich!
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
