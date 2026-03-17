import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Bot, Play, Copy, AlertCircle, CheckCircle2, AlertTriangle } from 'lucide-react';
import { toast } from 'sonner';
import axios from '../utils/axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function BotTestingPage() {
  const [testing, setTesting] = useState(false);
  const [report, setReport] = useState(null);
  const [copyText, setCopyText] = useState('');

  const runBotTests = async () => {
    setTesting(true);
    setReport(null);
    toast.info('Starte Bot-Tests... Dies dauert ~30 Sekunden', { duration: 3000 });

    try {
      const response = await axios.post(`${API}/admin/run-bot-tests`, {}, { timeout: 60000 });
      setReport(response.data);
      
      const bugsCount = response.data.bugs_found || 0;
      if (bugsCount === 0) {
        toast.success('🎉 Keine Bugs gefunden!');
      } else {
        toast.warning(`🐛 ${bugsCount} Bugs gefunden`, { duration: 5000 });
      }
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Bot-Tests fehlgeschlagen');
    } finally {
      setTesting(false);
    }
  };

  const copyBugReport = () => {
    if (!report) return;

    let text = `AETHORIA BOT TEST REPORT\n`;
    text += `Datum: ${new Date(report.test_date).toLocaleString('de-DE')}\n`;
    text += `Bugs gefunden: ${report.bugs_found}\n\n`;

    ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].forEach(severity => {
      const bugs = report.bugs_by_severity[severity] || [];
      if (bugs.length > 0) {
        text += `\n${severity} PRIORITY (${bugs.length}):\n`;
        text += `${'='.repeat(50)}\n`;
        bugs.forEach((bug, i) => {
          text += `\n${i + 1}. [${bug.category}] ${bug.description}\n`;
          text += `   Bot: ${bug.bot} | Level: ${bug.level_when_found}\n`;
          text += `   Evidence: ${JSON.stringify(bug.evidence, null, 2)}\n`;
        });
      }
    });

    text += `\n\nBOT SUMMARIES:\n`;
    text += `${'='.repeat(50)}\n`;
    report.bot_summaries.forEach(bot => {
      text += `${bot.bot} (${bot.path}): ${bot.actions} actions, ${bot.bugs} bugs found\n`;
    });

    navigator.clipboard.writeText(text);
    toast.success('Bug-Report in Zwischenablage kopiert!');
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'CRITICAL': return '#F44336';
      case 'HIGH': return '#FF9800';
      case 'MEDIUM': return '#FFB74D';
      case 'LOW': return '#81C784';
      default: return 'var(--aeth-parchment-dim)';
    }
  };

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'CRITICAL':
      case 'HIGH':
        return AlertCircle;
      case 'MEDIUM':
        return AlertTriangle;
      case 'LOW':
        return CheckCircle2;
      default:
        return AlertCircle;
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="mb-8">
        <h1
          className="text-3xl font-bold mb-2"
          style={{ color: 'var(--aeth-parchment)', fontFamily: "'Cinzel', serif" }}
        >
          Automatische Bot-Tests
        </h1>
        <p style={{ color: 'var(--aeth-parchment-dim)' }}>
          3 Bots (Knight, Shadow, Noble) spielen das Spiel durch und suchen nach Bugs
        </p>
      </div>

      {/* Control Panel */}
      <Card className="border-[color:var(--game-border-subtle)] bg-[color:var(--aeth-stone-2)]">
        <CardContent className="pt-6">
          <div className="flex items-center gap-4">
            <Button
              onClick={runBotTests}
              disabled={testing}
              className="btn-gold"
              data-testid="start-bot-tests"
            >
              <Play size={16} className="mr-2" />
              {testing ? 'Bots laufen...' : 'Bot-Tests starten'}
            </Button>
            
            {report && (
              <Button
                onClick={copyBugReport}
                variant="outline"
                className="border-[color:var(--aeth-gold)] text-[color:var(--aeth-gold)]"
                data-testid="copy-bug-report"
              >
                <Copy size={16} className="mr-2" />
                Bug-Report kopieren
              </Button>
            )}
          </div>
          
          {testing && (
            <div className="mt-4 flex items-center gap-2" style={{ color: 'var(--aeth-gold)' }}>
              <Bot className="animate-pulse" size={20} />
              <span className="text-sm">Bots spielen das Spiel durch... (~30 Sekunden)</span>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Results */}
      {report && (
        <>
          {/* Summary */}
          <Card className="border-[color:var(--aeth-gold)] bg-[color:var(--aeth-stone-2)]">
            <CardHeader>
              <CardTitle className="font-cinzel" style={{ color: 'var(--aeth-gold)' }}>
                Test-Zusammenfassung
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                <div>
                  <p className="text-sm mb-1" style={{ color: 'var(--aeth-parchment-dim)' }}>Bots</p>
                  <p className="text-2xl font-bold" style={{ color: 'var(--aeth-gold)' }}>{report.bots_run}</p>
                </div>
                <div>
                  <p className="text-sm mb-1" style={{ color: 'var(--aeth-parchment-dim)' }}>Aktionen</p>
                  <p className="text-2xl font-bold" style={{ color: 'var(--aeth-parchment)' }}>{report.total_actions}</p>
                </div>
                <div>
                  <p className="text-sm mb-1" style={{ color: 'var(--aeth-parchment-dim)' }}>Bugs gefunden</p>
                  <p className="text-2xl font-bold" style={{ 
                    color: report.bugs_found === 0 ? '#81C784' : report.bugs_found < 5 ? '#FFB74D' : '#F44336' 
                  }}>
                    {report.bugs_found}
                  </p>
                </div>
                <div>
                  <p className="text-sm mb-1" style={{ color: 'var(--aeth-parchment-dim)' }}>Status</p>
                  <p className="text-lg font-bold" style={{ color: report.bugs_found === 0 ? '#81C784' : '#FFB74D' }}>
                    {report.bugs_found === 0 ? '✅ Perfekt' : '⚠️ Bugs'}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Bot Summaries */}
          <div className="grid md:grid-cols-3 gap-4">
            {report.bot_summaries.map(bot => (
              <Card key={bot.bot} className="border-[color:var(--game-border-subtle)] bg-[color:var(--aeth-stone-2)]">
                <CardHeader>
                  <CardTitle className="text-base font-cinzel flex items-center gap-2">
                    <Bot size={20} style={{ color: 'var(--aeth-gold)' }} />
                    <span style={{ color: 'var(--aeth-parchment)' }}>{bot.bot}</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span style={{ color: 'var(--aeth-parchment-dim)' }}>Klasse:</span>
                      <span style={{ color: 'var(--aeth-gold)' }}>{bot.path}</span>
                    </div>
                    <div className="flex justify-between">
                      <span style={{ color: 'var(--aeth-parchment-dim)' }}>Aktionen:</span>
                      <span style={{ color: 'var(--aeth-parchment)' }}>{bot.actions}</span>
                    </div>
                    <div className="flex justify-between">
                      <span style={{ color: 'var(--aeth-parchment-dim)' }}>Bugs:</span>
                      <Badge variant={bot.bugs === 0 ? 'default' : 'destructive'}>
                        {bot.bugs}
                      </Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Bugs List */}
          {report.bugs_found > 0 && (
            <div className="space-y-4">
              <h2 className="text-2xl font-bold font-cinzel" style={{ color: 'var(--aeth-gold)' }}>
                Gefundene Bugs
              </h2>

              {['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map(severity => {
                const bugs = report.bugs_by_severity[severity] || [];
                if (bugs.length === 0) return null;

                return (
                  <div key={severity}>
                    <h3 className="text-lg font-semibold mb-3 flex items-center gap-2" style={{ color: getSeverityColor(severity) }}>
                      {React.createElement(getSeverityIcon(severity), { size: 20 })}
                      {severity} Priority ({bugs.length})
                    </h3>
                    
                    <div className="space-y-3">
                      {bugs.map((bug, i) => (
                        <Card key={i} className="border-l-4 bg-[color:var(--aeth-stone-2)]" style={{ borderLeftColor: getSeverityColor(severity) }}>
                          <CardContent className="pt-4">
                            <div className="flex items-start gap-3">
                              <div className="flex-1">
                                <div className="flex items-center gap-2 mb-2">
                                  <Badge variant="outline" style={{ borderColor: 'var(--aeth-gold)', color: 'var(--aeth-gold)' }}>
                                    {bug.category}
                                  </Badge>
                                  <Badge variant="outline" className="text-xs">
                                    {bug.bot}
                                  </Badge>
                                  <Badge variant="outline" className="text-xs">
                                    Level {bug.level_when_found}
                                  </Badge>
                                </div>
                                
                                <p className="text-sm mb-2" style={{ color: 'var(--aeth-parchment)' }}>
                                  {bug.description}
                                </p>
                                
                                {bug.evidence && Object.keys(bug.evidence).length > 0 && (
                                  <details className="text-xs mt-2">
                                    <summary className="cursor-pointer" style={{ color: 'var(--aeth-parchment-dim)' }}>
                                      Evidence anzeigen
                                    </summary>
                                    <pre className="mt-2 p-2 rounded bg-black/20 overflow-x-auto" style={{ color: 'var(--aeth-parchment-dim)' }}>
                                      {JSON.stringify(bug.evidence, null, 2)}
                                    </pre>
                                  </details>
                                )}
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {/* No Bugs Found */}
          {report.bugs_found === 0 && (
            <Card className="border-[color:var(--aeth-gold)] bg-[color:var(--aeth-stone-2)]">
              <CardContent className="py-12 text-center">
                <CheckCircle2 size={64} className="mx-auto mb-4" style={{ color: '#81C784' }} />
                <p className="text-xl font-bold font-cinzel mb-2" style={{ color: 'var(--aeth-parchment)' }}>
                  Keine Bugs gefunden!
                </p>
                <p style={{ color: 'var(--aeth-parchment-dim)' }}>
                  Alle Bot-Tests wurden erfolgreich durchgeführt.
                </p>
              </CardContent>
            </Card>
          )}
        </>
      )}
    </div>
  );
}
