import React, { useState } from 'react';
import { Copy, Check, Terminal, Shield, ArrowRight, Server, Key } from 'lucide-react';

export default function App() {
  const [baseUrl, setBaseUrl] = useState('');
  const [apiKey, setApiKey] = useState('');
  const [generatedCommand, setGeneratedCommand] = useState('');
  const [copied, setCopied] = useState(false);

  const handleGenerate = () => {
    // Generate the one-liner curl command
    // We assume the user's browser URL host is where the app is hosted
    const host = window.location.origin;
    const command = `curl -sL "${host}/script.py" | URL_MINI="${baseUrl}" KEY_MINI="${apiKey}" python3`;
    setGeneratedCommand(command);
    setCopied(false);
  };

  const handleCopy = async () => {
    if (!generatedCommand) return;
    await navigator.clipboard.writeText(generatedCommand);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="min-h-screen bg-[#121212] text-gray-100 py-10 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        <header className="mb-10 text-center">
          <div className="inline-flex items-center justify-center space-x-3 mb-4">
            <Shield className="text-green-500" size={36} />
            <h1 className="text-4xl font-bold">Kiro Agentic Deployer</h1>
          </div>
          <p className="text-gray-400 text-lg max-w-2xl mx-auto">
            Masukkan konfigurasi AI Anda untuk menghasilkan One-Liner Script.
            Script dapat langsung dijalankan di Termux atau VPS tanpa perlu membuat file .env manual.
          </p>
        </header>

        <div className="bg-[#1e1e1e] p-6 border border-gray-700 rounded-xl shadow-lg mb-8">
          <h2 className="text-xl font-semibold mb-6 text-white border-b border-gray-700 pb-4">Konfigurasi Kredensial</h2>
          
          <div className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-1 flex items-center">
                <Server size={16} className="mr-2 text-blue-400" />
                AI Base URL (URL_MINI)
              </label>
              <input
                type="url"
                value={baseUrl}
                onChange={(e) => setBaseUrl(e.target.value)}
                placeholder="https://autoapp.biz.id/v1"
                className="w-full bg-[#121212] text-gray-200 text-sm p-3 rounded border border-gray-700 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-400 mb-1 flex items-center">
                <Key size={16} className="mr-2 text-yellow-400" />
                AI API Key (KEY_MINI)
              </label>
              <input
                type="password"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder="sk-qwen-395decf..."
                className="w-full bg-[#121212] text-gray-200 text-sm p-3 rounded border border-gray-700 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none"
              />
            </div>
            
            <button
              onClick={handleGenerate}
              disabled={!baseUrl.trim() || !apiKey.trim()}
              className="mt-6 w-full flex items-center justify-center space-x-2 bg-blue-600 hover:bg-blue-500 disabled:bg-gray-600 disabled:cursor-not-allowed text-white py-3 rounded-lg font-semibold transition-colors"
            >
              <span>Generate Install Script</span>
              <ArrowRight size={18} />
            </button>
          </div>
        </div>

        {generatedCommand && (
          <div className="space-y-4 animate-in fade-in duration-500">
            <div className="bg-[#1e1e1e] p-6 border border-green-500/30 rounded-xl shadow-lg relative overflow-hidden">
              <div className="absolute top-0 left-0 w-full h-1 bg-green-500"></div>
              <h2 className="text-xl font-semibold mb-4 flex items-center text-green-400">
                <Check className="mr-2" size={24} />
                Script Berhasil Dibuat
              </h2>
              
              <p className="text-gray-400 mb-4 text-sm">
                Copy dan jalankan perintah di bawah ini pada terminal Termux atau VPS Anda.
                Script Kiro Agentic akan otomatis diunduh dan dieksekusi dengan kredensial Anda.
              </p>
              
              <div className="relative group">
                <div className="bg-[#121212] p-4 pr-16 rounded border border-gray-700 font-mono text-sm text-cyan-300 break-all">
                  {generatedCommand}
                </div>
                
                <button
                  onClick={handleCopy}
                  className="absolute right-2 top-2 bottom-2 px-4 flex items-center justify-center text-gray-300 bg-[#2d2d2d] hover:bg-[#3d3d3d] rounded transition-colors"
                  title="Copy to clipboard"
                >
                  {copied ? <Check size={18} className="text-green-400" /> : <Copy size={18} />}
                </button>
              </div>
              
              <div className="mt-6 border-t border-gray-700 pt-4 flex items-start space-x-3 text-sm text-gray-500">
                <Terminal size={18} className="mt-0.5 text-gray-400 flex-shrink-0" />
                <p>
                  Perintah ini menggunakan variabel lingkungan (environment variables) yang aman karena tidak akan tersimpan secara permanen dalam file di dalam server Anda. Kredensial hanya aktif selama script berjalan di memori.
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
