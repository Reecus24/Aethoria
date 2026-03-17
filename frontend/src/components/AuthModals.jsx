import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from './ui/dialog';
import { Label } from './ui/label';
import { Input } from './ui/input';
import { Separator } from './ui/separator';
import { Eye, EyeOff, Loader2, Shield, Sword, Crown, ChevronRight, ChevronLeft, Check } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// ─── PATH CARDS for step 2 ────────────────────────
const PATHS = [
  {
    key: 'knight',
    icon: '⚔️',
    label: 'The Knight',
    subtitle: 'Master of Combat',
    desc: 'Dominate through strength. Train at the Barracks, win tournaments, become the most feared warrior.',
    color: '#C0392B',
    stats: { Strength: 15, Dexterity: 10, Speed: 10, Defense: 15, Gold: 100 },
  },
  {
    key: 'shadow',
    icon: '🗡️',
    label: 'The Shadow',
    subtitle: 'Master of Cunning',
    desc: 'Rule from the darkness. Dark deeds, guild crimes, and arcane curses await the bold.',
    color: '#8E44AD',
    stats: { Strength: 10, Dexterity: 15, Speed: 15, Defense: 10, Gold: 100 },
  },
  {
    key: 'noble',
    icon: '👑',
    label: 'The Noble',
    subtitle: 'Master of Wealth',
    desc: 'Bend the economy to your will. Merchant Houses, Strongholds, and the Exchange await.',
    color: '#D4AC0D',
    stats: { Strength: 12, Dexterity: 12, Speed: 12, Defense: 12, Gold: 100 },
  },
];

const PathCard = ({ path, selected, onSelect }) => (
  <button
    onClick={() => onSelect(path.key)}
    data-testid={`path-select-${path.key}`}
    className="w-full text-left rounded-xl p-4 flex flex-col gap-2"
    style={{
      backgroundColor: selected ? `${path.color}18` : 'var(--aeth-stone-1)',
      border: `2px solid ${selected ? path.color : 'var(--aeth-iron)'}`,
      boxShadow: selected ? `0 0 20px ${path.color}25` : 'none',
      transition: 'border-color 0.2s ease, background-color 0.2s ease, box-shadow 0.2s ease',
      cursor: 'pointer',
    }}
  >
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-2">
        <span style={{ fontSize: '1.3rem' }}>{path.icon}</span>
        <div>
          <p style={{ fontFamily: "'Cinzel', serif", color: selected ? path.color : 'var(--aeth-parchment)', fontSize: '0.9rem', fontWeight: 700 }}>
            {path.label}
          </p>
          <p style={{ fontFamily: "'IBM Plex Sans', sans-serif", color: 'var(--aeth-iron)', fontSize: '0.72rem' }}>{path.subtitle}</p>
        </div>
      </div>
      {selected && (
        <div className="w-5 h-5 rounded-full flex items-center justify-center" style={{ backgroundColor: path.color }}>
          <Check size={12} color="white" />
        </div>
      )}
    </div>
    <p style={{ fontFamily: "'IBM Plex Sans', sans-serif", color: 'var(--aeth-parchment-dim)', fontSize: '0.78rem', lineHeight: 1.5 }}>
      {path.desc}
    </p>
    {/* Mini stats */}
    <div className="flex gap-2 flex-wrap mt-1">
      {Object.entries(path.stats).map(([k, v]) => (
        <span
          key={k}
          className="text-xs px-2 py-0.5 rounded"
          style={{
            backgroundColor: 'rgba(255,255,255,0.04)',
            border: '1px solid var(--aeth-iron)',
            color: 'var(--aeth-parchment-dim)',
            fontFamily: "'Azeret Mono', monospace",
          }}
        >
          {k[0]}: <span style={{ color: path.color }}>{v}</span>
        </span>
      ))}
    </div>
  </button>
);

// ─── LOGIN MODAL ─────────────────────────────────
export const LoginModal = ({ open, onClose, onSwitchToRegister, onSuccess }) => {
  const { loginWithData } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: '', password: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showPass, setShowPass] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.email || !form.password) { setError('All fields are required'); return; }
    setLoading(true); setError('');
    try {
      const res = await axios.post(`${API}/auth/login`, form);
      loginWithData(res.data);
      onClose();
      // Call parent's onSuccess for toast
      if (onSuccess) onSuccess(res.data);
      // Navigate immediately and reliably
      setTimeout(() => navigate('/game'), 100);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to enter the gate');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent data-testid="login-modal" className="max-w-md" style={{ backgroundColor: 'var(--aeth-stone-2)', border: '1px solid var(--aeth-iron)' }}>
        <DialogHeader>
          <div className="flex justify-center mb-2">
            <div className="w-14 h-14 rounded-full flex items-center justify-center" style={{ backgroundColor: 'var(--aeth-iron-2)', border: '2px solid var(--aeth-gold)', boxShadow: '0 0 20px rgba(214,162,77,0.2)' }}>
              <Shield size={24} style={{ color: 'var(--aeth-gold)' }} />
            </div>
          </div>
          <DialogTitle style={{ fontFamily: "'Cinzel', serif", color: 'var(--aeth-parchment)', textAlign: 'center', fontSize: '1.3rem', letterSpacing: '0.05em' }}>Enter the Gate</DialogTitle>
          <DialogDescription className="text-sm text-center mt-1" style={{ color: 'var(--aeth-parchment-dim)' }}>Prove your identity to the dungeon guard</DialogDescription>
        </DialogHeader>
        <Separator style={{ backgroundColor: 'var(--aeth-iron)', margin: '1rem 0' }} />
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label htmlFor="login-email" style={{ color: 'var(--aeth-parchment-dim)', fontFamily: "'Cinzel', serif", fontSize: '0.75rem', letterSpacing: '0.05em' }}>EMAIL ADDRESS</Label>
            <Input id="login-email" data-testid="login-email-input" type="email" placeholder="adventurer@realm.com" value={form.email} onChange={(e) => setForm(f => ({ ...f, email: e.target.value }))} className="mt-1" style={{ backgroundColor: 'var(--aeth-stone-1)', border: '1px solid var(--aeth-iron)', color: 'var(--aeth-parchment)' }} />
          </div>
          <div>
            <Label htmlFor="login-password" style={{ color: 'var(--aeth-parchment-dim)', fontFamily: "'Cinzel', serif", fontSize: '0.75rem', letterSpacing: '0.05em' }}>PASSPHRASE</Label>
            <div className="relative mt-1">
              <Input id="login-password" data-testid="login-password-input" type={showPass ? 'text' : 'password'} placeholder="Your secret passphrase" value={form.password} onChange={(e) => setForm(f => ({ ...f, password: e.target.value }))} style={{ backgroundColor: 'var(--aeth-stone-1)', border: '1px solid var(--aeth-iron)', color: 'var(--aeth-parchment)', paddingRight: '2.5rem' }} />
              <button type="button" onClick={() => setShowPass(s => !s)} className="absolute right-3 top-1/2 -translate-y-1/2" style={{ color: 'var(--aeth-iron)', background: 'none', border: 'none', cursor: 'pointer' }}>{showPass ? <EyeOff size={16} /> : <Eye size={16} />}</button>
            </div>
          </div>
          {error && (
            <p data-testid="auth-error-message" className="text-sm p-3 rounded-lg flex items-center gap-2" style={{ backgroundColor: 'rgba(142,29,44,0.22)', color: '#FF8A80', border: '1px solid rgba(200,50,60,0.55)', fontWeight: 500 }}>
              <span>⚠️</span> {error}
            </p>
          )}
          <button data-testid="login-submit-button" type="submit" disabled={loading} className="btn-gold w-full py-3 rounded-lg flex items-center justify-center gap-2">
            {loading && <Loader2 size={16} className="animate-spin" />}
            {loading ? 'Verifying...' : 'Enter the Realm'}
          </button>
        </form>
        <p className="text-sm text-center mt-4" style={{ color: 'var(--aeth-parchment-dim)' }}>
          No legend yet?{' '}
          <button onClick={() => { onClose(); onSwitchToRegister(); }} style={{ color: 'var(--aeth-gold)', background: 'none', border: 'none', cursor: 'pointer', fontWeight: 600 }}>Begin Your Story</button>
        </p>
      </DialogContent>
    </Dialog>
  );
};

// ─── REGISTER MODAL (2-step) ──────────────────────
export const RegisterModal = ({ open, onClose, onSwitchToLogin, onSuccess }) => {
  const { loginWithData } = useAuth();
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [form, setForm] = useState({ username: '', email: '', password: '' });
  const [pathChoice, setPathChoice] = useState('knight');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showPass, setShowPass] = useState(false);

  const handleStep1 = (e) => {
    e.preventDefault();
    if (!form.username || !form.email || !form.password) { setError('All fields are required'); return; }
    if (form.password.length < 6) { setError('Passphrase must be at least 6 characters'); return; }
    setError('');
    setStep(2);
  };

  const handleStep2 = async () => {
    setLoading(true); setError('');
    try {
      const res = await axios.post(`${API}/auth/register`, { ...form, path_choice: pathChoice });
      loginWithData(res.data);
      onClose();
      setStep(1);
      setForm({ username: '', email: '', password: '' });
      // Call parent's onSuccess for toast
      if (onSuccess) onSuccess(res.data);
      // Navigate immediately and reliably
      setTimeout(() => navigate('/game'), 100);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to register in the Realm');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setStep(1);
    setError('');
    onClose();
  };

  const selectedPath = PATHS.find(p => p.key === pathChoice);

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent data-testid="register-modal" className="max-w-lg" style={{ backgroundColor: 'var(--aeth-stone-2)', border: '1px solid var(--aeth-iron)', maxHeight: '90vh', overflowY: 'auto' }}>
        <DialogHeader>
          <div className="flex justify-center mb-2">
            <div className="w-14 h-14 rounded-full flex items-center justify-center" style={{ backgroundColor: 'var(--aeth-iron-2)', border: `2px solid ${step === 2 ? (selectedPath?.color || 'var(--aeth-gold)') : 'var(--aeth-gold)'}`, boxShadow: '0 0 20px rgba(214,162,77,0.2)', transition: 'border-color 0.3s ease' }}>
              {step === 1 ? <Sword size={24} style={{ color: 'var(--aeth-gold)' }} /> : <span style={{ fontSize: '1.5rem' }}>{selectedPath?.icon}</span>}
            </div>
          </div>
          <DialogTitle style={{ fontFamily: "'Cinzel', serif", color: 'var(--aeth-parchment)', textAlign: 'center', fontSize: '1.3rem', letterSpacing: '0.05em' }}>
            {step === 1 ? 'Begin Your Legend' : 'Choose Your Path'}
          </DialogTitle>
          <DialogDescription className="text-sm text-center mt-1" style={{ color: 'var(--aeth-parchment-dim)' }}>
            {step === 1 ? 'Register and forge your name in the annals of Aethoria' : 'Your chosen path defines your starting stats and destiny'}
          </DialogDescription>
          {/* Step indicator */}
          <div className="flex items-center justify-center gap-2 mt-3">
            {[1, 2].map(s => (
              <div key={s} className="flex items-center gap-2">
                <div className="w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold" style={{ backgroundColor: s <= step ? 'var(--aeth-gold)' : 'var(--aeth-iron-2)', color: s <= step ? 'var(--aeth-stone-0)' : 'var(--aeth-iron)', border: '1px solid var(--aeth-iron)', fontFamily: "'Cinzel', serif", transition: 'background-color 0.3s ease' }}>{s}</div>
                {s < 2 && <div className="w-8 h-px" style={{ backgroundColor: step > s ? 'var(--aeth-gold)' : 'var(--aeth-iron)', transition: 'background-color 0.3s ease' }} />}
              </div>
            ))}
          </div>
        </DialogHeader>
        <Separator style={{ backgroundColor: 'var(--aeth-iron)', margin: '1rem 0' }} />

        <AnimatePresence mode="wait">
          {step === 1 && (
            <motion.form key="step1" initial={{ opacity: 0, x: 12 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -12 }} transition={{ duration: 0.2 }} onSubmit={handleStep1} className="space-y-4">
              <div>
                <Label htmlFor="reg-username" style={{ color: 'var(--aeth-parchment-dim)', fontFamily: "'Cinzel', serif", fontSize: '0.75rem', letterSpacing: '0.05em' }}>ADVENTURER NAME</Label>
                <Input id="reg-username" data-testid="register-username-input" type="text" placeholder="What shall the realm call you?" value={form.username} onChange={(e) => setForm(f => ({ ...f, username: e.target.value }))} className="mt-1" style={{ backgroundColor: 'var(--aeth-stone-1)', border: '1px solid var(--aeth-iron)', color: 'var(--aeth-parchment)' }} />
              </div>
              <div>
                <Label htmlFor="reg-email" style={{ color: 'var(--aeth-parchment-dim)', fontFamily: "'Cinzel', serif", fontSize: '0.75rem', letterSpacing: '0.05em' }}>EMAIL ADDRESS</Label>
                <Input id="reg-email" data-testid="register-email-input" type="email" placeholder="adventurer@realm.com" value={form.email} onChange={(e) => setForm(f => ({ ...f, email: e.target.value }))} className="mt-1" style={{ backgroundColor: 'var(--aeth-stone-1)', border: '1px solid var(--aeth-iron)', color: 'var(--aeth-parchment)' }} />
              </div>
              <div>
                <Label htmlFor="reg-password" style={{ color: 'var(--aeth-parchment-dim)', fontFamily: "'Cinzel', serif", fontSize: '0.75rem', letterSpacing: '0.05em' }}>PASSPHRASE</Label>
                <div className="relative mt-1">
                  <Input id="reg-password" data-testid="register-password-input" type={showPass ? 'text' : 'password'} placeholder="Min. 6 characters" value={form.password} onChange={(e) => setForm(f => ({ ...f, password: e.target.value }))} style={{ backgroundColor: 'var(--aeth-stone-1)', border: '1px solid var(--aeth-iron)', color: 'var(--aeth-parchment)', paddingRight: '2.5rem' }} />
                  <button type="button" onClick={() => setShowPass(s => !s)} className="absolute right-3 top-1/2 -translate-y-1/2" style={{ color: 'var(--aeth-iron)', background: 'none', border: 'none', cursor: 'pointer' }}>{showPass ? <EyeOff size={16} /> : <Eye size={16} />}</button>
                </div>
              </div>
              {error && (
                <p data-testid="auth-error-message" className="text-sm p-3 rounded-lg flex items-center gap-2" style={{ backgroundColor: 'rgba(142,29,44,0.22)', color: '#FF8A80', border: '1px solid rgba(200,50,60,0.55)', fontWeight: 500 }}>
                  <span>⚠️</span> {error}
                </p>
              )}
              <button data-testid="register-next-button" type="submit" className="btn-gold w-full py-3 rounded-lg flex items-center justify-center gap-2">
                Choose Your Path <ChevronRight size={16} />
              </button>
            </motion.form>
          )}

          {step === 2 && (
            <motion.div key="step2" initial={{ opacity: 0, x: 12 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -12 }} transition={{ duration: 0.2 }} className="space-y-4">
              <p className="text-sm" style={{ color: 'var(--aeth-parchment-dim)', fontFamily: "'IBM Plex Sans', sans-serif" }}>Choose the path that defines your character in Aethoria. This cannot be changed later.</p>
              <div className="flex flex-col gap-3">
                {PATHS.map(path => (
                  <PathCard key={path.key} path={path} selected={pathChoice === path.key} onSelect={setPathChoice} />
                ))}
              </div>
              {error && (
                <p data-testid="auth-error-message" className="text-sm p-3 rounded-lg flex items-center gap-2" style={{ backgroundColor: 'rgba(142,29,44,0.22)', color: '#FF8A80', border: '1px solid rgba(200,50,60,0.55)', fontWeight: 500 }}>
                  <span>⚠️</span> {error}
                </p>
              )}
              <div className="flex gap-3">
                <button onClick={() => { setStep(1); setError(''); }} className="btn-iron flex-none px-4 py-3 rounded-lg flex items-center gap-2 text-sm">
                  <ChevronLeft size={16} /> Back
                </button>
                <button data-testid="register-submit-button" onClick={handleStep2} disabled={loading} className="btn-gold flex-1 py-3 rounded-lg flex items-center justify-center gap-2">
                  {loading && <Loader2 size={16} className="animate-spin" />}
                  {loading ? 'Forging your legend...' : `Join as ${selectedPath?.label}`}
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <p className="text-sm text-center mt-4" style={{ color: 'var(--aeth-parchment-dim)' }}>
          Already an adventurer?{' '}
          <button onClick={() => { handleClose(); onSwitchToLogin(); }} style={{ color: 'var(--aeth-gold)', background: 'none', border: 'none', cursor: 'pointer', fontWeight: 600 }}>Enter the Gate</button>
        </p>
      </DialogContent>
    </Dialog>
  );
};
