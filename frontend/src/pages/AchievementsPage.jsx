import { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import axios from 'axios';
import { motion } from 'framer-motion';
import { Trophy, Award, Crown, Target, Swords, Coins, Lock, CheckCircle2 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { toast } from 'sonner';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const ACHIEVEMENT_ICONS = {
  combat: Swords,
  wealth: Coins,
  training: Target,
  social: Trophy,
  exploration: Crown,
};

export default function AchievementsPage() {
  const { gameState } = useOutletContext();
  const [achievements, setAchievements] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchAchievements = async () => {
    try {
      const res = await axios.get(`${API}/game/achievements`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
      });
      setAchievements(res.data.achievements || []);
    } catch (err) {
      toast.error('Fehler beim Laden der Ehrungen');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAchievements();
  }, []);

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto">
        <div className="animate-pulse space-y-4">
          <div className="h-32 bg-[color:var(--aeth-stone-2)] rounded-[var(--radius-card)]"></div>
        </div>
      </div>
    );
  }

  const unlockedAchievements = achievements.filter((a) => a.unlocked);
  const lockedAchievements = achievements.filter((a) => !a.unlocked);
  const completionPercent = achievements.length > 0 ? (unlockedAchievements.length / achievements.length) * 100 : 0;

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="mb-8">
        <h1
          className="text-3xl font-bold mb-2"
          style={{ color: 'var(--aeth-parchment)', fontFamily: "'Cinzel', serif" }}
        >
          Königliche Ehrungen
        </h1>
        <p style={{ color: 'var(--aeth-parchment-dim)' }}>
          Schalte Errungenschaften frei und zeige deine Meisterschaft
        </p>
      </div>

      {/* Progress Overview */}
      <Card className="border-[color:var(--game-border-subtle)] bg-[color:var(--aeth-stone-2)] shadow-[var(--shadow-elev-1)]">
        <CardContent className="pt-6 space-y-4">
          <div className="flex justify-between items-center">
            <div>
              <p className="text-sm mb-1" style={{ color: 'var(--aeth-parchment-dim)' }}>Fortschritt</p>
              <p className="text-2xl font-bold font-cinzel" style={{ color: 'var(--aeth-gold)' }}>
                {unlockedAchievements.length} / {achievements.length}
              </p>
            </div>
            <Trophy size={48} style={{ color: 'var(--aeth-gold)' }} />
          </div>
          <Progress value={completionPercent} className="h-3" data-testid="achievements-progress" />
        </CardContent>
      </Card>

      {/* Achievements Tabs */}
      <Tabs defaultValue="unlocked" className="w-full">
        <TabsList
          className="grid w-full grid-cols-2 mb-6"
          style={{ backgroundColor: 'var(--aeth-stone-1)' }}
        >
          <TabsTrigger value="unlocked" data-testid="unlocked-tab">
            Freigeschaltet ({unlockedAchievements.length})
          </TabsTrigger>
          <TabsTrigger value="locked" data-testid="locked-tab">
            Gesperrt ({lockedAchievements.length})
          </TabsTrigger>
        </TabsList>

        {/* Unlocked */}
        <TabsContent value="unlocked">
          <ScrollArea className="h-[600px]">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {unlockedAchievements.length === 0 && (
                <Card className="border-[color:var(--game-border-subtle)] bg-[color:var(--aeth-stone-2)] col-span-2">
                  <CardContent className="py-12 text-center">
                    <Award size={48} className="mx-auto mb-4" style={{ color: 'var(--aeth-parchment-dim)' }} />
                    <p style={{ color: 'var(--aeth-parchment-dim)' }}>
                      Noch keine Ehrungen freigeschaltet. Spiele weiter!
                    </p>
                  </CardContent>
                </Card>
              )}

              {unlockedAchievements.map((achievement, idx) => {
                const Icon = ACHIEVEMENT_ICONS[achievement.category] || Award;
                return (
                  <motion.div
                    key={achievement.id}
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: idx * 0.05 }}
                  >
                    <Card
                      className="border-2 shadow-[var(--shadow-elev-1)]"
                      style={{ borderColor: 'var(--aeth-gold)', backgroundColor: 'var(--aeth-stone-2)' }}
                    >
                      <CardHeader>
                        <div className="flex items-start gap-3">
                          <div
                            className="p-3 rounded-lg"
                            style={{ backgroundColor: 'var(--aeth-gold)', color: 'var(--aeth-stone-0)' }}
                          >
                            <Icon size={24} />
                          </div>
                          <div className="flex-1">
                            <CardTitle className="text-base font-cinzel" style={{ color: 'var(--aeth-gold)' }}>
                              {achievement.name}
                            </CardTitle>
                            <CardDescription style={{ color: 'var(--aeth-parchment-dim)' }}>
                              {achievement.description}
                            </CardDescription>
                          </div>
                          <CheckCircle2 size={20} style={{ color: 'var(--aeth-gold)' }} />
                        </div>
                      </CardHeader>
                      <CardContent>
                        <div className="flex justify-between items-center">
                          <Badge variant="outline" style={{ borderColor: 'var(--aeth-gold)', color: 'var(--aeth-gold)' }}>
                            +{achievement.reward_xp} XP
                          </Badge>
                          {achievement.unlocked_at && (
                            <span className="text-xs font-mono-az" style={{ color: 'var(--aeth-parchment-dim)' }}>
                              {new Date(achievement.unlocked_at).toLocaleDateString('de-DE')}
                            </span>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  </motion.div>
                );
              })}
            </div>
          </ScrollArea>
        </TabsContent>

        {/* Locked */}
        <TabsContent value="locked">
          <ScrollArea className="h-[600px]">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {lockedAchievements.length === 0 && (
                <Card className="border-[color:var(--game-border-subtle)] bg-[color:var(--aeth-stone-2)] col-span-2">
                  <CardContent className="py-12 text-center">
                    <Trophy size={48} className="mx-auto mb-4" style={{ color: 'var(--aeth-gold)' }} />
                    <p className="text-xl font-bold font-cinzel mb-2" style={{ color: 'var(--aeth-gold)' }}>
                      Alle Ehrungen freigeschaltet!
                    </p>
                    <p style={{ color: 'var(--aeth-parchment-dim)' }}>
                      Du hast alle verfügbaren Ehrungen gemeistert!
                    </p>
                  </CardContent>
                </Card>
              )}

              {lockedAchievements.map((achievement, idx) => {
                const Icon = ACHIEVEMENT_ICONS[achievement.category] || Award;
                const progress = achievement.current_progress || 0;
                const required = achievement.required_progress || 1;
                const progressPercent = (progress / required) * 100;

                return (
                  <motion.div
                    key={achievement.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: idx * 0.05 }}
                  >
                    <Card className="border-[color:var(--game-border-subtle)] bg-[color:var(--aeth-stone-2)] opacity-75">
                      <CardHeader>
                        <div className="flex items-start gap-3">
                          <div
                            className="p-3 rounded-lg opacity-40"
                            style={{ backgroundColor: 'var(--aeth-iron)' }}
                          >
                            <Icon size={24} style={{ color: 'var(--aeth-parchment-dim)' }} />
                          </div>
                          <div className="flex-1">
                            <CardTitle className="text-base font-cinzel" style={{ color: 'var(--aeth-parchment)' }}>
                              {achievement.name}
                            </CardTitle>
                            <CardDescription style={{ color: 'var(--aeth-parchment-dim)' }}>
                              {achievement.description}
                            </CardDescription>
                          </div>
                          <Lock size={18} style={{ color: 'var(--aeth-parchment-dim)' }} />
                        </div>
                      </CardHeader>
                      <CardContent className="space-y-3">
                        {achievement.required_progress > 1 && (
                          <div>
                            <div className="flex justify-between text-xs mb-2">
                              <span style={{ color: 'var(--aeth-parchment-dim)' }}>Fortschritt</span>
                              <span className="font-mono-az" style={{ color: 'var(--aeth-parchment)' }}>
                                {progress} / {required}
                              </span>
                            </div>
                            <Progress value={progressPercent} className="h-2" />
                          </div>
                        )}
                        <Badge variant="outline" style={{ color: 'var(--aeth-parchment-dim)' }}>
                          Belohnung: +{achievement.reward_xp} XP
                        </Badge>
                      </CardContent>
                    </Card>
                  </motion.div>
                );
              })}
            </div>
          </ScrollArea>
        </TabsContent>
      </Tabs>
    </div>
  );
}
