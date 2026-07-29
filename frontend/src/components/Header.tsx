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

        {/* Tinkering Hub */}
        <div className="flex items-center h-8 overflow-hidden">
          <img
            src="/images/thub_logo.svg"
            alt="Tinkering Hub"
            width={832}
            height={264}
            style={{
              height: '32px',
              width: 'auto',
              objectFit: 'contain',
              imageRendering: 'auto',
            }}
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
