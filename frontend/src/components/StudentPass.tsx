"use client";

import { motion } from 'framer-motion';
import QRCode from 'react-qr-code';

interface PassProps {
  data: {
    full_name: string;
    enrollment_no: string;
    has_mac: string;
    registration_id: string;
  };
}

export default function StudentPass({ data }: PassProps) {
  return (
    <section className="py-24 px-4 relative z-10 flex justify-center items-center min-h-[80vh]">
      <motion.div 
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="w-full max-w-sm bg-black border border-white/20 rounded-3xl overflow-hidden shadow-[0_0_50px_rgba(152,94,255,0.2)] relative"
      >
        <div className="bg-gradient-to-r from-[#FF5257] to-[#985EFF] p-6 text-white text-center relative overflow-hidden">
          <div className="absolute inset-0 bg-black/20" />
          <div className="relative z-10">
            <h3 className="font-semibold tracking-widest uppercase text-xs opacity-90 mb-1">Parul University</h3>
            <h2 className="text-2xl font-bold">Event Pass</h2>
          </div>
        </div>

        <div className="p-8 pb-12 flex flex-col items-center">
          <div className="w-full mb-8">
            <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">Attendee</p>
            <p className="text-xl font-medium text-white">{data.full_name}</p>
          </div>

          <div className="w-full flex justify-between mb-8 pb-8 border-b border-white/10">
            <div>
              <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">Enrollment</p>
              <p className="font-mono text-gray-300">{data.enrollment_no}</p>
            </div>
            <div className="text-right">
              <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">Mac Status</p>
              <p className="text-gray-300">{data.has_mac === 'yes' ? 'BYOD' : 'Lab Required'}</p>
            </div>
          </div>

          <div className="bg-white p-4 rounded-xl shadow-inner mb-4">
            <QRCode 
              value={data.registration_id}
              size={180}
              level="H"
              className="mx-auto"
            />
          </div>
          <p className="text-xs text-gray-600 font-mono mt-2">{data.registration_id}</p>
        </div>
      </motion.div>
    </section>
  );
}
