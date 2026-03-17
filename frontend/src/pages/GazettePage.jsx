import { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import axios from 'axios';
import { motion } from 'framer-motion';
import { Newspaper, Trophy, Crown, Scroll, TrendingUp } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { toast } from 'sonner';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function GazettePage() {
  const { gameState } = useOutletContext();
  const [news, setNews] = useState([]);
  const [leaderboard, setLeaderboard] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await axios.get(`${API}/landing`);
        setNews(res.data.news || []);
        setLeaderboard(res.data.leaderboard || []);
      } catch (err) {
        toast.error('Fehler beim Laden der Gazette');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
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

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="mb-8">
        <h1
          className="text-3xl font-bold mb-2"
          style={{ color: 'var(--aeth-parchment)', fontFamily: "'Cinzel', serif" }}
        >
          Königliche Gazette
        </h1>
        <p style={{ color: 'var(--aeth-parchment-dim)' }}>
          Neuigkeiten aus dem Reich & Heldenhalle
        </p>
      </div>

      <Tabs defaultValue="news" className="w-full">
        <TabsList
          className="grid w-full grid-cols-2 mb-6"
          style={{ backgroundColor: 'var(--aeth-stone-1)' }}
        >
          <TabsTrigger value="news" data-testid="news-tab">
            <Newspaper size={18} className="mr-2" />
            Neuigkeiten
          </TabsTrigger>
          <TabsTrigger value="leaderboard" data-testid="leaderboard-tab">
            <Trophy size={18} className="mr-2" />
            Heldenhalle
          </TabsTrigger>
        </TabsList>

        {/* News Tab */}
        <TabsContent value="news">
          <ScrollArea className="h-[700px]">
            <div className="space-y-4">
              {news.length === 0 && (
                <Card className="border-[color:var(--game-border-subtle)] bg-[color:var(--aeth-stone-2)]">
                  <CardContent className="py-12 text-center">
                    <Scroll size={48} className="mx-auto mb-4" style={{ color: 'var(--aeth-parchment-dim)' }} />
                    <p style={{ color: 'var(--aeth-parchment-dim)' }}>
                      Keine Neuigkeiten verfügbar
                    </p>
                  </CardContent>
                </Card>
              )}

              {news.map((item, idx) => (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.05 }}
                >
                  <Card className="border-[color:var(--game-border-subtle)] bg-[color:var(--aeth-stone-2)] hover:border-[color:var(--aeth-gold)] transition-colors">
                    <CardHeader>
                      <div className="flex justify-between items-start gap-4">
                        <CardTitle className="text-lg font-cinzel" style={{ color: 'var(--aeth-parchment)' }}>
                          {item.title}
                        </CardTitle>
                        <Badge variant="outline" className="flex-shrink-0">
                          {item.category === 'patch' ? 'Patch' : item.category === 'event' ? 'Event' : 'News'}
                        </Badge>
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <p className="text-sm leading-relaxed" style={{ color: 'var(--aeth-parchment-dim)' }}>
                        {item.content}
                      </p>
                      <Separator style={{ backgroundColor: 'var(--game-border-subtle)' }} />
                      <div className="flex justify-between items-center text-xs">
                        <span style={{ color: 'var(--aeth-parchment-dim)' }}>
                          {item.version && `Version ${item.version}`}
                        </span>
                        <span className="font-mono-az" style={{ color: 'var(--aeth-parchment-dim)' }}>
                          {new Date(item.date).toLocaleDateString('de-DE')}
                        </span>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </div>
          </ScrollArea>
        </TabsContent>

        {/* Leaderboard Tab */}
        <TabsContent value="leaderboard">
          <ScrollArea className="h-[700px]">
            <div className="space-y-3">
              {leaderboard.length === 0 && (
                <Card className="border-[color:var(--game-border-subtle)] bg-[color:var(--aeth-stone-2)]">
                  <CardContent className="py-12 text-center">
                    <Trophy size={48} className="mx-auto mb-4" style={{ color: 'var(--aeth-parchment-dim)' }} />
                    <p style={{ color: 'var(--aeth-parchment-dim)' }}>
                      Keine Helden in der Halle. Sei der erste!
                    </p>
                  </CardContent>
                </Card>
              )}

              {leaderboard.map((player, idx) => {
                const rankColors = {
                  0: 'var(--aeth-gold)',
                  1: '#C0C0C0',
                  2: '#CD7F32',
                };
                const rankColor = rankColors[idx] || 'var(--aeth-parchment)';

                return (
                  <motion.div
                    key={player.name}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: idx * 0.04 }}
                  >
                    <Card
                      className={`border-[color:var(--game-border-subtle)] bg-[color:var(--aeth-stone-2)] ${
                        idx < 3 ? 'border-l-4' : ''
                      }`}
                      style={idx < 3 ? { borderLeftColor: rankColor } : {}}
                      data-testid={`leaderboard-rank-${idx + 1}`}
                    >
                      <CardContent className="pt-6">
                        <div className="flex items-center gap-4">
                          {/* Rank */}
                          <div
                            className="w-12 h-12 rounded-full flex items-center justify-center flex-shrink-0"
                            style={{
                              backgroundColor: 'var(--aeth-stone-1)',
                              border: `2px solid ${rankColor}`,
                            }}
                          >
                            <span className="text-xl font-bold font-mono-az" style={{ color: rankColor }}>
                              {idx + 1}
                            </span>
                          </div>

                          {/* Player Info */}
                          <div className="flex-1">
                            <p className="font-bold font-cinzel text-lg mb-1" style={{ color: 'var(--aeth-parchment)' }}>
                              {player.name}
                            </p>
                            <p className="text-sm" style={{ color: 'var(--aeth-parchment-dim)' }}>
                              {player.title || 'Abenteurer'}
                            </p>
                          </div>

                          {/* Stats */}
                          <div className="flex gap-6 text-right">
                            <div>
                              <p className="text-xs mb-1" style={{ color: 'var(--aeth-parchment-dim)' }}>Level</p>
                              <Badge variant="outline">{player.level}</Badge>
                            </div>
                            <div>
                              <p className="text-xs mb-1" style={{ color: 'var(--aeth-parchment-dim)' }}>Total XP</p>
                              <p className="text-lg font-bold font-mono-az" style={{ color: 'var(--aeth-gold)' }}>
                                {player.xp.toLocaleString()}
                              </p>
                            </div>
                          </div>
                        </div>
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
