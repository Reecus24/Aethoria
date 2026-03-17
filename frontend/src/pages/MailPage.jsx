import { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import axios from 'axios';
import { motion } from 'framer-motion';
import { Mail, MailOpen, Send, Plus, Trash2 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { toast } from 'sonner';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function MailPage() {
  const { gameState, refreshGameState } = useOutletContext();
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [composeOpen, setComposeOpen] = useState(false);
  const [recipient, setRecipient] = useState('');
  const [subject, setSubject] = useState('');
  const [body, setBody] = useState('');
  const [selectedMsg, setSelectedMsg] = useState(null);

  const fetchMessages = async () => {
    try {
      const res = await axios.get(`${API}/game/messages`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
      });
      setMessages(res.data.messages || []);
    } catch (err) {
      toast.error('Fehler beim Laden der Nachrichten');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMessages();
  }, []);

  const handleSendMessage = async () => {
    if (!recipient.trim() || !subject.trim() || !body.trim()) {
      toast.error('Alle Felder erforderlich');
      return;
    }

    try {
      const res = await axios.post(
        `${API}/game/messages/send`,
        { recipient_name: recipient, subject, body },
        { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } }
      );
      toast.success(res.data.message, { icon: '📨' });
      setComposeOpen(false);
      setRecipient('');
      setSubject('');
      setBody('');
      fetchMessages();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Fehler beim Senden');
    }
  };

  const handleMarkAsRead = async (msgId) => {
    try {
      await axios.post(
        `${API}/game/messages/${msgId}/read`,
        {},
        { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } }
      );
      fetchMessages();
      refreshGameState();
    } catch (err) {
      console.error('Error marking message as read:', err);
    }
  };

  const handleOpenMessage = (msg) => {
    setSelectedMsg(msg);
    if (!msg.read) {
      handleMarkAsRead(msg.id);
    }
  };

  const unreadCount = messages.filter((m) => !m.read).length;

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
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1
            className="text-3xl font-bold mb-2 flex items-center gap-3"
            style={{ color: 'var(--aeth-parchment)', fontFamily: "'Cinzel', serif" }}
          >
            Nachrichten
            {unreadCount > 0 && (
              <Badge className="bg-[color:var(--aeth-blood)] text-white" data-testid="unread-count-badge">
                {unreadCount}
              </Badge>
            )}
          </h1>
          <p style={{ color: 'var(--aeth-parchment-dim)' }}>
            Kommuniziere mit anderen Abenteurern
          </p>
        </div>
        <Dialog open={composeOpen} onOpenChange={setComposeOpen}>
          <DialogTrigger asChild>
            <Button className="btn-gold" data-testid="compose-message-button">
              <Plus size={18} className="mr-2" />
              Neue Nachricht
            </Button>
          </DialogTrigger>
          <DialogContent
            className="border-[color:var(--game-border-subtle)] max-w-2xl"
            style={{ backgroundColor: 'var(--aeth-stone-1)' }}
          >
            <DialogHeader>
              <DialogTitle className="font-cinzel" style={{ color: 'var(--aeth-parchment)' }}>
                Nachricht verfassen
              </DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <label className="text-sm mb-2 block" style={{ color: 'var(--aeth-parchment)' }}>
                  Empfänger
                </label>
                <Input
                  placeholder="Spielername"
                  value={recipient}
                  onChange={(e) => setRecipient(e.target.value)}
                  data-testid="message-recipient-input"
                />
              </div>
              <div>
                <label className="text-sm mb-2 block" style={{ color: 'var(--aeth-parchment)' }}>
                  Betreff
                </label>
                <Input
                  placeholder="Betreff"
                  value={subject}
                  onChange={(e) => setSubject(e.target.value)}
                  data-testid="message-subject-input"
                />
              </div>
              <div>
                <label className="text-sm mb-2 block" style={{ color: 'var(--aeth-parchment)' }}>
                  Nachricht
                </label>
                <Textarea
                  placeholder="Deine Nachricht..."
                  value={body}
                  onChange={(e) => setBody(e.target.value)}
                  rows={6}
                  data-testid="message-body-input"
                />
              </div>
              <Button onClick={handleSendMessage} className="btn-gold w-full" data-testid="send-message-button">
                <Send size={18} className="mr-2" />
                Senden
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Messages List */}
      <ScrollArea className="h-[600px]">
        <div className="space-y-3">
          {messages.length === 0 && (
            <Card className="border-[color:var(--game-border-subtle)] bg-[color:var(--aeth-stone-2)]">
              <CardContent className="py-12 text-center">
                <Mail size={48} className="mx-auto mb-4" style={{ color: 'var(--aeth-parchment-dim)' }} />
                <p style={{ color: 'var(--aeth-parchment-dim)' }}>
                  Keine Nachrichten. Schreibe die erste!
                </p>
              </CardContent>
            </Card>
          )}

          {messages.map((msg, idx) => (
            <motion.div
              key={msg.id}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: idx * 0.03 }}
            >
              <Card
                className={`border-[color:var(--game-border-subtle)] bg-[color:var(--aeth-stone-2)] cursor-pointer hover:border-[color:var(--aeth-gold)] transition-colors ${
                  !msg.read ? 'border-l-4 border-l-[color:var(--aeth-gold)]' : ''
                }`}
                onClick={() => handleOpenMessage(msg)}
                data-testid={`message-${msg.id}`}
              >
                <CardContent className="pt-6">
                  <div className="flex gap-4">
                    <div className="flex-shrink-0">
                      {msg.read ? (
                        <MailOpen size={24} style={{ color: 'var(--aeth-parchment-dim)' }} />
                      ) : (
                        <Mail size={24} style={{ color: 'var(--aeth-gold)' }} />
                      )}
                    </div>
                    <div className="flex-1">
                      <div className="flex justify-between items-start mb-2">
                        <p className="font-semibold" style={{ color: 'var(--aeth-parchment)' }}>
                          {msg.subject}
                        </p>
                        <span className="text-xs font-mono-az" style={{ color: 'var(--aeth-parchment-dim)' }}>
                          {new Date(msg.sent_at).toLocaleDateString('de-DE')}
                        </span>
                      </div>
                      <p className="text-sm mb-2" style={{ color: 'var(--aeth-parchment-dim)' }}>
                        Von: {msg.sender_name}
                      </p>
                      <p className="text-sm line-clamp-2" style={{ color: 'var(--aeth-parchment-dim)' }}>
                        {msg.body}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </ScrollArea>

      {/* Message Detail Dialog */}
      <Dialog open={selectedMsg !== null} onOpenChange={() => setSelectedMsg(null)}>
        <DialogContent
          className="border-[color:var(--game-border-subtle)] max-w-2xl"
          style={{ backgroundColor: 'var(--aeth-stone-1)' }}
        >
          {selectedMsg && (
            <>
              <DialogHeader>
                <DialogTitle className="font-cinzel" style={{ color: 'var(--aeth-parchment)' }}>
                  {selectedMsg.subject}
                </DialogTitle>
              </DialogHeader>
              <div className="space-y-4">
                <div className="flex justify-between text-sm">
                  <span style={{ color: 'var(--aeth-parchment-dim)' }}>Von: {selectedMsg.sender_name}</span>
                  <span className="font-mono-az" style={{ color: 'var(--aeth-parchment-dim)' }}>
                    {new Date(selectedMsg.sent_at).toLocaleString('de-DE')}
                  </span>
                </div>
                <Separator style={{ backgroundColor: 'var(--game-border-subtle)' }} />
                <ScrollArea className="h-[300px]">
                  <p className="text-sm leading-relaxed whitespace-pre-wrap" style={{ color: 'var(--aeth-parchment)' }}>
                    {selectedMsg.body}
                  </p>
                </ScrollArea>
              </div>
            </>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
