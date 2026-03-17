import { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import axios from '../utils/axios';
import { motion } from 'framer-motion';
import { Heart, Clock, Coins, AlertCircle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function HospitalPage() {
  const { gameState, refreshGameState } = useOutletContext();
  const [hospitalData, setHospitalData] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchHospital = async () => {
    try {
      const res = await axios.get(`${API}/game/hospital`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
      });
      setHospitalData(res.data);
    } catch (err) {
      toast.error('Fehler beim Laden');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHospital();
  }, []);

  const hospitalTimer = gameState?.timers?.hospital;
  const currentHP = gameState?.resources?.hp || 100;
  const maxHP = gameState?.resources?.max_hp || 100;
  const hpPercent = (currentHP / maxHP) * 100;

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="animate-pulse space-y-4">
          <div className="h-32 bg-[color:var(--aeth-stone-2)] rounded-[var(--radius-card)]"></div>
        </div>
      </div>
    );
  }

  const isInjured = currentHP < maxHP;
  const isInHospital = hospitalTimer?.in_hospital === true;
  
  // Calculate estimated healing for injured users
  const hpMissing = maxHP - currentHP;
  const estimatedHealingSeconds = hpMissing * 360;
  const estimatedHealingMinutes = Math.floor(estimatedHealingSeconds / 60);
  const estimatedHealingHours = Math.floor(estimatedHealingMinutes / 60);

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="mb-8">
        <h1
          className="text-3xl font-bold mb-2"
          style={{ color: 'var(--aeth-parchment)', fontFamily: "'Cinzel', serif" }}
        >
          Heilerin des Reiches
        </h1>
        <p style={{ color: 'var(--aeth-parchment-dim)' }}>
          Erhole dich von Verletzungen • Heilung dauert je nach Schwere der Verletzung
        </p>
      </div>

      {/* Current HP Status */}
      <Card
        className={`border-2 shadow-[var(--shadow-elev-1)] ${
          isInjured ? 'border-[color:var(--aeth-blood)]' : 'border-[color:var(--aeth-gold)]'
        }`}
        style={{ backgroundColor: 'var(--aeth-stone-2)' }}
      >
        <CardContent className="pt-6 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Heart
                size={32}
                style={{ color: isInjured ? 'var(--aeth-blood)' : 'var(--aeth-gold)' }}
                fill={isInjured ? 'var(--aeth-blood)' : 'none'}
              />
              <div>
                <p className="text-xs mb-1" style={{ color: 'var(--aeth-parchment-dim)' }}>Gesundheit</p>
                <p className="text-2xl font-bold font-mono-az" style={{ color: 'var(--aeth-parchment)' }} data-testid="current-hp">
                  {currentHP} / {maxHP} HP
                </p>
              </div>
            </div>
            <Badge variant={isInjured ? 'destructive' : 'outline'} className="text-sm px-3 py-1">
              {isInjured ? 'Verletzt' : 'Gesund'}
            </Badge>
          </div>
          <Progress value={hpPercent} className="h-3" data-testid="hp-progress" />
        </CardContent>
      </Card>

      {/* Hospital Timer */}
      {isInHospital && (
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
          <Card className="border-[color:var(--aeth-gold)] bg-[color:var(--aeth-stone-2)]">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm mb-1" style={{ color: 'var(--aeth-parchment-dim)' }}>
                    Du wirst behandelt...
                  </p>
                  <p className="text-xl font-bold font-cinzel" style={{ color: 'var(--aeth-gold)' }}>
                    Heilung läuft
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-sm mb-1" style={{ color: 'var(--aeth-parchment-dim)' }}>Verbleibend:</p>
                  <p className="text-xl font-bold font-mono-az" style={{ color: 'var(--aeth-gold)' }} data-testid="hospital-timer">
                    {Math.floor((hospitalTimer?.seconds_remaining || 0) / 60)}:{String((hospitalTimer?.seconds_remaining || 0) % 60).padStart(2, '0')}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Info Card - for injured users not in hospital */}
      {!isInHospital && isInjured && (
        <Card className="border-[color:var(--game-border-subtle)] bg-[color:var(--aeth-stone-2)]">
          <CardContent className="pt-6">
            <div className="flex items-start gap-3">
              <AlertCircle size={24} style={{ color: 'var(--aeth-gold)' }} />
              <div className="text-sm space-y-3" style={{ color: 'var(--aeth-parchment-dim)' }}>
                <p className="font-semibold mb-2" style={{ color: 'var(--aeth-parchment)' }}>
                  Natürliche Heilung
                </p>
                
                <div className="bg-black/20 p-3 rounded-lg">
                  <p className="text-xs mb-1">Geschätzte Zeit bis Vollheilung:</p>
                  <p className="text-lg font-bold font-mono-az" style={{ color: 'var(--aeth-gold)' }} data-testid="natural-healing-timer">
                    {estimatedHealingHours}h {estimatedHealingMinutes % 60}m
                  </p>
                  <p className="text-xs mt-1" style={{ color: 'var(--aeth-parchment-dim)' }}>
                    ({hpMissing} HP fehlen × 6 Min/HP)
                  </p>
                </div>
                
                <ul className="list-disc list-inside space-y-1">
                  <li>Leben regeneriert sich automatisch (1 HP alle 6 Minuten)</li>
                  <li>Du kannst weiterspielen und Abenteuer erleben</li>
                  <li>Bei schweren Verletzungen kommst du automatisch hierher</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {!isInjured && !isInHospital && (
        <Card className="border-[color:var(--game-border-subtle)] bg-[color:var(--aeth-stone-2)]">
          <CardContent className="py-12 text-center">
            <Heart size={64} className="mx-auto mb-4" style={{ color: 'var(--aeth-gold)' }} />
            <p className="text-xl font-bold font-cinzel mb-2" style={{ color: 'var(--aeth-parchment)' }}>
              Du bist gesund!
            </p>
            <p style={{ color: 'var(--aeth-parchment-dim)' }}>
              Keine Behandlung erforderlich. Kehre zum Abenteuer zurück!
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
