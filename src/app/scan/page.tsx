"use client";

import { useEffect, useState, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  QrCode, 
  Lock, 
  CheckCircle2, 
  AlertTriangle, 
  XCircle, 
  Search, 
  Users, 
  Play, 
  Square,
  RefreshCw,
  LogOut,
  Laptop
} from "lucide-react";

interface Attendee {
  full_name: string;
  enrollment_no: string;
  email: string;
  semester: string;
  has_mac: string;
  proficiency: string;
  attendance: string;
}

interface ScanLog {
  timestamp: string;
  registration_id: string;
  name: string;
  status: "success" | "already_marked" | "error";
  message: string;
}

// Browser Audio Synthesizer (Web Audio API)
const playAudioBeep = (type: "success" | "warning" | "error") => {
  try {
    const AudioContextClass = window.AudioContext || (window as any).webkitAudioContext;
    if (!AudioContextClass) return;
    const ctx = new AudioContextClass();
    
    if (ctx.state === "suspended") {
      ctx.resume();
    }
    
    if (type === "success") {
      // High quick double beep
      const osc1 = ctx.createOscillator();
      const gain1 = ctx.createGain();
      osc1.connect(gain1);
      gain1.connect(ctx.destination);
      osc1.frequency.setValueAtTime(880, ctx.currentTime);
      gain1.gain.setValueAtTime(0.1, ctx.currentTime);
      gain1.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.12);
      osc1.start(ctx.currentTime);
      osc1.stop(ctx.currentTime + 0.12);
      
      const osc2 = ctx.createOscillator();
      const gain2 = ctx.createGain();
      osc2.connect(gain2);
      gain2.connect(ctx.destination);
      osc2.frequency.setValueAtTime(1320, ctx.currentTime + 0.1);
      gain2.gain.setValueAtTime(0.1, ctx.currentTime + 0.1);
      gain2.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.25);
      osc2.start(ctx.currentTime + 0.1);
      osc2.stop(ctx.currentTime + 0.25);
    } else if (type === "warning") {
      // Double mid chime
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.frequency.setValueAtTime(587.33, ctx.currentTime);
      gain.gain.setValueAtTime(0.1, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.25);
      osc.start(ctx.currentTime);
      osc.stop(ctx.currentTime + 0.25);
    } else {
      // Low buzz
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.type = "sawtooth";
      osc.frequency.setValueAtTime(130, ctx.currentTime);
      gain.gain.setValueAtTime(0.15, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.4);
      osc.start(ctx.currentTime);
      osc.stop(ctx.currentTime + 0.4);
    }
  } catch (e) {
    console.error("Audio playback error:", e);
  }
};

export default function ScanPage() {
  const [pin, setPin] = useState("");
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [authError, setAuthError] = useState("");
  const [stats, setStats] = useState({ total: 0, present: 0 });
  const [loadingStats, setLoadingStats] = useState(false);

  // Scanner states
  const [scannerActive, setScannerActive] = useState(false);
  const [scannerError, setScannerError] = useState("");
  const [scanning, setScanning] = useState(false);
  const [scanResult, setScanResult] = useState<{
    type: "success" | "already_marked" | "error";
    message: string;
    student?: Attendee;
  } | null>(null);

  // Manual Check-in state
  const [manualId, setManualId] = useState("");
  const [manualLoading, setManualLoading] = useState(false);

  // Logs state
  const [logs, setLogs] = useState<ScanLog[]>([]);

  const html5QrCodeRef = useRef<any>(null);
  const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "";

  // Check saved PIN on load
  useEffect(() => {
    const savedPin = localStorage.getItem("coordinator_pin");
    if (savedPin) {
      verifyPin(savedPin);
    }
  }, []);

  const verifyPin = async (pinCode: string) => {
    setLoadingStats(true);
    setAuthError("");
    try {
      const res = await fetch(`${backendUrl}/api/attendance/stats?pin=${pinCode}`);
      if (res.ok) {
        const data = await res.json();
        setStats({ total: data.total_registrations, present: data.checked_in_count });
        setIsAuthenticated(true);
        localStorage.setItem("coordinator_pin", pinCode);
        setPin(pinCode);
      } else {
        setAuthError("Invalid Coordinator PIN.");
        localStorage.removeItem("coordinator_pin");
      }
    } catch {
      setAuthError("Failed to connect to backend server.");
    } finally {
      setLoadingStats(false);
    }
  };

  const handlePinSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!pin.trim()) return;
    verifyPin(pin);
  };

  const handleLogout = () => {
    stopScanner();
    localStorage.removeItem("coordinator_pin");
    setIsAuthenticated(false);
    setPin("");
  };

  const fetchStats = async () => {
    try {
      const res = await fetch(`${backendUrl}/api/attendance/stats?pin=${pin}`);
      if (res.ok) {
        const data = await res.json();
        setStats({ total: data.total_registrations, present: data.checked_in_count });
      }
    } catch (e) {
      console.error("Failed to refresh stats:", e);
    }
  };

  // Start QR Camera Scanner
  const startScanner = async () => {
    setScannerError("");
    setScanResult(null);
    setScannerActive(true);

    try {
      // Dynamically import to avoid SSR errors
      const { Html5Qrcode } = await import("html5-qrcode");
      
      // Ensure element exists before initializing
      const readerElement = document.getElementById("reader");
      if (!readerElement) {
        setScannerError("Reader DOM element not found.");
        setScannerActive(false);
        return;
      }

      const html5QrCode = new Html5Qrcode("reader");
      html5QrCodeRef.current = html5QrCode;

      setScanning(true);
      await html5QrCode.start(
        { facingMode: "environment" },
        {
          fps: 10,
          qrbox: (width, height) => {
            const size = Math.min(width, height) * 0.7;
            return { width: size, height: size };
          }
        },
        async (decodedText) => {
          // Play positive sound immediately upon detection
          stopScanner();
          await processCheckIn(decodedText);
        },
        () => {
          // Silent failure for framing errors
        }
      );
    } catch (err: any) {
      console.error("Error starting camera scanner:", err);
      setScannerError(
        err.message || "Failed to start camera. Please verify camera permissions."
      );
      setScannerActive(false);
      setScanning(false);
    }
  };

  // Stop QR Camera Scanner
  const stopScanner = async () => {
    setScanning(false);
    if (html5QrCodeRef.current) {
      try {
        if (html5QrCodeRef.current.isScanning) {
          await html5QrCodeRef.current.stop();
        }
      } catch (e) {
        console.error("Error stopping scanner:", e);
      } finally {
        html5QrCodeRef.current = null;
        setScannerActive(false);
      }
    }
  };

  useEffect(() => {
    return () => {
      // Cleanup on unmount
      if (html5QrCodeRef.current && html5QrCodeRef.current.isScanning) {
        html5QrCodeRef.current.stop().catch((e: any) => console.error("Cleanup stop error:", e));
      }
    };
  }, []);

  const processCheckIn = async (registrationId: string) => {
    if (!registrationId.trim()) return;
    
    // Clear previous results
    setScanResult(null);
    
    try {
      const res = await fetch(`${backendUrl}/api/attendance/mark`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ registration_id: registrationId, pin }),
      });

      const data = await res.json();

      if (res.ok) {
        if (data.status === "success") {
          playAudioBeep("success");
          setScanResult({
            type: "success",
            message: data.message,
            student: data,
          });
          logAction(registrationId, data.full_name, "success", data.message);
        } else if (data.status === "already_marked") {
          playAudioBeep("warning");
          setScanResult({
            type: "already_marked",
            message: data.message,
            student: data,
          });
          logAction(registrationId, data.full_name, "already_marked", data.message);
        }
        fetchStats();
      } else {
        playAudioBeep("error");
        const errMsg = data.detail || "Verification failed.";
        setScanResult({
          type: "error",
          message: errMsg,
        });
        logAction(registrationId, "Unknown", "error", errMsg);
      }
    } catch {
      playAudioBeep("error");
      const networkMsg = "Network connection issue. Check backend server.";
      setScanResult({
        type: "error",
        message: networkMsg,
      });
      logAction(registrationId, "Unknown", "error", networkMsg);
    }
  };

  const handleManualCheckIn = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!manualId.trim() || manualLoading) return;

    setManualLoading(true);
    await processCheckIn(manualId);
    setManualId("");
    setManualLoading(false);
  };

  const logAction = (
    id: string,
    name: string,
    status: "success" | "already_marked" | "error",
    message: string
  ) => {
    const newLog: ScanLog = {
      timestamp: new Date().toLocaleTimeString(),
      registration_id: id,
      name,
      status,
      message,
    };
    setLogs((prev) => [newLog, ...prev.slice(0, 19)]);
  };

  // Auth screen
  if (!isAuthenticated) {
    return (
      <main className="min-h-screen bg-black flex flex-col items-center justify-center px-4 relative overflow-hidden">
        {/* Neon BG Accents */}
        <div className="absolute top-1/4 left-1/4 w-80 h-80 bg-[#FF5257]/10 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-[#985EFF]/10 rounded-full blur-3xl" />

        <motion.div 
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          className="w-full max-w-md bg-[#0c0c0e] border border-white/10 p-8 rounded-3xl shadow-2xl relative z-10 text-center"
        >
          <div className="w-16 h-16 mx-auto mb-6 bg-gradient-to-tr from-[#FF5257] to-[#985EFF] rounded-2xl flex items-center justify-center shadow-lg shadow-[#985EFF]/20">
            <Lock className="w-8 h-8 text-white" />
          </div>

          <h1 className="text-3xl font-bold tracking-tight text-white mb-2">Coordinator Access</h1>
          <p className="text-gray-400 text-sm mb-8">Enter the masterclass attendance PIN to enable QR camera check-ins.</p>

          <form onSubmit={handlePinSubmit} className="space-y-6">
            <div>
              <input
                type="password"
                placeholder="••••••"
                value={pin}
                onChange={(e) => setPin(e.target.value)}
                className="w-full text-center tracking-widest text-2xl font-bold bg-white/5 border border-white/10 rounded-2xl px-4 py-4 text-white focus:outline-none focus:border-[#985EFF] focus:ring-1 focus:ring-[#985EFF]/30 transition-all duration-200"
                maxLength={8}
                autoFocus
              />
            </div>

            {authError && (
              <div className="text-red-400 text-sm bg-red-500/10 border border-red-500/20 py-3 px-4 rounded-xl">
                {authError}
              </div>
            )}

            <button
              type="submit"
              disabled={loadingStats}
              className="w-full py-4 rounded-2xl font-semibold text-white bg-gradient-to-r from-[#FF5257] to-[#985EFF] hover:opacity-90 active:scale-98 transition-all duration-200 flex items-center justify-center gap-2 shadow-lg shadow-[#985EFF]/20 disabled:opacity-50"
            >
              {loadingStats ? (
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                "Authorize Session"
              )}
            </button>
          </form>
        </motion.div>
      </main>
    );
  }

  // Dashboard screen
  return (
    <main className="min-h-screen bg-[#060608] text-[#f5f5f7] flex flex-col relative pb-12">
      {/* Navbar */}
      <header className="border-b border-white/5 bg-black/40 backdrop-blur-md sticky top-0 z-50 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-tr from-[#FF5257] to-[#985EFF] rounded-xl flex items-center justify-center">
            <QrCode className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="font-bold text-lg leading-tight">Club Attendance</h1>
            <p className="text-xs text-gray-500 font-medium">Parul University Masterclass</p>
          </div>
        </div>
        
        <button 
          onClick={handleLogout}
          className="flex items-center gap-2 px-4 py-2 border border-white/10 hover:bg-white/5 active:scale-95 transition-all text-xs font-semibold rounded-xl text-gray-400 hover:text-white"
        >
          <LogOut className="w-4 h-4" />
          Exit Session
        </button>
      </header>

      {/* Main Container */}
      <div className="max-w-6xl w-full mx-auto px-4 md:px-6 mt-8 flex flex-col gap-8">
        
        {/* Real-time stats header card */}
        <section className="grid grid-cols-1 md:grid-cols-3 gap-6 bg-gradient-to-b from-[#111115] to-[#0c0c0f] border border-white/5 rounded-3xl p-6 relative overflow-hidden shadow-xl">
          <div className="absolute -right-16 -top-16 w-48 h-48 bg-[#985EFF]/5 rounded-full blur-3xl pointer-events-none" />
          
          <div className="md:col-span-2 flex flex-col justify-between">
            <div>
              <h2 className="text-xl font-bold text-white flex items-center gap-2">
                <Users className="w-5 h-5 text-[#985EFF]" />
                Live Checking Statistics
              </h2>
              <p className="text-gray-400 text-sm mt-1">Real-time attendance syncing directly with Google Sheets.</p>
            </div>
            
            {/* Progress bar */}
            <div className="mt-6 md:mt-0 pr-0 md:pr-8">
              <div className="flex justify-between text-sm mb-2 font-medium">
                <span className="text-gray-500">Check-in Completion</span>
                <span className="text-white">{stats.total > 0 ? Math.round((stats.present / stats.total) * 100) : 0}%</span>
              </div>
              <div className="w-full bg-white/5 h-2.5 rounded-full overflow-hidden border border-white/5">
                <motion.div 
                  className="bg-gradient-to-r from-[#FF5257] to-[#985EFF] h-full"
                  initial={{ width: 0 }}
                  animate={{ width: `${stats.total > 0 ? (stats.present / stats.total) * 100 : 0}%` }}
                  transition={{ duration: 0.8, ease: "easeOut" }}
                />
              </div>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4 border-t md:border-t-0 md:border-l border-white/5 pt-4 md:pt-0 md:pl-6">
            <div className="bg-white/[0.02] border border-white/5 p-4 rounded-2xl text-center">
              <span className="text-gray-500 text-xs uppercase tracking-wider font-semibold">Total Registered</span>
              <p className="text-3xl font-extrabold text-white mt-1">{stats.total}</p>
            </div>
            <div className="bg-white/[0.02] border border-white/5 p-4 rounded-2xl text-center shadow-[inset_0_0_15px_rgba(152,94,255,0.05)]">
              <span className="text-[#985EFF] text-xs uppercase tracking-wider font-semibold">Checked In</span>
              <p className="text-3xl font-extrabold text-[#985EFF] mt-1 flex justify-center items-center gap-1.5">
                {stats.present}
                <button 
                  onClick={fetchStats} 
                  className="p-1 hover:bg-white/5 rounded-lg active:scale-90 transition-all"
                  title="Refresh stats"
                >
                  <RefreshCw className="w-4 h-4 text-gray-500 hover:text-white" />
                </button>
              </p>
            </div>
          </div>
        </section>

        {/* Dashboard Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          
          {/* Scanner column */}
          <section className="lg:col-span-7 flex flex-col gap-6">
            
            {/* QR Camera Card */}
            <div className="bg-[#0c0c0f] border border-white/5 rounded-3xl p-6 flex flex-col shadow-xl overflow-hidden relative">
              <h3 className="font-semibold text-lg text-white mb-4 flex items-center gap-2">
                <QrCode className="w-5 h-5 text-[#FF5257]" />
                Camera QR Scanner
              </h3>
              
              {/* Camera view-port */}
              <div className="aspect-square w-full max-w-md mx-auto bg-black rounded-2xl border border-white/10 overflow-hidden relative flex flex-col items-center justify-center">
                
                {/* Custom Overlay lines */}
                {scanning && (
                  <div className="absolute inset-0 pointer-events-none z-10 border-2 border-[#985EFF]/30 rounded-2xl overflow-hidden">
                    {/* Laser line animation */}
                    <div className="w-full h-1 bg-gradient-to-r from-transparent via-[#FF5257] to-transparent shadow-[0_0_12px_#FF5257] absolute top-0 animate-[scan_2.5s_linear_infinite]" />
                    
                    {/* Framing corners */}
                    <div className="absolute top-4 left-4 w-6 h-6 border-t-2 border-l-2 border-[#985EFF]" />
                    <div className="absolute top-4 right-4 w-6 h-6 border-t-2 border-r-2 border-[#985EFF]" />
                    <div className="absolute bottom-4 left-4 w-6 h-6 border-b-2 border-l-2 border-[#985EFF]" />
                    <div className="absolute bottom-4 right-4 w-6 h-6 border-b-2 border-r-2 border-[#985EFF]" />
                  </div>
                )}

                {/* html5-qrcode target container */}
                <div 
                  id="reader" 
                  className={`w-full h-full object-cover transition-opacity duration-300 ${scanning ? 'opacity-100' : 'opacity-0 absolute pointer-events-none'}`} 
                />

                {!scannerActive && (
                  <div className="flex flex-col items-center justify-center p-8 text-center text-gray-500 relative z-20">
                    <QrCode className="w-16 h-16 stroke-[1.2] mb-4 opacity-30 text-[#985EFF]" />
                    <p className="text-sm font-medium">Camera is currently inactive.</p>
                    <p className="text-xs mt-1 text-gray-600 max-w-xs">Activate camera stream to instantly scan student event passes.</p>
                    
                    <button
                      onClick={startScanner}
                      className="mt-6 px-6 py-3 bg-gradient-to-r from-[#FF5257] to-[#985EFF] hover:opacity-90 active:scale-95 transition-all text-sm font-semibold text-white rounded-xl flex items-center gap-2 shadow-lg shadow-[#985EFF]/10"
                    >
                      <Play className="w-4 h-4 fill-current" />
                      Initialize Camera
                    </button>
                  </div>
                )}

                {scannerActive && !scanning && (
                  <div className="text-center text-gray-500 py-6">
                    <p className="text-sm animate-pulse">Initializing camera stream...</p>
                  </div>
                )}

                {scannerError && (
                  <div className="absolute inset-0 bg-black/95 z-20 flex flex-col items-center justify-center p-6 text-center text-red-400">
                    <XCircle className="w-12 h-12 mb-3" />
                    <p className="font-semibold text-sm">Failed to open camera</p>
                    <p className="text-xs text-gray-500 max-w-xs mt-1 leading-relaxed">{scannerError}</p>
                    <button
                      onClick={startScanner}
                      className="mt-4 px-4 py-2 border border-red-500/30 bg-red-500/10 hover:bg-red-500/20 text-xs font-semibold rounded-lg transition-all"
                    >
                      Try Again
                    </button>
                  </div>
                )}
              </div>

              {/* Stop camera button */}
              {scanning && (
                <div className="mt-4 flex justify-center">
                  <button
                    onClick={stopScanner}
                    className="px-5 py-2.5 border border-red-500/20 bg-red-500/5 hover:bg-red-500/10 text-red-400 active:scale-95 text-xs font-semibold rounded-xl flex items-center gap-2 transition-all"
                  >
                    <Square className="w-3.5 h-3.5 fill-current" />
                    Stop Camera Feed
                  </button>
                </div>
              )}
            </div>

            {/* Manual Lookup Card */}
            <div className="bg-[#0c0c0f] border border-white/5 rounded-3xl p-6 shadow-xl relative">
              <h3 className="font-semibold text-base text-white mb-3 flex items-center gap-2">
                <Search className="w-4.5 h-4.5 text-gray-400" />
                Manual Attendance Override
              </h3>
              <p className="text-xs text-gray-500 mb-4">Fallback in case of camera permissions, cracked phone screens, or low lighting conditions.</p>
              
              <form onSubmit={handleManualCheckIn} className="flex gap-3">
                <div className="relative flex-1">
                  <input
                    type="text"
                    placeholder="Enter Registration ID (e.g. hash) or Enrollment"
                    value={manualId}
                    onChange={(e) => setManualId(e.target.value)}
                    className="w-full bg-white/5 border border-white/10 rounded-xl pl-4 pr-10 py-3 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-[#985EFF] transition-all"
                    disabled={manualLoading}
                  />
                  {manualLoading && (
                    <div className="absolute right-3 top-3.5 w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin" />
                  )}
                </div>
                <button
                  type="submit"
                  disabled={manualLoading || !manualId.trim()}
                  className="px-5 py-3 rounded-xl bg-white/10 hover:bg-white/20 active:scale-95 transition-all text-sm font-semibold text-white disabled:opacity-50"
                >
                  Verify
                </button>
              </form>
            </div>
          </section>

          {/* Feedback & Logs column */}
          <section className="lg:col-span-5 flex flex-col gap-6">
            
            {/* Live Scan Results Overlay */}
            <div className="bg-[#0c0c0f] border border-white/5 rounded-3xl p-6 shadow-xl flex flex-col min-h-[250px] relative justify-center overflow-hidden">
              <div className="absolute -left-16 -bottom-16 w-32 h-32 bg-[#FF5257]/5 rounded-full blur-3xl pointer-events-none" />
              
              <AnimatePresence mode="wait">
                {scanResult ? (
                  <motion.div
                    key={scanResult.message}
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.95 }}
                    className="w-full flex flex-col items-center text-center py-4"
                  >
                    {scanResult.type === "success" && (
                      <div className="w-16 h-16 rounded-full bg-green-500/10 border border-green-500/30 flex items-center justify-center text-green-400 mb-4 shadow-[0_0_20px_rgba(34,197,94,0.1)]">
                        <CheckCircle2 className="w-8 h-8" />
                      </div>
                    )}
                    {scanResult.type === "already_marked" && (
                      <div className="w-16 h-16 rounded-full bg-yellow-500/10 border border-yellow-500/30 flex items-center justify-center text-yellow-400 mb-4 shadow-[0_0_20px_rgba(234,179,8,0.1)]">
                        <AlertTriangle className="w-8 h-8" />
                      </div>
                    )}
                    {scanResult.type === "error" && (
                      <div className="w-16 h-16 rounded-full bg-red-500/10 border border-red-500/30 flex items-center justify-center text-red-400 mb-4 shadow-[0_0_20px_rgba(239,68,68,0.1)]">
                        <XCircle className="w-8 h-8" />
                      </div>
                    )}

                    <h4 className={`text-xl font-bold mb-1 ${scanResult.type === 'success' ? 'text-green-400' : scanResult.type === 'already_marked' ? 'text-yellow-400' : 'text-red-400'}`}>
                      {scanResult.type === "success" ? "Check-in Successful" : scanResult.type === "already_marked" ? "Duplicate Entry" : "Verification Failed"}
                    </h4>
                    <p className="text-gray-300 text-sm max-w-sm mb-6 leading-relaxed">{scanResult.message}</p>

                    {scanResult.student && (
                      <motion.div 
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="w-full bg-white/[0.02] border border-white/5 rounded-2xl p-4 text-left space-y-3 shadow-inner"
                      >
                        <div className="flex justify-between items-center pb-2 border-b border-white/5">
                          <span className="text-gray-500 text-xs font-semibold uppercase">Attendee Profile</span>
                          <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${scanResult.student.has_mac === 'yes' ? 'bg-[#985EFF]/10 text-[#985EFF]' : 'bg-[#FF5257]/10 text-[#FF5257]'}`}>
                            {scanResult.student.has_mac === "yes" ? "BYOD Mac" : "Lab Machine"}
                          </span>
                        </div>
                        
                        <div className="grid grid-cols-2 gap-y-3 gap-x-2 text-sm">
                          <div>
                            <span className="text-gray-500 text-[10px] uppercase font-semibold">Full Name</span>
                            <p className="font-semibold text-white mt-0.5 leading-tight truncate">{scanResult.student.full_name}</p>
                          </div>
                          <div>
                            <span className="text-gray-500 text-[10px] uppercase font-semibold">Enrollment No</span>
                            <p className="font-mono text-gray-300 mt-0.5 leading-tight truncate">{scanResult.student.enrollment_no}</p>
                          </div>
                          <div>
                            <span className="text-gray-500 text-[10px] uppercase font-semibold">Semester</span>
                            <p className="text-gray-300 mt-0.5 leading-tight">{scanResult.student.semester}</p>
                          </div>
                          <div>
                            <span className="text-gray-500 text-[10px] uppercase font-semibold">Proficiency</span>
                            <p className="text-gray-300 mt-0.5 leading-tight">{scanResult.student.proficiency}</p>
                          </div>
                        </div>
                      </motion.div>
                    )}

                    {scannerActive && !scanning && (
                      <button
                        onClick={startScanner}
                        className="mt-6 px-4 py-2 text-xs font-semibold text-white bg-white/5 border border-white/10 rounded-xl hover:bg-white/10 transition-all"
                      >
                        Resume Camera Scanning
                      </button>
                    )}
                  </motion.div>
                ) : (
                  <div className="flex flex-col items-center justify-center p-8 text-center text-gray-500">
                    <Laptop className="w-12 h-12 stroke-[1.2] mb-3 opacity-30 text-[#985EFF]" />
                    <p className="text-sm font-semibold">Waiting for Scanned Pass</p>
                    <p className="text-xs text-gray-600 max-w-[240px] mt-1 leading-relaxed">Student details will pop up here instantly when a valid QR code is scanned or typed.</p>
                  </div>
                )}
              </AnimatePresence>
            </div>

            {/* Scan Logs Feed */}
            <div className="bg-[#0c0c0f] border border-white/5 rounded-3xl p-6 shadow-xl flex flex-col flex-1 max-h-[350px]">
              <h3 className="font-semibold text-base text-white mb-4 flex items-center justify-between">
                <span>Verification Logs</span>
                <span className="text-[10px] font-bold text-gray-600 uppercase tracking-widest bg-white/5 px-2.5 py-0.5 rounded-full">
                  Recent {logs.length}
                </span>
              </h3>

              <div className="overflow-y-auto pr-1 flex-1 flex flex-col gap-3 scrollbar-thin">
                {logs.length > 0 ? (
                  logs.map((log, index) => (
                    <div 
                      key={index} 
                      className="flex items-start justify-between p-3 rounded-xl bg-white/[0.02] border border-white/5 text-xs text-left"
                    >
                      <div className="flex gap-2.5 items-start">
                        {log.status === "success" && <div className="w-2 h-2 rounded-full bg-green-500 mt-1.5 flex-shrink-0" />}
                        {log.status === "already_marked" && <div className="w-2 h-2 rounded-full bg-yellow-500 mt-1.5 flex-shrink-0" />}
                        {log.status === "error" && <div className="w-2 h-2 rounded-full bg-red-500 mt-1.5 flex-shrink-0" />}
                        
                        <div>
                          <p className="font-bold text-gray-200">{log.name}</p>
                          <p className="text-[10px] text-gray-500 mt-0.5 font-medium">{log.message}</p>
                        </div>
                      </div>
                      <span className="text-[10px] font-semibold font-mono text-gray-600 flex-shrink-0 mt-0.5">{log.timestamp}</span>
                    </div>
                  ))
                ) : (
                  <div className="h-full flex flex-col items-center justify-center text-center text-gray-600 py-12">
                    <p className="text-xs">No scan events recorded in this session.</p>
                  </div>
                )}
              </div>
            </div>

          </section>

        </div>
      </div>
      
      {/* Scanner laser animation styling */}
      <style jsx global>{`
        @keyframes scan {
          0% {
            transform: translateY(0);
          }
          50% {
            transform: translateY(440px);
          }
          100% {
            transform: translateY(0);
          }
        }
      `}</style>
    </main>
  );
}
