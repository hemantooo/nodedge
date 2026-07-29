"use client";

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Loader2, AlertCircle, CheckCircle2 } from 'lucide-react';
import StudentPass from './StudentPass';

type Proficiency = 'Beginner' | 'Intermediate' | 'Advanced';

interface FormData {
  full_name: string;
  enrollment_no: string;
  email: string;
  semester: string;
  has_mac: string;
  proficiency: Proficiency | '';
}

interface PassData {
  full_name: string;
  enrollment_no: string;
  has_mac: string;
  registration_id: string;
}

const inputClass =
  'w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-[#985EFF]/60 focus:ring-1 focus:ring-[#985EFF]/30 transition-all duration-200';

export default function RegistrationForm() {
  const [form, setForm] = useState<FormData>({
    full_name: '',
    enrollment_no: '',
    email: '',
    semester: '',
    has_mac: '',
    proficiency: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [passData, setPassData] = useState<PassData | null>(null);

  const validate = (): string => {
    if (!form.full_name.trim()) return 'Full name is required.';
    if (!form.enrollment_no.trim()) return 'Enrollment number is required.';
    if (!form.email.trim()) return 'Email is required.';
    if (!form.email.endsWith('@paruluniversity.ac.in'))
      return 'Email must be a Parul University address (@paruluniversity.ac.in).';
    if (!form.semester) return 'Please select your semester.';
    if (!form.has_mac) return 'Please select your Mac availability.';
    if (!form.proficiency) return 'Please select your proficiency level.';
    return '';
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const validationError = validate();
    if (validationError) { setError(validationError); return; }
    setError('');
    setLoading(true);

    try {
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
      const res = await fetch(`${backendUrl}/api/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          full_name: form.full_name,
          enrollment_no: form.enrollment_no,
          email: form.email,
          semester: form.semester,
          has_mac: form.has_mac,
          proficiency: form.proficiency,
        }),
      });

      const data = await res.json();

      if (res.ok) {
        setPassData({
          full_name: form.full_name,
          enrollment_no: form.enrollment_no,
          has_mac: form.has_mac,
          registration_id: data.registration_id,
        });
      } else if (res.status === 400) {
        setError(data.detail || 'Registration failed. You may already be registered or your email is invalid.');
      } else {
        setError('An unexpected error occurred. Please try again later.');
      }
    } catch {
      setError('Could not connect to the server. Please check your connection and try again.');
    } finally {
      setLoading(false);
    }
  };

  if (passData) return <StudentPass data={passData} />;

  return (
    <section id="register-section" className="py-24 px-4 relative z-10">
      <div className="max-w-2xl mx-auto">
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-5xl font-bold mb-4">Claim Your Spot</h2>
          <p className="text-gray-400">Seats are limited. Register now to secure your place in the masterclass.</p>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="relative rounded-3xl bg-white/5 backdrop-blur-xl border border-white/10 p-8 md:p-12 shadow-2xl overflow-hidden"
        >
          {/* Glow accents */}
          <div className="absolute -top-20 -left-20 w-60 h-60 bg-[#985EFF]/10 rounded-full blur-3xl pointer-events-none" />
          <div className="absolute -bottom-20 -right-20 w-60 h-60 bg-[#FF5257]/10 rounded-full blur-3xl pointer-events-none" />

          <form onSubmit={handleSubmit} noValidate className="relative z-10 space-y-6">
            {/* Full Name */}
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">Full Name</label>
              <input
                id="full_name"
                type="text"
                placeholder="e.g. Aisha Mehta"
                value={form.full_name}
                onChange={(e) => setForm({ ...form, full_name: e.target.value })}
                className={inputClass}
              />
            </div>

            {/* Enrollment No */}
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">Enrollment Number</label>
              <input
                id="enrollment_no"
                type="text"
                placeholder="e.g. 22BAIML123"
                value={form.enrollment_no}
                onChange={(e) => setForm({ ...form, enrollment_no: e.target.value })}
                className={inputClass}
              />
            </div>

            {/* Email */}
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">University Email</label>
              <input
                id="email"
                type="email"
                placeholder="yourname@paruluniversity.ac.in"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
                className={inputClass}
              />
              <p className="text-xs text-gray-600 mt-1.5">Must be your @paruluniversity.ac.in address.</p>
            </div>

            {/* Semester + Has Mac row */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              {/* Semester */}
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">Semester</label>
                <select
                  id="semester"
                  value={form.semester}
                  onChange={(e) => setForm({ ...form, semester: e.target.value })}
                  className={`${inputClass} appearance-none`}
                >
                  <option value="" className="bg-gray-900">Select semester</option>
                  {[1, 2, 3, 4, 5, 6, 7, 8].map((s) => (
                    <option key={s} value={`Sem ${s}`} className="bg-gray-900">Sem {s}</option>
                  ))}
                </select>
              </div>

              {/* Has Mac */}
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">Mac Availability</label>
                <div className="flex flex-col gap-2">
                  {[
                    { value: 'yes', label: 'Yes, I have a Mac' },
                    { value: 'no', label: 'No, I need a lab machine' },
                  ].map((opt) => (
                    <label key={opt.value} className={`flex items-center gap-3 p-3 rounded-xl border cursor-pointer transition-all duration-200 ${form.has_mac === opt.value ? 'border-[#985EFF]/60 bg-[#985EFF]/10' : 'border-white/10 bg-white/5 hover:border-white/20'}`}>
                      <input
                        id={`has_mac_${opt.value}`}
                        type="radio"
                        name="has_mac"
                        value={opt.value}
                        checked={form.has_mac === opt.value}
                        onChange={() => setForm({ ...form, has_mac: opt.value })}
                        className="accent-[#985EFF]"
                      />
                      <span className="text-sm text-gray-300">{opt.label}</span>
                    </label>
                  ))}
                </div>
              </div>
            </div>

            {/* Proficiency */}
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-3">Proficiency Level</label>
              <div className="flex gap-3 flex-wrap">
                {(['Beginner', 'Intermediate', 'Advanced'] as Proficiency[]).map((level) => (
                  <button
                    key={level}
                    type="button"
                    id={`proficiency_${level.toLowerCase()}`}
                    onClick={() => setForm({ ...form, proficiency: level })}
                    className={`px-5 py-2 rounded-full text-sm font-medium border transition-all duration-200 ${form.proficiency === level ? 'bg-gradient-to-r from-[#FF5257] to-[#985EFF] border-transparent text-white shadow-lg shadow-[#985EFF]/20' : 'border-white/10 bg-white/5 text-gray-400 hover:border-white/20 hover:text-white'}`}
                  >
                    {level}
                  </button>
                ))}
              </div>
            </div>

            {/* Error Banner */}
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

            {/* Submit Button */}
            <button
              type="submit"
              id="submit-registration"
              disabled={loading}
              className="w-full py-4 rounded-xl font-semibold text-white bg-gradient-to-r from-[#FF5257] to-[#985EFF] hover:opacity-90 active:scale-95 transition-all duration-200 flex items-center justify-center gap-2 disabled:opacity-50"
            >
              {loading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Submitting…
                </>
              ) : (
                <>
                  <CheckCircle2 className="w-5 h-5" />
                  Submit Application
                </>
              )}
            </button>
          </form>
        </motion.div>
      </div>
    </section>
  );
}
