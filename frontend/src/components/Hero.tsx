"use client";

import { motion } from 'framer-motion';
import { useState, useEffect } from 'react';

export default function Hero() {
  const [timeLeft, setTimeLeft] = useState({ days: 14, hours: 0, minutes: 0, seconds: 0 });

  useEffect(() => {
    // 14 days from initialization time
    const targetDate = new Date(Date.now() + 14 * 24 * 60 * 60 * 1000).getTime();

    const interval = setInterval(() => {
      const now = new Date().getTime();
      const difference = targetDate - now;

      if (difference > 0) {
        setTimeLeft({
          days: Math.floor(difference / (1000 * 60 * 60 * 24)),
          hours: Math.floor((difference % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60)),
          minutes: Math.floor((difference % (1000 * 60 * 60)) / (1000 * 60)),
          seconds: Math.floor((difference % (1000 * 60)) / 1000)
        });
      } else {
        clearInterval(interval);
      }
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  const scrollToForm = () => {
    document.getElementById('register-section')?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <section className="relative min-h-screen flex flex-col items-center justify-center text-center px-4 pt-20 overflow-hidden">
      {/* Background glow effects */}
      <div className="absolute top-1/2 left-1/4 w-96 h-96 bg-[#FF5257]/20 rounded-full blur-[128px] -translate-y-1/2" />
      <div className="absolute top-1/2 right-1/4 w-96 h-96 bg-[#985EFF]/20 rounded-full blur-[128px] -translate-y-1/2" />

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
        className="z-10 max-w-4xl"
      >
        <span className="inline-block py-1 px-3 mb-6 rounded-full bg-white/5 border border-white/10 text-sm font-medium text-gray-300 backdrop-blur-sm">
          Exclusive Event for AIML Students @ Parul University
        </span>
        <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-6 bg-clip-text text-transparent bg-gradient-to-br from-white to-gray-500">
          3-Day Swift & SwiftUI
          <br />
          Intensive Masterclass
        </h1>
        <p className="text-xl text-gray-400 mb-12 max-w-2xl mx-auto">
          Master iOS development from the ground up. Build native apps, learn modern declarative UI, and launch your Apple ecosystem journey.
        </p>

        {/* Countdown */}
        <div className="flex items-center justify-center gap-4 md:gap-8 mb-12">
          {[
            { label: 'Days', value: timeLeft.days },
            { label: 'Hours', value: timeLeft.hours },
            { label: 'Minutes', value: timeLeft.minutes },
            { label: 'Seconds', value: timeLeft.seconds },
          ].map((item) => (
            <div key={item.label} className="flex flex-col items-center">
              <div className="w-16 h-16 md:w-24 md:h-24 flex items-center justify-center bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl md:rounded-3xl shadow-lg mb-2">
                <span className="text-2xl md:text-4xl font-semibold text-white">{item.value.toString().padStart(2, '0')}</span>
              </div>
              <span className="text-xs md:text-sm text-gray-400 uppercase tracking-widest">{item.label}</span>
            </div>
          ))}
        </div>

        <button
          onClick={scrollToForm}
          className="group relative inline-flex items-center justify-center px-8 py-4 text-base font-semibold text-white transition-all duration-200 bg-white/10 border border-white/20 rounded-full hover:bg-white/20 hover:scale-105 overflow-hidden backdrop-blur-md"
        >
          <span className="relative z-10">Claim Your Spot</span>
          <div className="absolute inset-0 -z-10 bg-gradient-to-r from-[#FF5257] to-[#985EFF] opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
        </button>
      </motion.div>
    </section>
  );
}
