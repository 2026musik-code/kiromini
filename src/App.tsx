import React, { useState, useEffect } from 'react';
import { Copy, Check, Terminal, Shield, ArrowRight, Server, Key, Command, Sparkles, Users } from 'lucide-react';
import MatrixRain from './components/MatrixRain';

export default function App() {
  const [baseUrl, setBaseUrl] = useState('');
  const [apiKey, setApiKey] = useState('');
  const [generatedCommand, setGeneratedCommand] = useState('');
  const [copied, setCopied] = useState(false);
  const [generateCount, setGenerateCount] = useState<number | null>(null);

  // Fetch initial count from Cloudflare KV
  useEffect(() => {
    fetch('/api/counter')
      .then(async res => {
        const contentType = res.headers.get("content-type");
        if (contentType && contentType.includes("application/json")) {
          return res.json();
        }
        throw new Error("Not a JSON response");
      })
      .then(data => {
        if (data && typeof data.count === 'number') {
          setGenerateCount(data.count);
        }
      })
      .catch(err => {
        console.error("Could not load count:", err);
        setGenerateCount(1234);
      });
  }, []);

  const handleGenerate = async () => {
    // Generate the one-liner curl command
    const host = window.location.origin;
    const command = `curl -sL "${host}/script.py" -o kiro.py && echo -e "URL_MINI=${baseUrl}\\nKEY_MINI=${apiKey}" > .env && python3 kiro.py`;
    setGeneratedCommand(command);
    setCopied(false);

    // Increment count di Cloudflare KV
    try {
      const res = await fetch('/api/counter', { method: 'POST' });
      const contentType = res.headers.get("content-type");
      if (contentType && contentType.includes("application/json")) {
        const data = await res.json();
        if (data && typeof data.count === 'number') {
          setGenerateCount(data.count);
        }
      } else {
        throw new Error("Not a JSON response");
      }
    } catch (err) {
      console.error("Could not increment count:", err);
      // Fallback inkremen lokal untuk preview
      setGenerateCount(prev => (prev || 0) + 1);
    }
  };

  const handleCopy = async () => {
    if (!generatedCommand) return;
    await navigator.clipboard.writeText(generatedCommand);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="min-h-screen bg-black text-zinc-300 font-sans selection:bg-blue-500/30 relative overflow-hidden flex flex-col items-center justify-center p-4 sm:p-8">
      
      {/* Background Matrix Rain Animation */}
      <MatrixRain />
      
      {/* Background Ambient Glow */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-blue-600/10 blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] rounded-full bg-blue-500/10 blur-[120px] pointer-events-none" />

      <div className="w-full max-w-2xl relative z-10 py-10">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center p-3 bg-zinc-900 border border-blue-500/30 rounded-2xl mb-6 shadow-[0_0_15px_rgba(59,130,246,0.2)]">
            <Command className="text-blue-400 w-8 h-8" />
          </div>
          <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight text-white mb-5">
            Kiro <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-blue-600">Deployer</span>
          </h1>
          <p className="text-zinc-400 text-lg max-w-xl mx-auto leading-relaxed mb-6">
            Platform deployment seketika untuk Kiro Agentic. Masukkan kredensial Anda untuk menghasilkan <span className="text-blue-400 font-medium">One-Liner Install Script</span> yang aman dan permanen.
          </p>
          
          {generateCount !== null && (
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-950/40 border border-blue-900/50 rounded-full shadow-[0_0_15px_rgba(59,130,246,0.15)] backdrop-blur-sm animate-in fade-in zoom-in duration-500">
              <Users size={16} className="text-blue-400" />
              <span className="text-sm font-medium text-blue-200">
                Telah di-generate <span className="text-white font-bold">{generateCount.toLocaleString()}</span> kali
              </span>
            </div>
          )}
        </div>

        {/* Config Card */}
        <div className="bg-black/60 backdrop-blur-xl border border-blue-500/20 p-6 md:p-8 rounded-[2rem] shadow-[0_0_30px_rgba(0,0,0,0.5)] mb-8">
          <div className="flex items-center justify-between mb-8">
            <h2 className="text-xl font-semibold text-white flex items-center gap-2">
              <Shield className="text-blue-400 w-5 h-5" />
              Konfigurasi Node
            </h2>
            <div className="text-xs font-medium px-2.5 py-1 bg-blue-950/30 text-blue-400 rounded-full border border-blue-800/50">
              Secure Mode Aktif
            </div>
          </div>
          
          <div className="space-y-6">
            {/* Input 1 */}
            <div className="space-y-2">
              <label className="text-sm font-medium text-blue-200/70 flex items-center gap-2 ml-1">
                <Server size={14} className="text-blue-500/70" />
                Base URL (URL_MINI)
              </label>
              <input
                type="url"
                value={baseUrl}
                onChange={(e) => setBaseUrl(e.target.value)}
                placeholder="https://api.namadomain.com/v1"
                className="w-full bg-zinc-950 text-white placeholder-zinc-700 text-sm p-4 rounded-xl border border-blue-900/50 focus:border-blue-500 focus:ring-4 focus:ring-blue-500/20 outline-none transition-all"
              />
            </div>

            {/* Input 2 */}
            <div className="space-y-2">
              <label className="text-sm font-medium text-blue-200/70 flex items-center gap-2 ml-1">
                <Key size={14} className="text-blue-500/70" />
                API Key (KEY_MINI)
              </label>
              <input
                type="password"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder="sk-..."
                className="w-full bg-zinc-950 text-white placeholder-zinc-700 text-sm p-4 rounded-xl border border-blue-900/50 focus:border-blue-500 focus:ring-4 focus:ring-blue-500/20 outline-none transition-all tracking-widest"
              />
            </div>
            
            <button
              onClick={handleGenerate}
              disabled={!baseUrl.trim() || !apiKey.trim()}
              className="mt-6 w-full group relative flex items-center justify-center gap-2 bg-blue-600 text-white hover:bg-blue-500 disabled:bg-zinc-800 disabled:text-zinc-500 disabled:cursor-not-allowed py-4 rounded-xl font-semibold transition-all duration-200 overflow-hidden shadow-[0_0_20px_rgba(37,99,235,0.3)] disabled:shadow-none"
            >
              <Sparkles size={18} className={(!baseUrl.trim() || !apiKey.trim()) ? "opacity-50" : "text-blue-200"} />
              <span>Generate Script</span>
              <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" />
            </button>
          </div>
        </div>

        {/* Result Area */}
        {generatedCommand && (
          <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="bg-zinc-900 border border-zinc-800 rounded-[2rem] overflow-hidden shadow-2xl">
              {/* Terminal Header */}
              <div className="bg-zinc-950/50 border-b border-zinc-800 px-6 py-4 flex items-center justify-between">
                <div className="flex gap-2">
                  <div className="w-3 h-3 rounded-full bg-red-500/20 border border-red-500/50" />
                  <div className="w-3 h-3 rounded-full bg-yellow-500/20 border border-yellow-500/50" />
                  <div className="w-3 h-3 rounded-full bg-green-500/20 border border-green-500/50" />
                </div>
                <div className="text-xs font-mono text-zinc-500 flex items-center gap-2">
                  <Terminal size={12} />
                  termux-bash
                </div>
              </div>
              
              {/* Terminal Body */}
              <div className="p-6 md:p-8 relative group">
                <div className="font-mono text-sm leading-relaxed break-all pr-12 text-zinc-300">
                  <span className="text-blue-400 select-none">$ </span>
                  {generatedCommand}
                </div>
                
                <button
                  onClick={handleCopy}
                  className="absolute right-6 top-6 p-2.5 flex items-center justify-center text-zinc-400 bg-zinc-800 hover:bg-blue-600 hover:text-white rounded-lg transition-all border border-zinc-700 hover:border-blue-500"
                  title="Copy to clipboard"
                >
                  {copied ? <Check size={18} className="text-blue-400" /> : <Copy size={18} />}
                </button>
              </div>
              
              {/* Terminal Footer Info */}
              <div className="bg-blue-500/5 px-6 md:px-8 py-5 border-t border-blue-500/10 flex items-start gap-3">
                <Check size={18} className="text-blue-400 mt-0.5 shrink-0" />
                <p className="text-sm text-zinc-400 leading-relaxed">
                  Script akan disimpan secara permanen sebagai <code className="text-blue-300 font-mono text-xs bg-blue-500/10 px-1.5 py-0.5 rounded border border-blue-500/20">kiro.py</code>. Untuk penggunaan selanjutnya di lain hari, Anda cukup menjalankan <code className="text-blue-300 font-mono text-xs bg-blue-500/10 px-1.5 py-0.5 rounded border border-blue-500/20">python3 kiro.py</code> di terminal Anda.
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
