import { useState } from 'react';
import { useOutletContext } from 'react-router-dom';
import axios from '../utils/axios';
import { motion } from 'framer-motion';
import { Dice1, Dice2, Dice3, Dice4, Dice5, Dice6, Coins } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { toast } from 'sonner';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const DICE_ICONS = [Dice1, Dice2, Dice3, Dice4, Dice5, Dice6];

export default function TavernPage() {
  const { gameState, refreshGameState } = useOutletContext();
  const [wager, setWager] = useState(100);
  const [rolling, setRolling] = useState(false);
  const [result, setResult] = useState(null);

  const rollDice = async () => {
    if (wager < 10) {
      toast.error('Mindesteinsatz: 10 Gold');
      return;
    }
    if (wager > (gameState?.resources?.gold || 0)) {
      toast.error('Nicht genug Gold');
      return;
    }

    setRolling(true);
    setResult(null);

    try {
      const res = await axios.post(
        `${API}/game/tavern/dice`,
        { wager },
        { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } }
      );
      
      // Animation delay
      setTimeout(() => {
        setResult(res.data);
        if (res.data.won) {
          toast.success(`Gewonnen! +${res.data.winnings} Gold`, { icon: '🎉', duration: 4000 });
        } else {
          toast.error(`Verloren! -${wager} Gold`, { icon: '💀' });
        }
        refreshGameState();
      }, 1500);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Fehler beim Würfeln');
      setRolling(false);
    } finally {
      setTimeout(() => setRolling(false), 1500);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1
          className="text-3xl font-bold mb-2"
          style={{ color: 'var(--aeth-parchment)', fontFamily: "'Cinzel', serif" }}
        >
          Die Taverne
        </h1>
        <p style={{ color: 'var(--aeth-parchment-dim)' }}>
          Wage dein Glück beim Würfelspiel • Mindesteinsatz: 10 Gold
        </p>
      </div>

      {/* Dice Game */}
      <Card className="border-[color:var(--game-border-subtle)] bg-[color:var(--aeth-stone-2)] shadow-[var(--shadow-elev-2)]">
        <CardHeader>
          <CardTitle className="font-cinzel" style={{ color: 'var(--aeth-gold)' }}>
            Würfelspiel
          </CardTitle>
          <CardDescription style={{ color: 'var(--aeth-parchment-dim)' }}>
            Würfle sechs Würfel (6d6). Summe ≥21 = Gewinn (2x Einsatz), &lt;21 = Verlust
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Wager Input */}
          <div>
            <label className="text-sm mb-2 block" style={{ color: 'var(--aeth-parchment)' }}>
              Einsatz (Gold)
            </label>
            <div className="flex gap-3">
              <Input
                type="number"
                value={wager}
                onChange={(e) => setWager(Math.max(10, parseInt(e.target.value) || 10))}
                min={10}
                max={gameState?.resources?.gold || 100}
                className="flex-1"
                data-testid="tavern-wager-input"
              />
              <Button
                onClick={() => setWager(Math.min(100, gameState?.resources?.gold || 0))}
                variant="outline"
                size="sm"
                data-testid="wager-preset-100"
              >
                100
              </Button>
              <Button
                onClick={() => setWager(Math.min(500, gameState?.resources?.gold || 0))}
                variant="outline"
                size="sm"
                data-testid="wager-preset-500"
              >
                500
              </Button>
            </div>
          </div>

          <Separator style={{ backgroundColor: 'var(--game-border-subtle)' }} />

          {/* Dice Display */}
          <div className="py-8">
            {result && !rolling && (
              <motion.div
                initial={{ scale: 0.5, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                className="flex justify-center flex-wrap gap-4 mb-6"
              >
                {(result.rolls || []).map((die, idx) => {
                  const DiceIcon = DICE_ICONS[die - 1] || Dice1;
                  return (
                    <motion.div
                      key={idx}
                      initial={{ rotate: 0 }}
                      animate={{ rotate: 360 }}
                      transition={{ duration: 0.6, delay: idx * 0.1 }}
                    >
                      <DiceIcon size={60} style={{ color: 'var(--aeth-gold)' }} data-testid={`dice-result-${idx + 1}`} />
                    </motion.div>
                  );
                })}
              </motion.div>
            )}

            {result && !rolling && (
              <div className="text-center space-y-2">
                <p className="text-5xl font-bold font-mono-az" style={{ color: 'var(--aeth-gold)' }} data-testid="dice-sum">
                  {result.total}
                </p>
                <Badge
                  variant={result.won ? 'default' : 'destructive'}
                  className="text-lg px-4 py-1"
                  data-testid="dice-result-badge"
                >
                  {result.won ? `Gewonnen: ${result.winnings} Gold` : `Verloren: ${wager} Gold`}
                </Badge>
              </div>
            )}

            {rolling && (
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                className="flex justify-center"
              >
                <Dice3 size={80} style={{ color: 'var(--aeth-gold)' }} />
              </motion.div>
            )}

            {!result && !rolling && (
              <div className="text-center" style={{ color: 'var(--aeth-parchment-dim)' }}>
                <Dice3 size={80} className="mx-auto mb-4 opacity-30" />
                <p>Platziere deinen Einsatz und würfle</p>
              </div>
            )}
          </div>

          <Button
            onClick={rollDice}
            disabled={rolling || wager < 10}
            className="btn-gold w-full py-6 text-lg"
            data-testid="roll-dice-button"
          >
            {rolling ? 'Würfeln...' : `Würfeln (${wager} Gold)`}
          </Button>
        </CardContent>
      </Card>

      {/* Info Box */}
      <Card className="border-[color:var(--game-border-subtle)] bg-[color:var(--aeth-stone-1)]">
        <CardContent className="pt-6">
          <div className="flex items-start gap-3">
            <Coins size={20} style={{ color: 'var(--aeth-gold)' }} className="mt-1" />
            <div className="text-sm" style={{ color: 'var(--aeth-parchment-dim)' }}>
              <p className="font-semibold mb-1" style={{ color: 'var(--aeth-parchment)' }}>
                Spielregeln:
              </p>
              <ul className="list-disc list-inside space-y-1">
                <li>Würfle sechs Würfel (6d6)</li>
                <li>Summe ≥21: Du gewinnst das Doppelte deines Einsatzes</li>
                <li>Summe &lt;21: Du verlierst deinen Einsatz</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
