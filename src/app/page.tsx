import Header from "@/components/Header";
import Hero from "@/components/Hero";
import Curriculum from "@/components/Curriculum";
import RegistrationForm from "@/components/RegistrationForm";

export default function Home() {
  return (
    <main className="min-h-screen bg-black">
      <Header />
      <Hero />

      {/* Divider */}
      <div className="w-full h-px bg-gradient-to-r from-transparent via-white/10 to-transparent" />

      <Curriculum />

      {/* Divider */}
      <div className="w-full h-px bg-gradient-to-r from-transparent via-white/10 to-transparent" />

      <RegistrationForm />

      {/* Footer */}
      <footer className="py-8 text-center text-gray-600 text-sm border-t border-white/5">
        <p>© 2025 Swift Coding Club · Parul University · Apple AATEC</p>
      </footer>
    </main>
  );
}
