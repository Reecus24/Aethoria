import { useState } from 'react';
import axios from 'axios';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from './ui/dialog';
import { Label } from './ui/label';
import { Input } from './ui/input';
import { Separator } from './ui/separator';
import { Eye, EyeOff, Loader2, Shield, Sword } from 'lucide-react';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export const LoginModal = ({ open, onClose, onSwitchToRegister, onSuccess }) => {
  const [form, setForm] = useState({ email: '', password: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showPass, setShowPass] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.email || !form.password) {
      setError('All fields are required');
      return;
    }
    setLoading(true);
    setError('');
    try {
      const res = await axios.post(`${API}/auth/login`, form);
      onSuccess(res.data);
      onClose();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to enter the gate');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent
        data-testid="login-modal"
        className="max-w-md"
        style={{
          backgroundColor: 'var(--aeth-stone-2)',
          border: '1px solid var(--aeth-iron)',
          fontFamily: "'IBM Plex Sans', sans-serif",
        }}
      >
        <DialogHeader>
          <div className="flex justify-center mb-2">
            <div
              className="w-14 h-14 rounded-full flex items-center justify-center"
              style={{
                backgroundColor: 'var(--aeth-iron-2)',
                border: '2px solid var(--aeth-gold)',
                boxShadow: '0 0 20px rgba(214,162,77,0.2)',
              }}
            >
              <Shield size={24} style={{ color: 'var(--aeth-gold)' }} />
            </div>
          </div>
          <DialogTitle
            style={{
              fontFamily: "'Cinzel', serif",
              color: 'var(--aeth-parchment)',
              textAlign: 'center',
              fontSize: '1.3rem',
              letterSpacing: '0.05em',
            }}
          >
            Enter the Gate
          </DialogTitle>
          <p
            className="text-sm text-center mt-1"
            style={{ color: 'var(--aeth-parchment-dim)' }}
          >
            Prove your identity to the dungeon guard
          </p>
        </DialogHeader>

        <Separator style={{ backgroundColor: 'var(--aeth-iron)', margin: '1rem 0' }} />

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label
              htmlFor="login-email"
              style={{ color: 'var(--aeth-parchment-dim)', fontFamily: "'Cinzel', serif", fontSize: '0.75rem', letterSpacing: '0.05em' }}
            >
              EMAIL ADDRESS
            </Label>
            <Input
              id="login-email"
              data-testid="login-email-input"
              type="email"
              placeholder="adventurer@realm.com"
              value={form.email}
              onChange={(e) => setForm((f) => ({ ...f, email: e.target.value }))}
              className="mt-1"
              style={{
                backgroundColor: 'var(--aeth-stone-1)',
                border: '1px solid var(--aeth-iron)',
                color: 'var(--aeth-parchment)',
              }}
            />
          </div>

          <div>
            <Label
              htmlFor="login-password"
              style={{ color: 'var(--aeth-parchment-dim)', fontFamily: "'Cinzel', serif", fontSize: '0.75rem', letterSpacing: '0.05em' }}
            >
              PASSPHRASE
            </Label>
            <div className="relative mt-1">
              <Input
                id="login-password"
                data-testid="login-password-input"
                type={showPass ? 'text' : 'password'}
                placeholder="Your secret passphrase"
                value={form.password}
                onChange={(e) => setForm((f) => ({ ...f, password: e.target.value }))}
                style={{
                  backgroundColor: 'var(--aeth-stone-1)',
                  border: '1px solid var(--aeth-iron)',
                  color: 'var(--aeth-parchment)',
                  paddingRight: '2.5rem',
                }}
              />
              <button
                type="button"
                onClick={() => setShowPass((s) => !s)}
                className="absolute right-3 top-1/2 -translate-y-1/2"
                style={{ color: 'var(--aeth-iron)', background: 'none', border: 'none', cursor: 'pointer' }}
              >
                {showPass ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>

          {error && (
            <p
              className="text-sm p-3 rounded-lg"
              style={{
                backgroundColor: 'rgba(142,29,44,0.15)',
                color: '#E57373',
                border: '1px solid rgba(142,29,44,0.4)',
              }}
            >
              {error}
            </p>
          )}

          <button
            data-testid="login-submit-button"
            type="submit"
            disabled={loading}
            className="btn-gold w-full py-3 rounded-lg flex items-center justify-center gap-2"
          >
            {loading ? <Loader2 size={16} className="animate-spin" /> : null}
            {loading ? 'Verifying your identity...' : 'Enter the Realm'}
          </button>
        </form>

        <p
          className="text-sm text-center mt-4"
          style={{ color: 'var(--aeth-parchment-dim)' }}
        >
          No legend yet?{' '}
          <button
            onClick={() => { onClose(); onSwitchToRegister(); }}
            style={{ color: 'var(--aeth-gold)', background: 'none', border: 'none', cursor: 'pointer', fontWeight: 600 }}
          >
            Begin Your Story
          </button>
        </p>
      </DialogContent>
    </Dialog>
  );
};

export const RegisterModal = ({ open, onClose, onSwitchToLogin, onSuccess }) => {
  const [form, setForm] = useState({ username: '', email: '', password: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showPass, setShowPass] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.username || !form.email || !form.password) {
      setError('All fields are required');
      return;
    }
    if (form.password.length < 6) {
      setError('Passphrase must be at least 6 characters');
      return;
    }
    setLoading(true);
    setError('');
    try {
      const res = await axios.post(`${API}/auth/register`, form);
      onSuccess(res.data);
      onClose();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to register in the Realm');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent
        data-testid="register-modal"
        className="max-w-md"
        style={{
          backgroundColor: 'var(--aeth-stone-2)',
          border: '1px solid var(--aeth-iron)',
          fontFamily: "'IBM Plex Sans', sans-serif",
        }}
      >
        <DialogHeader>
          <div className="flex justify-center mb-2">
            <div
              className="w-14 h-14 rounded-full flex items-center justify-center"
              style={{
                backgroundColor: 'var(--aeth-iron-2)',
                border: '2px solid var(--aeth-gold)',
                boxShadow: '0 0 20px rgba(214,162,77,0.2)',
              }}
            >
              <Sword size={24} style={{ color: 'var(--aeth-gold)' }} />
            </div>
          </div>
          <DialogTitle
            style={{
              fontFamily: "'Cinzel', serif",
              color: 'var(--aeth-parchment)',
              textAlign: 'center',
              fontSize: '1.3rem',
              letterSpacing: '0.05em',
            }}
          >
            Begin Your Legend
          </DialogTitle>
          <p
            className="text-sm text-center mt-1"
            style={{ color: 'var(--aeth-parchment-dim)' }}
          >
            Register and forge your name in the annals of Aethoria
          </p>
        </DialogHeader>

        <Separator style={{ backgroundColor: 'var(--aeth-iron)', margin: '1rem 0' }} />

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label
              htmlFor="reg-username"
              style={{ color: 'var(--aeth-parchment-dim)', fontFamily: "'Cinzel', serif", fontSize: '0.75rem', letterSpacing: '0.05em' }}
            >
              ADVENTURER NAME
            </Label>
            <Input
              id="reg-username"
              data-testid="register-username-input"
              type="text"
              placeholder="What shall the realm call you?"
              value={form.username}
              onChange={(e) => setForm((f) => ({ ...f, username: e.target.value }))}
              className="mt-1"
              style={{
                backgroundColor: 'var(--aeth-stone-1)',
                border: '1px solid var(--aeth-iron)',
                color: 'var(--aeth-parchment)',
              }}
            />
          </div>

          <div>
            <Label
              htmlFor="reg-email"
              style={{ color: 'var(--aeth-parchment-dim)', fontFamily: "'Cinzel', serif", fontSize: '0.75rem', letterSpacing: '0.05em' }}
            >
              EMAIL ADDRESS
            </Label>
            <Input
              id="reg-email"
              data-testid="register-email-input"
              type="email"
              placeholder="adventurer@realm.com"
              value={form.email}
              onChange={(e) => setForm((f) => ({ ...f, email: e.target.value }))}
              className="mt-1"
              style={{
                backgroundColor: 'var(--aeth-stone-1)',
                border: '1px solid var(--aeth-iron)',
                color: 'var(--aeth-parchment)',
              }}
            />
          </div>

          <div>
            <Label
              htmlFor="reg-password"
              style={{ color: 'var(--aeth-parchment-dim)', fontFamily: "'Cinzel', serif", fontSize: '0.75rem', letterSpacing: '0.05em' }}
            >
              PASSPHRASE
            </Label>
            <div className="relative mt-1">
              <Input
                id="reg-password"
                data-testid="register-password-input"
                type={showPass ? 'text' : 'password'}
                placeholder="Min. 6 characters"
                value={form.password}
                onChange={(e) => setForm((f) => ({ ...f, password: e.target.value }))}
                style={{
                  backgroundColor: 'var(--aeth-stone-1)',
                  border: '1px solid var(--aeth-iron)',
                  color: 'var(--aeth-parchment)',
                  paddingRight: '2.5rem',
                }}
              />
              <button
                type="button"
                onClick={() => setShowPass((s) => !s)}
                className="absolute right-3 top-1/2 -translate-y-1/2"
                style={{ color: 'var(--aeth-iron)', background: 'none', border: 'none', cursor: 'pointer' }}
              >
                {showPass ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>

          {error && (
            <p
              className="text-sm p-3 rounded-lg"
              style={{
                backgroundColor: 'rgba(142,29,44,0.15)',
                color: '#E57373',
                border: '1px solid rgba(142,29,44,0.4)',
              }}
            >
              {error}
            </p>
          )}

          <button
            data-testid="register-submit-button"
            type="submit"
            disabled={loading}
            className="btn-gold w-full py-3 rounded-lg flex items-center justify-center gap-2"
          >
            {loading ? <Loader2 size={16} className="animate-spin" /> : null}
            {loading ? 'Forging your legend...' : 'Join the Realm'}
          </button>
        </form>

        <p
          className="text-sm text-center mt-4"
          style={{ color: 'var(--aeth-parchment-dim)' }}
        >
          Already an adventurer?{' '}
          <button
            onClick={() => { onClose(); onSwitchToLogin(); }}
            style={{ color: 'var(--aeth-gold)', background: 'none', border: 'none', cursor: 'pointer', fontWeight: 600 }}
          >
            Enter the Gate
          </button>
        </p>
      </DialogContent>
    </Dialog>
  );
};
