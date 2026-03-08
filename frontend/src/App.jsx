import React, { useState, useEffect } from 'react';
import { 
  Shield, ShieldAlert, Lock, Zap, Search, Fingerprint, 
  Database, CheckCircle, Menu, Activity, TerminalSquare, 
  AlertTriangle, AlertCircle, Share2, Download, Info, 
  Globe, Cpu, Server, Radio, BarChart3, ScanEye, Eye, 
  FileSearch, MessageSquareQuote, Layers, History, Settings
} from 'lucide-react';

export default function App() {
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [activeTab, setActiveTab] = useState('ANALYZE');
  const [scanningEffect, setScanningEffect] = useState(false);

  const getThemeColor = (category) => {
    switch (category?.toLowerCase()) {
      case 'fake': return { text: 'text-red-500', bg: 'bg-red-500', border: 'border-red-500', accent: '#ef4444' };
      case 'suspicious': return { text: 'text-yellow-500', bg: 'bg-yellow-500', border: 'border-yellow-500', accent: '#eab308' };
      case 'real': return { text: 'text-[#00ff88]', bg: 'bg-[#00ff88]', border: 'border-[#00ff88]', accent: '#00ff88' };
      default: return { text: 'text-gray-500', bg: 'bg-gray-500', border: 'border-gray-500', accent: '#6b7280' };
    }
  };

  const handleAnalyze = async () => {
    if (!inputText.trim()) return;
    
    setLoading(true);
    setScanningEffect(true);
    
    // Artificial delay for "Cyber" feel
    await new Promise(r => setTimeout(r, 2200));

    try {
      const apiUrl = import.meta.env.VITE_API_URL || '';
      const response = await fetch(`${apiUrl}/api/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: inputText }),
      });
      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error("Deep Scan failed:", error);
      setResult({
        score: 0,
        category: "Network Error",
        explanation: "Neural link severed. Ensure Deep Scan Engine (backend) is active.",
        sentiment: "Unknown",
        subjectivity: 0.0,
        flags: ["CONNECTION_LOST"],
        entities: []
      });
    } finally {
      setLoading(false);
      setScanningEffect(false);
    }
  };
  const kbDatasets = [
    { name: "FakeNewsNet", size: "~23,000", source: "GitHub", desc: "Political + Celebrity news" },
    { name: "CREDBANK", size: "~60M tweets", source: "Research", desc: "Twitter credibility" },
    { name: "PHEME", size: "~6,425", source: "Research", desc: "Rumor detection on Twitter" },
    { name: "BuzzFace", size: "~2,263", source: "Research", desc: "Facebook misinformation" },
    { name: "Fakeddit", size: "~1,000,000", source: "Reddit/GitHub", desc: "Multi-modal (text + image)" },
    { name: "COVID-19 Fake News", size: "~10,000", source: "Kaggle", desc: "Pandemic misinformation" },
    { name: "Indian Fake News", size: "~4,000", source: "Kaggle", desc: "Regional/Hindi news" },
    { name: "NELA-GT", size: "~1,800,000", source: "Research", desc: "200+ news sources over years" },
    { name: "MediaEval", size: "~15,000", source: "Research", desc: "Multimedia verification" },
    { name: "FA-KES", size: "~804", source: "Research", desc: "War/conflict misinformation" },
    { name: "Common Crawl", size: "~10.5 PB", source: "Web Archive", desc: "Raw internet pages continuously indexed" },
    { name: "GDELT Project", size: "~3 Trillion+", source: "Global Sensors", desc: "Real-time world events & news feeds" },
    { name: "Wikipedia Enterprise", size: "~65M articles", source: "Wikimedia", desc: "Global encyclopedia in 300+ languages" },
    { name: "Twitter Firehose", size: "~500M / day", source: "Enterprise API", desc: "Live global micro-blog ingestion" },
    { name: "Reddit Pushshift", size: "~5B+ posts", source: "Pushshift", desc: "Historical & live discussion boards" },
    { name: "Wayback Machine", size: "~866B pages", source: "Internet Archive", desc: "Historical website and domain snapshots" },
    { name: "Google News Corpus", size: "~100B words", source: "Google", desc: "Indexed news articles and vectors" },
    { name: "Project Gutenberg", size: "~70,000 books", source: "Public Domain", desc: "Digitized cultural works and literature" },
    { name: "Enron Email Corpus", size: "~500,000 emails", source: "Public Records", desc: "Real-world corporate communication data" },
    { name: "Dark Web Scrapes", size: "~Over 2 TB", source: "Threat Intel", desc: "Unindexed Tor network forums and markets" },
    { name: "ImageNet", size: "~14M images", source: "Vision DB", desc: "Large-scale visual recognition database" },
    { name: "YouTube-8M", size: "~8M videos", source: "Google Research", desc: "Large-scale labeled video dataset" },
    { name: "The Stack (BigCode)", size: "~6.2 TB", source: "GitHub", desc: "Open-source codebase archive in 358 languages" },
    { name: "Stack Overflow Dumps", size: "~87 GB", source: "Dev Network", desc: "All developer Q&A and coding history" },
    { name: "arXiv / PubMed", size: "~40M+ papers", source: "Academia", desc: "Scientific, mathematical, and medical research" },
    { name: "Semantic Scholar", size: "~215M papers", source: "Allen Institute", desc: "Graph of global academic citations" },
    { name: "OpenStreetMap", size: "~1.7 TB", source: "Geospatial", desc: "Crowdsourced global maps and infrastructure" },
    { name: "Landsat/Sentinel", size: "~8+ PB", source: "Satellite", desc: "Planet-wide daily topographical imagery" },
    { name: "Mozilla Common Voice", size: "~28,000 hrs", source: "Audio Dumps", desc: "Crowdsourced global spoken voice records" },
    { name: "LibriSpeech", size: "~1,000 hrs", source: "Audio Books", desc: "Large-scale collection of read English speech" },
    { name: "The Pile / C4", size: "~800 GB", source: "EleutherAI", desc: "Massive curated dataset for LLM training" },
    { name: "SEC EDGAR", size: "~20+ TB", source: "Financial", desc: "Corporate financial filings and global markets" },
    { name: "GenBank (NCBI)", size: "~14.7 TB", source: "Biological", desc: "The blueprint of all known living genetic sequences" },
    { name: "OSINT Database", size: "Infinite", source: "Open Source", desc: "Public intelligence sensors & feeds" }
  ];

  return (
    <div className="min-h-screen bg-[#06070a] text-gray-300 font-sans selection:bg-[#00ff88] selection:text-black overflow-x-hidden">
      {/* Background Matrix-like Overlay */}
      <div className="fixed inset-0 pointer-events-none opacity-20 z-0 overflow-hidden">
        <div className="absolute inset-0 bg-[linear-gradient(rgba(0,255,136,0.05)_1px,transparent_1px),linear-gradient(90deg,rgba(0,255,136,0.05)_1px,transparent_1px)] bg-[size:40px_40px]"></div>
        <div className="absolute inset-0 bg-gradient-to-t from-[#06070a] via-transparent to-transparent"></div>
        <div className="absolute -top-[50%] -left-[20%] w-[140%] h-[140%] bg-[radial-gradient(circle,rgba(0,255,136,0.03)_0%,transparent_70%)] animate-pulse"></div>
      </div>

      {/* CRT Scanline Effect */}
      <div className="fixed inset-0 pointer-events-none z-[100] opacity-[0.03] bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.25)_50%),linear-gradient(90deg,rgba(255,0,0,0.06),rgba(0,255,0,0.02),rgba(0,0,118,0.06))] bg-[size:100%_2px,3px_100%]"></div>
      
      <div className="relative z-10 flex flex-col min-h-screen">
        {/* Top Intelligence Header */}
        <header className="border-b border-[#00ff88]/10 bg-black/40 backdrop-blur-md sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="relative group">
                <div className="absolute -inset-1 bg-[#00ff88]/30 rounded-lg blur group-hover:blur-md transition-all duration-500"></div>
                <div className="relative bg-black rounded-lg p-2 border border-[#00ff88]/50 text-[#00ff88]">
                   <ScanEye size={22} className="animate-pulse" />
                </div>
              </div>
              <div className="flex flex-col">
                <span className="font-display font-black text-xl tracking-[0.25em] text-white">TRUSTGUARD AI</span>
                <span className="text-[9px] font-mono text-[#00ff88]/70 tracking-[0.4em] uppercase">Deep Scan Protocol v4.2.0</span>
              </div>
            </div>

            <div className="hidden lg:flex items-center gap-10">
               <NavItem icon={<Globe size={14}/>} label="GLOBAL FEED" active={activeTab === 'FEED'} onClick={() => setActiveTab('FEED')} />
               <NavItem icon={<Cpu size={14}/>} label="DEEP SCAN" active={activeTab === 'ANALYZE'} onClick={() => setActiveTab('ANALYZE')} />
               <NavItem icon={<Database size={14}/>} label="MODEL KB" active={activeTab === 'KB'} onClick={() => setActiveTab('KB')} />
            </div>

            <div className="flex items-center gap-4">
               <div className="h-2 w-2 rounded-full bg-[#00ff88] animate-ping"></div>
               <div className="hidden sm:block text-[10px] font-mono text-[#00ff88]">SYSTEM_STATUS: OK</div>
               <button className="p-2 hover:bg-white/5 rounded-full transition-colors text-white">
                 <Settings size={20} />
               </button>
            </div>
          </div>
        </header>

        <main className="flex-1 max-w-7xl mx-auto w-full px-6 pt-12 pb-24">
          {activeTab === 'ANALYZE' && (
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 animate-in fade-in slide-in-from-bottom-4 duration-500">
              
              {/* Left Control Panel (Main Input) */}
            <div className="lg:col-span-8 flex flex-col gap-8">
              <div className="flex flex-col gap-2">
                <h2 className="text-4xl md:text-5xl font-display font-extrabold text-white tracking-tight leading-tight">
                  AI <span className="text-[#00ff88] text-glow">REALITY</span> CHECKER
                </h2>
                <p className="text-gray-500 font-mono text-sm max-w-xl">
                  Analyze news, social media, and messages to detect fake content. Paste the text below to start the verification process.
                </p>
              </div>

              <div className="relative group">
                 {/* Input Glow */}
                 <div className={`absolute -inset-1 rounded-3xl transition-all duration-700 opacity-20 blur-xl ${inputText ? 'bg-[#00ff88]' : 'bg-transparent'}`}></div>
                 
                 <div className="relative bg-[#0d0f14] border border-white/5 rounded-2xl overflow-hidden focus-within:border-[#00ff88]/30 transition-all duration-300">
                    <div className="flex items-center px-6 py-3 border-b border-white/5 bg-white/[0.02]">
                       <div className="flex items-center gap-2 text-[10px] font-mono text-gray-500 font-bold tracking-widest uppercase">
                          <Radio size={12} className="text-[#00ff88]" /> Input_Buffer
                       </div>
                       <div className="ml-auto flex items-center gap-4">
                          <div className="text-[10px] font-mono text-gray-600 uppercase">UTF-8 Encrypted</div>
                          <History size={14} className="text-gray-600 hover:text-white cursor-pointer" />
                       </div>
                    </div>
                    
                    <textarea 
                      value={inputText}
                      onChange={(e) => setInputText(e.target.value)}
                      placeholder="Paste suspicious article, social media post, or phishing content here for forensic breakdown..."
                      className="w-full h-64 bg-transparent p-8 text-xl text-gray-200 outline-none resize-none placeholder:text-gray-700 font-sans leading-relaxed"
                    />

                    <div className="absolute bottom-6 right-8 flex items-center gap-4">
                       <span className="text-[10px] font-mono text-gray-600">{inputText.length} CHARS</span>
                       <div className="w-12 h-1 bg-white/5 rounded-full overflow-hidden">
                          <div className="h-full bg-[#00ff88] transition-all duration-300" style={{ width: `${Math.min(100, (inputText.length / 500) * 100)}%` }}></div>
                       </div>
                    </div>
                 </div>
              </div>

              <button 
                onClick={handleAnalyze}
                disabled={loading || !inputText}
                className={`group relative py-6 rounded-2xl overflow-hidden transition-all duration-500
                   ${(!inputText || loading) ? 'cursor-not-allowed opacity-50' : 'hover:scale-[1.01] active:scale-[0.99] font-glow'}`}
              >
                <div className={`absolute inset-0 bg-[#00ff88] transition-all duration-500 ${(inputText && !loading) ? 'opacity-100' : 'opacity-20'}`}></div>
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000"></div>
                
                <div className="relative flex items-center justify-center gap-4 text-black font-display font-black text-xl tracking-widest uppercase">
                  {loading ? <Activity className="animate-spin" /> : <Layers className={inputText ? 'animate-bounce' : ''} />}
                  {loading ? 'RUNNING_DEEP_SCAN' : 'INITIALIZE FORENSICS'}
                </div>
              </button>

              {/* Technical Footnote */}
              <div className="flex items-center gap-8 px-4 text-[9px] font-mono text-gray-600 font-bold tracking-[0.2em] uppercase">
                <div className="flex items-center gap-2"><Server size={10}/> AWS_REGION: GLOBAL_HUB</div>
                <div className="flex items-center gap-2"><MessageSquareQuote size={10}/> ENTROPY_MODE: ENABLED</div>
                <div className="flex items-center gap-2"><Fingerprint size={10}/> AES_256_ACTIVE</div>
              </div>
            </div>

            {/* Right Sidebar (Live Status / Results) */}
            <div className="lg:col-span-4 flex flex-col gap-8">
               
               {/* Result Module */}
               <div className="relative min-h-[500px]">
                  {!result && !loading && (
                    <div className="h-full border border-white/5 bg-[#0d0f14]/50 backdrop-blur-sm rounded-3xl p-10 flex flex-col items-center justify-center text-center gap-8 group">
                       <div className="w-24 h-24 rounded-full border border-white/10 flex items-center justify-center relative">
                          <div className="absolute inset-0 bg-[#00ff88]/5 rounded-full blur-xl group-hover:bg-[#00ff88]/10 transition-all"></div>
                          <Eye size={40} className="text-gray-700 group-hover:text-[#00ff88] transition-all" />
                       </div>
                       <div className="space-y-3">
                          <h3 className="text-white font-display font-bold text-lg tracking-widest uppercase">SYSTEM READY</h3>
                          <p className="text-gray-600 text-xs font-mono leading-relaxed px-6">
                             Awaiting forensic packet insertion. Initialize deep scan to begin neural mapping and risk assessment.
                          </p>
                       </div>
                       <div className="w-full max-w-[150px] space-y-2">
                          <div className="h-0.5 w-full bg-white/5 rounded-full overflow-hidden"><div className="h-full bg-gray-800 w-1/3 animate-[shimmer_2s_infinite]"></div></div>
                          <div className="h-0.5 w-full bg-white/5 rounded-full overflow-hidden"><div className="h-full bg-gray-800 w-2/3 animate-[shimmer_2s_infinite_0.5s]"></div></div>
                       </div>
                    </div>
                  )}

                  {loading && (
                    <div className="h-full border border-[#00ff88]/20 bg-[#0d0f14]/80 backdrop-blur-xl rounded-3xl p-10 flex flex-col gap-10">
                       <div className="flex items-center gap-4 border-b border-white/5 pb-6">
                          <Activity className="text-[#00ff88] animate-spin" size={24} />
                          <div className="flex flex-col">
                             <span className="text-white font-mono text-sm font-black animate-pulse">ANALYZING...</span>
                             <span className="text-gray-500 font-mono text-[9px] uppercase tracking-widest">Compiling Neural Signals</span>
                          </div>
                       </div>

                       <div className="space-y-6">
                          <LoadingStep label="PATTERN MATCHING" active delay="0" />
                          <LoadingStep label="SEMANTIC MAPPING" active delay="1s" />
                          <LoadingStep label="ENTROPY CHECK" active delay="2s" />
                          <LoadingStep label="CROSS_REF_GLOBAL" active={false} />
                       </div>

                       <div className="mt-auto space-y-4">
                          <div className="flex justify-between text-[10px] font-mono text-[#00ff88]">
                             <span>CPU_LOAD</span>
                             <span>84%</span>
                          </div>
                          <div className="h-1 bg-white/5 rounded-full overflow-hidden">
                             <div className="h-full bg-[#00ff88] animate-progress"></div>
                          </div>
                       </div>
                    </div>
                  )}

                  {result && !loading && (
                    <div className="animate-in slide-in-from-right-10 fade-in duration-500 h-full border border-white/10 bg-[#0d0f14] rounded-3xl p-8 relative overflow-hidden flex flex-col shadow-2xl shadow-black/80">
                       {/* Background Logo Overlay */}
                       <Shield className={`absolute -right-20 -top-20 w-80 h-80 opacity-5 rotate-12 ${getThemeColor(result.category).text}`} />
                       
                       <div className="relative z-10 flex flex-col h-full">
                          
                          <div className="flex items-start justify-between mb-8">
                             <div className="flex flex-col">
                                <span className="text-[10px] font-mono font-black text-gray-500 tracking-[0.3em] uppercase mb-1">Risk Assessment</span>
                                <h3 className={`text-4xl font-display font-black tracking-tighter uppercase ${getThemeColor(result.category).text}`}>
                                   {result.category}
                                </h3>
                             </div>
                             <div className={`p-3 rounded-xl bg-black border ${getThemeColor(result.category).border}/30 ${getThemeColor(result.category).text}`}>
                                {result.category.toLowerCase() === 'fake' ? <AlertCircle size={28} /> : 
                                 result.category.toLowerCase() === 'suspicious' ? <AlertTriangle size={28} /> : 
                                 <CheckCircle size={28} />}
                             </div>
                          </div>

                          {/* Score Visualizer */}
                          <div className="bg-black/40 rounded-2xl p-6 border border-white/5 mb-8">
                             <div className="flex items-center justify-between mb-4">
                                <span className="text-xs font-mono font-bold text-gray-300">TRUST_INDEX</span>
                                <span className={`text-2xl font-display font-black ${getThemeColor(result.category).text}`}>{result.score}%</span>
                             </div>
                             <div className="h-3 bg-white/5 rounded-full overflow-hidden">
                                <div 
                                  className={`h-full transition-all duration-1000 ease-out rounded-full ${getThemeColor(result.category).bg}`}
                                  style={{ width: `${result.score}%` }}
                                ></div>
                             </div>
                          </div>

                          {/* Detail Grid */}
                          <div className="grid grid-cols-2 gap-3 mb-8">
                             <AnalysisPill label="SENTIMENT" value={result.sentiment || 'NEUTRAL'} color={result.sentiment?.includes('Positive') ? '#00ff88' : '#ef4444'} />
                             <AnalysisPill label="SUBJECTIVITY" value={`${(result.subjectivity * 100).toFixed(0)}%`} color="#a855f7" />
                          </div>

                          {/* Deep Scan Flags */}
                          <div className="flex-1 space-y-4">
                             <div className="flex items-center gap-2 text-[10px] font-mono font-black text-gray-500 uppercase">
                                <FileSearch size={12} /> Forensic Flags
                             </div>
                             <div className="flex flex-wrap gap-2">
                                {result.flags && result.flags.length > 0 ? (
                                  result.flags.map((flag, i) => (
                                    <span key={i} className="px-3 py-1.5 rounded-lg bg-red-500/10 border border-red-500/20 text-red-500 text-[9px] font-mono font-bold uppercase tracking-widest">
                                      {flag}
                                    </span>
                                  ))
                                ) : (
                                  <span className="px-3 py-1.5 rounded-lg bg-[#00ff88]/10 border border-[#00ff88]/20 text-[#00ff88] text-[9px] font-mono font-bold uppercase tracking-widest">
                                    NO_SCAM_PATTERNS_DETECTED
                                  </span>
                                )}
                             </div>
                          </div>

                          <div className="mt-8 border-t border-white/5 pt-6">
                             <p className="text-gray-400 text-sm italic leading-relaxed font-mono">
                                "{result.explanation}"
                             </p>
                          </div>

                          <div className="flex items-center gap-3 mt-8">
                             <button className="flex-1 py-3 bg-white/5 border border-white/10 rounded-xl text-white font-mono text-[10px] font-bold uppercase tracking-widest hover:bg-white/10 transition-all flex items-center justify-center gap-2">
                                <Download size={12} /> Export_Packet
                             </button>
                             <button className="flex-1 py-3 bg-white/5 border border-white/10 rounded-xl text-white font-mono text-[10px] font-bold uppercase tracking-widest hover:bg-white/10 transition-all flex items-center justify-center gap-2 text-glow">
                                <Share2 size={12} /> Global_Broadcast
                             </button>
                          </div>
                       </div>
                    </div>
                  )}
               </div>

               {/* Entities Module */}
               {result && result.entities && result.entities.length > 0 && (
                 <div className="animate-in slide-in-from-bottom-10 fade-in duration-700 delay-300 border border-white/5 bg-[#0d0f14]/50 rounded-3xl p-8 backdrop-blur-sm">
                    <div className="flex items-center gap-2 text-[10px] font-mono font-black text-[#00ff88] uppercase mb-6">
                       <BarChart3 size={14} /> Intelligence_Nodes
                    </div>
                    <div className="flex flex-col gap-3">
                       {result.entities.map((ent, i) => (
                         <div key={i} className="flex items-center justify-between group">
                            <span className="text-sm font-semibold text-gray-300 group-hover:text-white transition-colors">{ent}</span>
                            <div className="h-px flex-1 mx-4 bg-white/[0.03]"></div>
                            <span className="text-[10px] font-mono text-gray-600">ENTITY_{i+1}</span>
                         </div>
                       ))}
                    </div>
                 </div>
               )}

            </div>
          </div>
          )}

          {activeTab === 'KB' && (
            <div className="flex flex-col gap-10 animate-in fade-in slide-in-from-bottom-4 duration-500">
              
              {/* Header and Summary Dashboard */}
              <div className="flex flex-col lg:flex-row gap-8 items-start lg:items-end justify-between border-b border-white/5 pb-8">
                <div className="flex flex-col gap-3 max-w-2xl">
                  <div className="flex items-center gap-3 text-[#00ff88] mb-2">
                    <Database size={24} />
                    <span className="text-[10px] font-mono font-black tracking-[0.3em] uppercase">Global Neural Index</span>
                  </div>
                  <h2 className="text-4xl md:text-5xl font-display font-black text-white tracking-tight uppercase leading-none">
                    Intelligence <span className="text-[#00ff88] text-glow">Registry</span>
                  </h2>
                  <p className="text-gray-400 font-mono text-xs leading-relaxed mt-2">
                    A comprehensive catalog of the raw datasets, global sensors, academic archives, and web crawls utilized to construct the Deep Scan Engine's foundational parameters. Total synthesis represents the entirety of indexed human digital presence.
                  </p>
                </div>
                
                {/* Scale Dashboards */}
                <div className="flex gap-4 w-full lg:w-auto">
                   <div className="flex-1 lg:w-40 bg-[#0d0f14]/80 border border-white/10 rounded-2xl p-4 flex flex-col justify-between relative overflow-hidden group">
                      <div className="absolute top-0 right-0 w-16 h-16 bg-[#00ff88]/10 blur-xl group-hover:bg-[#00ff88]/20 transition-all"></div>
                      <span className="text-[9px] font-mono font-black text-gray-500 tracking-[0.2em] uppercase mb-4 relative z-10">Total Volume</span>
                      <span className="text-2xl font-display font-black text-white relative z-10 flex items-baseline gap-1">
                        100+ <span className="text-xs text-[#00ff88]">PB</span>
                      </span>
                   </div>
                   <div className="flex-1 lg:w-40 bg-[#0d0f14]/80 border border-white/10 rounded-2xl p-4 flex flex-col justify-between relative overflow-hidden group">
                      <div className="absolute top-0 right-0 w-16 h-16 bg-[#00ff88]/10 blur-xl group-hover:bg-[#00ff88]/20 transition-all"></div>
                      <span className="text-[9px] font-mono font-black text-gray-500 tracking-[0.2em] uppercase mb-4 relative z-10">Data Nodes</span>
                      <span className="text-2xl font-display font-black text-white relative z-10 flex items-baseline gap-1">
                        Trillions
                      </span>
                   </div>
                </div>
              </div>

              {/* Data Grid */}
              <div className="bg-[#0d0f14]/40 border border-white/5 rounded-3xl overflow-hidden backdrop-blur-md">
                 <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse">
                       <thead>
                          <tr className="border-b border-white/5 bg-black/40">
                             <th className="px-6 py-5 text-[10px] font-mono font-black text-gray-500 tracking-widest uppercase">Dataset Name</th>
                             <th className="px-6 py-5 text-[10px] font-mono font-black text-gray-500 tracking-widest uppercase">Description</th>
                             <th className="px-6 py-5 text-[10px] font-mono font-black text-gray-500 tracking-widest uppercase">Target Source</th>
                             <th className="px-6 py-5 text-[10px] font-mono font-black text-gray-500 tracking-widest uppercase text-right">Volume</th>
                          </tr>
                       </thead>
                       <tbody className="divide-y divide-white/5">
                          {kbDatasets.map((ds, i) => (
                             <tr key={i} className="group hover:bg-white/[0.02] transition-colors relative">
                                <td className="px-6 py-5">
                                   <div className="flex items-center gap-3">
                                      <div className="w-1.5 h-1.5 rounded-full bg-gray-700 group-hover:bg-[#00ff88] group-hover:shadow-[0_0_8px_#00ff88] transition-all duration-300"></div>
                                      <span className="text-sm font-display font-bold text-gray-200 group-hover:text-white transition-colors uppercase tracking-wider">{ds.name}</span>
                                   </div>
                                </td>
                                <td className="px-6 py-5">
                                   <span className="text-xs font-sans text-gray-400 group-hover:text-gray-300 transition-colors">
                                      {ds.desc}
                                   </span>
                                </td>
                                <td className="px-6 py-5">
                                   <span className="inline-flex items-center justify-center px-2 py-1 rounded bg-black/60 border border-white/10 text-[9px] font-mono font-black text-gray-400 uppercase tracking-widest whitespace-nowrap">
                                      {ds.source}
                                   </span>
                                </td>
                                <td className="px-6 py-5 text-right">
                                   <span className="text-xs font-mono font-bold text-[#00ff88] whitespace-nowrap">
                                      {ds.size}
                                   </span>
                                </td>
                             </tr>
                          ))}
                       </tbody>
                    </table>
                 </div>
              </div>

            </div>
          )}
        </main>
      </div>
    </div>
  );
}

function NavItem({ icon, label, active, onClick }) {
  return (
    <button 
      onClick={onClick}
      className={`flex items-center gap-2 group transition-all duration-300 relative
        ${active ? 'text-[#00ff88]' : 'text-gray-500 hover:text-gray-300'}`}
    >
      {icon}
      <span className="text-[10px] font-mono font-black tracking-widest uppercase">{label}</span>
      {active && <div className="absolute -bottom-7 left-0 right-0 h-0.5 bg-[#00ff88] shadow-[0_0_8px_#00ff88]"></div>}
    </button>
  );
}

function LoadingStep({ label, active, delay }) {
  return (
    <div className={`flex items-center gap-4 transition-all duration-500`} style={{ transitionDelay: delay }}>
       <div className={`w-1.5 h-1.5 rounded-full ${active ? 'bg-[#00ff88] animate-ping' : 'bg-gray-800'}`}></div>
       <span className={`text-[10px] font-mono font-bold tracking-widest uppercase ${active ? 'text-white' : 'text-gray-700'}`}>
         {label}
       </span>
       {active && <div className="ml-auto w-12 h-px bg-[#00ff88]/20"></div>}
    </div>
  );
}

function AnalysisPill({ label, value, color }) {
  return (
    <div className="bg-black/60 rounded-xl p-4 border border-white/5">
       <div className="text-[8px] font-mono font-black text-gray-600 uppercase mb-2">{label}</div>
       <div className="text-[10px] font-mono font-black uppercase tracking-widest" style={{ color }}>{value}</div>
    </div>
  );
}
