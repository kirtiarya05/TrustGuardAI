import React, { useState, useEffect } from 'react';
import { Shield, ShieldAlert, Lock, Zap, Search, Fingerprint, Database, CheckCircle, Menu, Activity, TerminalSquare, AlertTriangle, AlertCircle, Share2, Download, Info } from 'lucide-react';

export default function App() {
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [logs, setLogs] = useState([]);

  const getThemeColor = (category) => {
    switch (category?.toLowerCase()) {
      case 'fake': return { text: 'text-red-500', bg: 'bg-red-500', border: 'border-red-500' };
      case 'suspicious': return { text: 'text-yellow-500', bg: 'bg-yellow-500', border: 'border-yellow-500' };
      case 'real': return { text: 'text-accent', bg: 'bg-accent', border: 'border-accent' };
      default: return { text: 'text-gray-500', bg: 'bg-gray-500', border: 'border-gray-500' };
    }
  };

  const handleAnalyze = async () => {
    if (!inputText.trim()) return;
    
    setLoading(true);
    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: inputText }),
      });
      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error("Analysis failed:", error);
      setResult({
        score: 0,
        category: "Error",
        explanation: "Neural connection failed. Please ensure the Threat Analysis Engine (backend) is running."
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0b0c10] text-gray-200 font-sans selection:bg-accent selection:text-black relative">
      <div className="absolute inset-0 pointer-events-none opacity-40 z-0">
        <div className="w-full h-full bg-animated-grid" style={{ maskImage: 'linear-gradient(to bottom, black 30%, transparent 100%)', WebkitMaskImage: 'linear-gradient(to bottom, black 30%, transparent 100%)' }}></div>
      </div>
      
      <div className="relative z-10 w-full">
      {/* Navigation Bar */}
      <nav className="flex items-center justify-between px-8 py-6 border-b border-white/5">
        <div className="flex items-center gap-3">
          <div className="bg-accent rounded-lg p-2 text-black shadow-[0_0_15px_rgba(0,255,136,0.3)]">
            <Shield size={24} className="fill-current" />
          </div>
          <span className="font-display font-bold text-xl tracking-widest text-white">TRUSTGUARD AI</span>
        </div>
        
        <div className="hidden md:flex items-center gap-8 text-sm font-semibold tracking-wider text-gray-400">
          <a href="#" className="hover:text-accent transition-colors">TECHNOLOGY</a>
          <a href="#" className="hover:text-accent transition-colors flex items-center gap-2">
            <TerminalSquare size={16} /> API
          </a>
          <button className="text-gray-300 hover:text-white transition-colors">
            <Menu size={24} />
          </button>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-6 pt-20 pb-32">
        
        {/* Hero Section */}
        <div className="flex flex-col items-center text-center space-y-6 mb-16 relative z-10">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-accent/30 bg-accent/5 text-accent text-xs font-mono font-semibold tracking-wider">
            <Zap size={14} className="fill-accent text-accent" />
            NEXT-GEN MISINFORMATION DEFENSE
          </div>
          
          <h1 className="text-5xl md:text-7xl font-display font-bold leading-tight tracking-tight text-white mb-4">
            VERIFY THE <span className="text-accent">TRUTH</span><br />
            IN REAL-TIME.
          </h1>
        </div>

        {/* Inference / Input Section */}
        <div className="max-w-4xl mx-auto mb-20 relative z-10">
          <div className={`rounded-xl transition-all duration-300 p-px ${inputText ? 'bg-gradient-to-r from-accent to-neon-blue' : 'bg-white/10 hover:bg-white/20'}`}>
            <div className="bg-[#121319] rounded-xl p-1 relative flex flex-col">
              <AnimatedTextarea 
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
              />
              
              <div className="absolute bottom-4 right-5 text-xs text-gray-600 font-mono">
                {inputText.length} characters
              </div>
            </div>
          </div>

          <button 
            onClick={handleAnalyze}
            disabled={loading || !inputText}
            className={`w-full mt-4 py-4 rounded-xl flex items-center justify-center gap-3 font-semibold text-lg tracking-wide transition-all shadow-[0_0_20px_rgba(0,255,136,0.15)]
              ${(!inputText || loading) ? 'bg-accent/40 text-black/50 cursor-not-allowed' : 'bg-accent text-black hover:bg-accent-dark hover:shadow-[0_0_25px_rgba(0,255,136,0.4)]'}`}
          >
            {loading ? (
              <Activity className="animate-spin" size={24} />
            ) : (
              <ShieldCheck size={24} />
            )}
            {loading ? 'ANALYZING NEURAL PATTERNS...' : 'CHECK TRUST SCORE'}
          </button>
          {/* Share / Export Buttons */}
          {result && !loading && (
            <div className="flex justify-end gap-3 mt-8 mb-2 animate-in fade-in duration-700 relative z-10 w-full max-w-2xl mx-auto">
              <button className="flex items-center gap-2 px-5 py-2.5 rounded-full border border-white/10 hover:border-white/30 bg-[#121318]/80 backdrop-blur-sm text-gray-300 text-xs font-semibold tracking-widest transition-all uppercase">
                <Share2 size={14} /> Share
              </button>
              <button className="flex items-center gap-2 px-5 py-2.5 rounded-full border border-white/10 hover:border-white/30 bg-[#121318]/80 backdrop-blur-sm text-gray-300 text-xs font-semibold tracking-widest transition-all uppercase">
                <Download size={14} /> Export PDF
              </button>
            </div>
          )}

          {/* Result Card Injection */}
          {result && !loading && (
             <div className="mt-4 animate-in slide-in-from-bottom-8 fade-in duration-700 relative z-10 flex justify-center w-full">
                {(() => {
                  const theme = getThemeColor(result.category);
                  return (
                    <div className={`w-full max-w-2xl border ${theme.border}/20 bg-[#0b0c10]/80 backdrop-blur-xl rounded-3xl p-8 md:p-12 relative overflow-hidden shadow-2xl shadow-black/50`}>
                       {/* Background Shield Logo */}
                       <Shield className={`absolute -right-10 -top-10 w-72 h-72 ${theme.text} opacity-5 transform rotate-12`} />
                       
                       <div className="flex flex-col items-center text-center relative z-10">
                         {/* Score Circular Indicator */}
                          <div className="relative flex items-center justify-center shrink-0 mb-8">
                             <svg className="w-40 h-40 transform -rotate-90 drop-shadow-xl">
                                <circle cx="80" cy="80" r="70" stroke="currentColor" strokeWidth="12" fill="none" className="text-[#1a1b23]" />
                                <circle cx="80" cy="80" r="70" stroke="currentColor" strokeWidth="12" fill="none" strokeLinecap="round" strokeDasharray="439.8" strokeDashoffset={439.8 - (439.8 * result.score) / 100} className={`${theme.text} transition-all duration-[2000ms] ease-out`} />
                             </svg>
                             <div className="absolute flex flex-col items-center justify-center text-white">
                               <AnimatedCounter value={result.score} className="text-5xl font-display font-bold leading-none" />
                               <span className="text-xs font-mono font-semibold uppercase tracking-widest mt-2 text-gray-400">Score</span>
                             </div>
                          </div>

                          <div className="space-y-6 w-full">
                            <div className="flex items-center justify-center gap-3">
                               {result.category.toLowerCase() === 'fake' ? <AlertCircle className={theme.text} size={36} /> : 
                                result.category.toLowerCase() === 'suspicious' ? <AlertTriangle className={theme.text} size={36} /> : 
                                <CheckCircle className={theme.text} size={36} />}
                               <h2 className={`text-4xl font-display font-black tracking-widest uppercase ${theme.text}`}>
                                 {result.category}
                               </h2>
                            </div>
                            
                            <div className="text-left mt-8 w-full border border-white/5 bg-[#14151a]/50 p-6 rounded-2xl">
                              <div className="flex items-center gap-2 mb-4">
                                <Info size={16} className="text-accent" />
                                <span className="font-mono text-sm font-semibold tracking-widest text-gray-400">AI ANALYSIS REPORT</span>
                              </div>
                              <p className="text-gray-300 text-lg md:text-xl leading-relaxed italic pr-4">
                                "{result.explanation}"
                              </p>
                            </div>
                          </div>
                       </div>
                    </div>
                  );
                })()}
             </div>
          )}
        </div>

        {/* Feature Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-32 max-w-5xl mx-auto">
          <FeatureCard 
            icon={<Search className="text-accent" size={24} />}
            title="Deep Analysis"
            desc="Our NLP models scan for linguistic manipulation, logical fallacies, and emotional triggers."
          />
          <FeatureCard 
            icon={<Lock className="text-[#a855f7]" size={24} />}
            title="Privacy First"
            desc="Your queries are processed anonymously and never stored. We prioritize data sovereignty."
          />
          <FeatureCard 
            icon={<Shield className="text-accent" size={24} />}
            title="Source Check"
            desc="Cross-references content against a global database of 50,000+ verified news sources."
          />
        </div>

        {/* Threat Monitor UI */}
        <div className="max-w-5xl mx-auto">
          <div className="rounded-2xl border border-white/5 bg-[#121318] p-6 lg:p-8">
             <div className="flex items-center justify-between mb-8 border-b border-white/5 pb-4">
               <div className="flex items-center gap-3">
                 <Activity className="text-accent animate-pulse" size={20} />
                 <h3 className="font-mono text-sm tracking-widest text-gray-400 font-semibold">GLOBAL THREAT MONITOR</h3>
               </div>
               <div className="flex items-center gap-2 text-xs font-mono text-gray-500">
                 <div className="w-2 h-2 rounded-full bg-accent animate-ping"></div>
                 LIVE FEED
               </div>
             </div>

             <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <ThreatItem city="London, UK" threat="Deepfake Audio" level="High" color="text-yellow-500" bg="bg-yellow-500" />
                <ThreatItem city="New York, US" threat="Phishing Campaign" level="Critical" color="text-red-500" bg="bg-red-500" />
                <ThreatItem city="Tokyo, JP" threat="Bot Network" level="Medium" color="text-accent" bg="bg-accent" />
                <ThreatItem city="Berlin, DE" threat="Fake News Surge" level="High" color="text-yellow-500" bg="bg-yellow-500" />
             </div>
          </div>
        </div>

      </main>

      <footer className="text-center py-10 text-gray-600 font-mono text-xs tracking-widest border-t border-white/5">
        &copy; 2026 TRUSTGUARD AI SYSTEMS • NEURAL DEFENSE PROTOCOL V1.0.4
      </footer>
      </div>
    </div>
  );
}

function AnimatedCounter({ value, className }) {
  const [count, setCount] = React.useState(0);

  React.useEffect(() => {
    let start = 0;
    const end = parseInt(value) || 0;
    if (start === end) {
      setCount(end);
      return;
    }
    
    let totalDuration = 1500;
    let incrementTime = Math.max(10, totalDuration / end);
    
    let timer = setInterval(() => {
      start += 1;
      setCount(start);
      if (start >= end) {
        clearInterval(timer);
        setCount(end);
      }
    }, incrementTime);
    
    return () => clearInterval(timer);
  }, [value]);

  return <span className={className}>{count}</span>;
}

function AnimatedTextarea({ value, onChange }) {
  const [placeholder, setPlaceholder] = useState('');
  const [isFocused, setIsFocused] = useState(false);
  const text = "Paste news article, social media post, or suspicious message here to verify truth patterns...";
  
  useEffect(() => {
    if (isFocused || value) {
      setPlaceholder('');
      return;
    }
    
    let currentIndex = 0;
    const interval = setInterval(() => {
      if (currentIndex <= text.length) {
        setPlaceholder(text.slice(0, currentIndex) + (currentIndex % 2 === 0 ? '|' : ''));
        currentIndex++;
      } else {
        clearInterval(interval);
      }
    }, 40);
    
    return () => clearInterval(interval);
  }, [isFocused, value]);

  return (
    <textarea
      className="w-full h-48 bg-transparent text-gray-200 p-5 outline-none resize-none font-sans text-lg placeholder:text-gray-500"
      placeholder={placeholder}
      value={value}
      onChange={onChange}
      onFocus={() => setIsFocused(true)}
      onBlur={() => setIsFocused(false)}
    ></textarea>
  );
}

function ShieldCheck({ size }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
      <path d="M9 12l2 2 4-4"/>
    </svg>
  );
}

function FeatureCard({ icon, title, desc }) {
  return (
    <div className="bg-[#14151a] border border-white/5 rounded-2xl p-8 hover:border-accent/30 transition-colors duration-300 text-left">
      <div className="bg-dark border border-white/5 w-14 h-14 rounded-xl flex items-center justify-center mb-6 shadow-sm">
        {icon}
      </div>
      <h3 className="text-white font-display font-bold text-xl mb-3 tracking-wide">{title}</h3>
      <p className="text-gray-400 leading-relaxed text-sm">
        {desc}
      </p>
    </div>
  );
}

function ThreatItem({ city, threat, level, color, bg }) {
  return (
    <div className="bg-[#0b0c10] border border-white/5 rounded-xl p-4 hover:border-white/10 transition-colors">
      <div className="flex justify-between items-start mb-4">
        <span className="text-[10px] text-gray-500 font-mono tracking-wider uppercase">{city}</span>
        <Activity size={12} className="text-accent" />
      </div>
      <div className="text-white font-semibold text-md mb-2">{threat}</div>
      <div className={`flex items-center gap-2 text-[10px] font-mono font-bold uppercase tracking-widest ${color}`}>
        <div className={`w-1.5 h-1.5 rounded-full ${bg}`}></div>
        {level} RISK
      </div>
    </div>
  );
}
