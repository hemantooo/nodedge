"use client";

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Loader2, AlertCircle, CheckCircle2 } from 'lucide-react';

interface FormData {
  full_name: string;
  enrollment_no: string;
  email: string;
  class_name: string;
  phone_number: string;
  has_mac: string;
  accepted_terms: boolean;
}

const inputClass =
  'w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-[#985EFF]/60 focus:ring-1 focus:ring-[#985EFF]/30 transition-all duration-200';

export default function RegistrationForm() {
  const [form, setForm] = useState<FormData>({
    full_name: '',
    enrollment_no: '',
    email: '',
    class_name: '',
    phone_number: '',
    has_mac: '',
    accepted_terms: false,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [isSuccess, setIsSuccess] = useState(false);

  const validate = (): string => {
    if (!form.full_name.trim()) return 'Full name is required.';
    if (!form.enrollment_no.trim()) return 'Enrollment number is required.';
    if (!form.email.trim()) return 'Email is required.';
    if (!form.email.endsWith('@paruluniversity.ac.in'))
      return 'Email must be a Parul University address (@paruluniversity.ac.in).';
    if (!form.phone_number.trim()) return 'Phone number is required.';
    if (!/^\d{10}$/.test(form.phone_number.trim())) return 'Phone number must be exactly 10 digits.';
    if (!form.class_name.trim()) return 'Class is required.';
    if (!form.has_mac) return 'Please select your Mac availability.';
    if (!form.accepted_terms) return 'You must accept the terms and conditions to register.';
    return '';
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const validationError = validate();
    if (validationError) { setError(validationError); return; }
    setError('');
    setLoading(true);

    try {
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || '';
      const res = await fetch(`${backendUrl}/api/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          full_name: form.full_name,
          enrollment_no: form.enrollment_no,
          email: form.email,
          class_name: form.class_name,
          phone_number: form.phone_number,
          has_mac: form.has_mac,
        }),
      });

      const data = await res.json();

      if (res.ok) {
        setIsSuccess(true);
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

  if (isSuccess) return (
    <section id="register-section" className="py-24 px-4 relative z-10 min-h-[60vh] flex items-center justify-center">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="max-w-md w-full bg-white/5 backdrop-blur-xl border border-[#985EFF]/30 p-8 rounded-3xl shadow-2xl text-center relative overflow-hidden"
      >
        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-[#FF5257] to-[#985EFF]" />
        <div className="w-20 h-20 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-6">
          <CheckCircle2 className="w-10 h-10 text-green-400" />
        </div>
        <h2 className="text-2xl font-bold text-white mb-4">Application Submitted!</h2>
        <p className="text-gray-300 leading-relaxed mb-6">
          Thank you for registering, <strong>{form.full_name}</strong>. We are currently reviewing applications and will share the ticket with selected participants shortly via email.
        </p>
        <p className="text-sm text-gray-400">
          We will notify you about your selection status soon.
        </p>
      </motion.div>
    </section>
  );

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

            {/* Email & Phone */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
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

              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">Phone Number</label>
                <input
                  id="phone_number"
                  type="tel"
                  placeholder="e.g. 9876543210"
                  value={form.phone_number}
                  onChange={(e) => setForm({ ...form, phone_number: e.target.value })}
                  className={inputClass}
                />
                <p className="text-xs text-gray-600 mt-1.5">10 digits without country code.</p>
              </div>
            </div>

            {/* Class + Has Mac row */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              {/* Class */}
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">Class</label>
                <input
                  id="class_name"
                  type="text"
                  placeholder="e.g. 2AIML4"
                  value={form.class_name}
                  onChange={(e) => setForm({ ...form, class_name: e.target.value })}
                  className={inputClass}
                />
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

            {/* Conditional Mac Instructions */}
            <AnimatePresence>
              {form.has_mac === 'yes' && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="overflow-hidden"
                >
                  <div className="p-4 rounded-xl bg-[#985EFF]/10 border border-[#985EFF]/30 text-gray-300 mt-2">
                    <h4 className="font-semibold text-white mb-2">Mac User Requirements</h4>
                    <p className="text-sm leading-relaxed">
                      Please ensure you have the <strong>latest stable version of Xcode</strong> (not a beta version) and the <strong>iOS Simulator</strong> installed on your machine before the event.
                    </p>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Terms and Conditions */}
            <div className="pt-4 border-t border-white/10">
              <label className="flex items-start gap-3 cursor-pointer group">
                <div className="relative flex items-center justify-center mt-0.5">
                  <input
                    type="checkbox"
                    id="terms_conditions"
                    checked={form.accepted_terms}
                    onChange={(e) => setForm({ ...form, accepted_terms: e.target.checked })}
                    className="peer appearance-none w-5 h-5 rounded-md border border-white/20 bg-white/5 checked:bg-gradient-to-r checked:from-[#FF5257] checked:to-[#985EFF] checked:border-transparent transition-all"
                  />
                  <CheckCircle2 className="absolute w-3 h-3 text-white opacity-0 peer-checked:opacity-100 pointer-events-none" strokeWidth={4} />
                </div>
                <span className="text-sm text-gray-400 group-hover:text-gray-300 transition-colors">
                  I confirm that I will attend all 3 days of the masterclass and comply with the prerequisites.
                </span>
              </label>
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
