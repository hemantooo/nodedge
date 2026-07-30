import Image from 'next/image';

export default function Header() {
  return (
    <header className="fixed top-0 left-0 right-0 z-50 flex items-center justify-center p-3">
      <nav className="flex items-center gap-3 sm:gap-6 px-4 sm:px-8 py-2.5 bg-white/5 backdrop-blur-xl border border-white/10 rounded-full shadow-2xl">

        {/* Parul University — pure SVG, white paths, render crisply */}
        <div className="flex items-center h-8">
          <Image
            src="/images/parul_logo.svg"
            alt="Parul University"
            width={117}
            height={36}
            className="h-8 w-auto object-contain"
            priority
          />
        </div>

        <div className="w-px h-5 bg-white/20" />

        {/* AACTE */}
        <div className="flex items-center h-9 overflow-hidden" style={{ isolation: 'isolate' }}>
          <Image
            src="/images/aatce_logo.svg"
            alt="AACTE"
            width={126}
            height={40}
            className="h-9 w-auto object-contain"
            style={{ transform: 'translateZ(0)', willChange: 'transform' }}
            unoptimized
            priority
          />
        </div>

        <div className="w-px h-5 bg-white/20" />

        {/* Swift logo */}
        <div className="flex items-center h-8">
          <Image
            src="/images/Swift_logo.svg"
            alt="Swift Coding Club"
            width={34}
            height={34}
            className="h-8 w-auto object-contain"
            priority
          />
        </div>

      </nav>
    </header>
  );
}
