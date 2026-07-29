"use client";

import { motion } from 'framer-motion';
import { BookOpen, Code2, MonitorPlay } from 'lucide-react';

const days = [
  {
    day: 1,
    title: "Swift Core Foundations",
    icon: BookOpen,
    color: "from-[#FF5257]/20 to-transparent",
    border: "group-hover:border-[#FF5257]/50",
    topics: [
      "Swift Core Syntax & Data Types",
      "Optionals & Error Handling",
      "Structs vs Classes",
      "Closures & Higher Order Functions",
      "Protocols & Extensions",
      "Async/Await Concurrency"
    ]
  },
  {
    day: 2,
    title: "Declarative UI with SwiftUI",
    icon: Code2,
    color: "from-[#985EFF]/20 to-transparent",
    border: "group-hover:border-[#985EFF]/50",
    topics: [
      "Introduction to Declarative UI",
      "View Hierarchy & Modifiers",
      "State Management (@State, @Binding)",
      "Custom Animations & Transitions",
      "Layout Engines (VStack, HStack, ZStack)"
    ]
  },
  {
    day: 3,
    title: "Native App Building",
    icon: MonitorPlay,
    color: "from-blue-500/20 to-transparent",
    border: "group-hover:border-blue-500/50",
    topics: [
      "Xcode Environment Setup",
      "App Architecture Patterns",
      "Navigation & Data Flow",
      "Live Hands-On Demo",
      "Q&A and Next Steps"
    ]
  }
];

export default function Curriculum() {
  return (
    <section className="py-24 px-4 relative z-10">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-5xl font-bold mb-4">Workshop Curriculum</h2>
          <p className="text-gray-400 max-w-2xl mx-auto">Three days of intensive, hands-on learning designed to take you from absolute beginner to building your first native iOS application.</p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {days.map((day, index) => (
            <motion.div
              key={day.day}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.2 }}
              className={`group relative p-8 rounded-3xl bg-white/5 backdrop-blur-xl border border-white/10 ${day.border} transition-colors duration-300 overflow-hidden`}
            >
              <div className={`absolute inset-0 bg-gradient-to-b ${day.color} opacity-0 group-hover:opacity-100 transition-opacity duration-500`} />
              
              <div className="relative z-10">
                <div className="w-14 h-14 rounded-2xl bg-white/10 flex items-center justify-center mb-6">
                  <day.icon className="w-7 h-7 text-white" />
                </div>
                
                <h3 className="text-2xl font-bold mb-2">Day {day.day}</h3>
                <h4 className="text-lg text-gray-300 mb-6 min-h-[56px]">{day.title}</h4>
                
                <ul className="space-y-3">
                  {day.topics.map((topic, i) => (
                    <li key={i} className="flex items-start text-sm text-gray-400">
                      <span className="mr-3 text-white/50">•</span>
                      {topic}
                    </li>
                  ))}
                </ul>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
