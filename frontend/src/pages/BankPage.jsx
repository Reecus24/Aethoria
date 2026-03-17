import { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import axios from '../utils/axios';
import { motion } from 'framer-motion';
import { Landmark, TrendingUp, ArrowDownToLine, ArrowUpFromLine } from 'lucide-react';
import { toast } from 'sonner';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function BankPage() {
  const { gameState, refreshGameState } = useOutletContext();
  const [account, setAccount] = useState(null);
  const [depositAmount, setDepositAmount] = useState('');
  const [withdrawAmount, setWithdrawAmount] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAccount();
  }, []);

  const fetchAccount = async () => {
    try {
      const res = await axios.get(`${API}/game/bank/account`);
      setAccount(res.data);
      setLoading(false);
    } catch (err) {
      toast.error('Fehler beim Laden des Bankkontos');
      setLoading(false);
    }
  };

  const handleDeposit = async () => {
    const amount = parseInt(depositAmount);
    if (!amount || amount < 1) {
      toast.error('Ungültiger Betrag');
      return;
    }
    if (amount > gameState.resources.gold) {
      toast.error('Nicht genug Gold!');
      return;
    }

    try {
      const res = await axios.post(`${API}/game/bank/deposit`, { amount });
      toast.success(res.data.message);
      setDepositAmount('');
      fetchAccount();
      refreshGameState();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Fehler beim Einzahlen');
    }
  };

  const handleWithdraw = async () => {
    const amount = parseInt(withdrawAmount);
    if (!amount || amount < 1) {
      toast.error('Ungültiger Betrag');
      return;
    }

    try {
      const res = await axios.post(`${API}/game/bank/withdraw`, { amount });
      toast.success(res.data.message);
      setWithdrawAmount('');
      fetchAccount();
      refreshGameState();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Fehler beim Abheben');
    }
  };

  if (loading) return <div className="text-center py-20">Loading bank...</div>;

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2" style={{ color: 'var(--aeth-parchment)', fontFamily: "'Cinzel', serif" }}>
          Royal Bank & Treasury
        </h1>
        <p style={{ color: 'var(--aeth-parchment-dim)', fontFamily: "'IBM Plex Sans', sans-serif" }}>
          Verwalte dein Vermögen sicher
        </p>
      </div>

      {/* Account Balance */}
      <div className="aeth-card p-8 mb-6 text-center">
        <p className="text-sm mb-2" style={{ color: 'var(--aeth-parchment-dim)' }}>Bankguthaben</p>
        <p className="text-4xl font-bold" style={{ color: 'var(--aeth-gold)', fontFamily: "'Azeret Mono', monospace" }}>
          {account.balance.toLocaleString()} Gold
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        {/* Deposit */}
        <div className="aeth-card p-6">
          <div className="flex items-center gap-2 mb-4">
            <ArrowDownToLine size={20} style={{ color: 'var(--aeth-gold)' }} />
            <h2 className="text-lg font-semibold" style={{ color: 'var(--aeth-parchment)', fontFamily: "'Cinzel', serif" }}>
              Einzahlen
            </h2>
          </div>
          <p className="text-xs mb-4" style={{ color: 'var(--aeth-parchment-dim)' }}>
            Aktuell bei dir: {gameState.resources.gold.toLocaleString()} Gold
          </p>
          <input
            type="number"
            value={depositAmount}
            onChange={(e) => setDepositAmount(e.target.value)}
            placeholder="Betrag"
            className="w-full px-4 py-3 rounded-lg mb-4 text-sm"
            style={{
              backgroundColor: 'var(--aeth-stone-1)',
              border: '1px solid var(--aeth-iron)',
              color: 'var(--aeth-parchment)',
              fontFamily: "'Azeret Mono', monospace"
            }}
            data-testid="deposit-input"
          />
          <button
            onClick={handleDeposit}
            className="btn-gold w-full py-3 rounded-lg font-semibold"
            data-testid="deposit-btn"
          >
            Einzahlen
          </button>
        </div>

        {/* Withdraw */}
        <div className="aeth-card p-6">
          <div className="flex items-center gap-2 mb-4">
            <ArrowUpFromLine size={20} style={{ color: 'var(--aeth-gold)' }} />
            <h2 className="text-lg font-semibold" style={{ color: 'var(--aeth-parchment)', fontFamily: "'Cinzel', serif" }}>
              Abheben
            </h2>
          </div>
          <p className="text-xs mb-4" style={{ color: 'var(--aeth-parchment-dim)' }}>
            Auf Bank: {account.balance.toLocaleString()} Gold
          </p>
          <input
            type="number"
            value={withdrawAmount}
            onChange={(e) => setWithdrawAmount(e.target.value)}
            placeholder="Betrag"
            className="w-full px-4 py-3 rounded-lg mb-4 text-sm"
            style={{
              backgroundColor: 'var(--aeth-stone-1)',
              border: '1px solid var(--aeth-iron)',
              color: 'var(--aeth-parchment)',
              fontFamily: "'Azeret Mono', monospace"
            }}
            data-testid="withdraw-input"
          />
          <button
            onClick={handleWithdraw}
            className="btn-gold w-full py-3 rounded-lg font-semibold"
            data-testid="withdraw-btn"
          >
            Abheben
          </button>
        </div>
      </div>
    </div>
  );
};