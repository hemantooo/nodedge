"use client";

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Loader2, AlertCircle, CheckCircle2, Lock } from 'lucide-react';
import Header from '../../components/Header';

const inputClass =
  'w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-[#985EFF]/60 focus:ring-1 focus:ring-[#985EFF]/30 transition-all duration-200';

export default function AdminPage() {
  const [pin, setPin] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleProcessTickets = async () => {
    if (!pin) {
      setError('Please enter the Admin Password.');
      return;
    }
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || '';
      const res = await fetch(`${backendUrl}/api/admin/process-tickets`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password: pin }),
      });

      const data = await res.json();

      if (res.ok) {
        setSuccess(`Successfully processed tickets. Approved Emails Sent: ${data.approved_sent}, Rejection Emails Sent: ${data.rejected_sent}`);
      } else {
        setError(data.detail || 'Failed to process tickets. Please check the password.');
      }
    } catch {
      setError('Could not connect to the server. Please check your connection and try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-[#0A0A0A] text-white selection:bg-[#985EFF]/30 overflow-hidden font-sans">
      <Header />
      <section className="py-32 px-4 relative z-10 min-h-[80vh] flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="max-w-md w-full bg-white/5 backdrop-blur-xl border border-white/10 p-8 rounded-3xl shadow-2xl relative overflow-hidden"
        >
          <div className="absolute -top-20 -left-20 w-40 h-40 bg-[#FF5257]/10 rounded-full blur-3xl pointer-events-none" />
          
          <div className="text-center mb-8 relative z-10">
            <div className="w-16 h-16 bg-white/5 rounded-2xl flex items-center justify-center mx-auto mb-4 border border-white/10">
              <Lock className="w-8 h-8 text-[#985EFF]" />
            </div>
            <h2 className="text-2xl font-bold mb-2">Admin Dashboard</h2>
            <p className="text-gray-400 text-sm">Send tickets and rejection emails based on Google Sheet status.</p>
          </div>

          <div className="space-y-6 relative z-10">
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">Admin Password</label>
              <input
                type="password"
                placeholder="Enter password"
                value={pin}
                onChange={(e) => setPin(e.target.value)}
                className={inputClass}
              />
            </div>

            <AnimatePresence>
              {error && (
                <motion.div
                  initial={{ opacity: 0, y: -8 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -8 }}
                  className="flex items-start gap-3 p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400"
                >
                  <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
                  <p className="text-sm">{error}</p>
                </motion.div>
              )}
            </AnimatePresence>

            <AnimatePresence>
              {success && (
                <motion.div
                  initial={{ opacity: 0, y: -8 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -8 }}
                  className="flex items-start gap-3 p-4 rounded-xl bg-green-500/10 border border-green-500/30 text-green-400"
                >
                  <CheckCircle2 className="w-5 h-5 flex-shrink-0 mt-0.5" />
                  <p className="text-sm">{success}</p>
                </motion.div>
              )}
            </AnimatePresence>

            <button
              onClick={handleProcessTickets}
              disabled={loading}
              className="w-full py-4 rounded-xl font-semibold text-white bg-gradient-to-r from-[#FF5257] to-[#985EFF] hover:opacity-90 active:scale-95 transition-all duration-200 flex items-center justify-center gap-2 disabled:opacity-50"
            >
              {loading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Processing...
                </>
              ) : (
                'Process Pending Approvals'
              )}
            </button>
          </div>
        </motion.div>
      </section>
    </main>
  );
}
