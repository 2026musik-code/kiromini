import React, { useState } from 'react';
import { Copy, Download, Check, Code2, Cloud, Terminal, Shield, ArrowRight } from 'lucide-react';

const defaultPythonCode = `import os
import sys

# Ambil kredensial dari ENV (Otomatis disediakan oleh parser di atas)
API_KEY = os.environ.get("KEY_MINI")
BASE_URL = os.environ.get("URL_MINI")

def main():
    print("✅ Berhasil terhubung!")
    print(f"URL: {BASE_URL}")
    print(f"KEY: {API_KEY[:6]}... (Tersembunyi)")
    
    # Masukkan sisa logika Anda di sini...
    # (Hapus kode ini dan masukkan kode asli Anda, ingat untuk menggunakan os.environ.get() untuk membaca key)

if __name__ == "__main__":
    main()
`;

function CodeBlock({ filename, content, language = 'python' }: { filename: string, content: string, language?: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (!content) return null;

  return (
    <div className="bg-[#1e1e1e] border border-gray-700 rounded-lg overflow-hidden flex flex-col">
      <div className="flex items-center justify-between px-4 py-2 bg-[#2d2d2d] border-b border-gray-700">
        <div className="flex items-center space-x-2 text-gray-300">
          <Code2 size={16} className="text-blue-400" />
          <span className="font-mono text-sm font-semibold">{filename}</span>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={handleCopy}
            className="flex items-center space-x-1 px-3 py-1.5 text-xs font-medium text-gray-300 bg-[#3d3d3d] hover:bg-[#4d4d4d] rounded transition-colors cursor-pointer"
          >
            {copied ? <Check size={14} className="text-green-400" /> : <Copy size={14} />}
            <span>{copied ? 'Copied!' : 'Copy'}</span>
          </button>
          <button
            onClick={handleDownload}
            className="flex items-center space-x-1 px-3 py-1.5 text-xs font-medium text-white bg-blue-600 hover:bg-blue-500 rounded transition-colors cursor-pointer"
          >
            <Download size={14} />
            <span>Download</span>
          </button>
        </div>
      </div>
      <div className="p-4 overflow-x-auto max-h-[400px] overflow-y-auto">
        <pre className="text-gray-300 font-mono text-xs md:text-sm whitespace-pre">
          <code>{content}</code>
        </pre>
      </div>
    </div>
  );
}

export default function App() {
  const [inputCode, setInputCode] = useState(defaultPythonCode);
  const [workerCode, setWorkerCode] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState('');

  const handleGenerate = async () => {
    setIsGenerating(true);
    setError('');
    
    try {
      const response = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pythonCode: inputCode })
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || 'Failed to generate worker');
      }
      
      setWorkerCode(data.workerCode);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#121212] text-gray-100 py-10 px-4 sm:px-6 lg:px-8">
      <div className="max-w-5xl mx-auto">
        <header className="mb-10 text-center">
          <div className="inline-flex items-center justify-center space-x-3 mb-4">
            <Shield className="text-green-500" size={36} />
            <h1 className="text-4xl font-bold">Stealth Deploy Generator</h1>
            <Cloud className="text-blue-500" size={36} />
          </div>
          <p className="text-gray-400 text-lg max-w-2xl mx-auto">
            Ubah Script Python Anda menjadi One-Liner Execution via Cloudflare Worker.
            Kode diacak (Obfuscated) dan berjalan In-Memory tanpa menyimpan file asli di VPS user!
          </p>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          
          {/* LEFT COLUMN: Input */}
          <div className="space-y-4">
            <div className="bg-[#1e1e1e] p-5 border border-gray-700 rounded-xl shadow-lg">
              <h2 className="text-xl font-semibold mb-2 flex items-center text-blue-400">
                <Code2 className="mr-2" size={20} />
                1. Masukkan Script Python Asli
              </h2>
              <p className="text-sm text-gray-400 mb-4">
                PENTING: Ubah bagian <code>API_KEY</code> agar mengambil dari <code>os.environ.get("KEY_MINI")</code>. 
                Sistem akan otomatis menginjeksi pembaca <code>.env</code> ke script Anda!
              </p>
              
              <textarea
                value={inputCode}
                onChange={(e) => setInputCode(e.target.value)}
                className="w-full h-[400px] bg-[#121212] text-gray-200 font-mono text-sm p-4 rounded border border-gray-700 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none resize-y"
                spellCheck="false"
              />
              
              {error && (
                <div className="mt-4 p-3 bg-red-900/50 border border-red-500 text-red-200 rounded text-sm">
                  {error}
                </div>
              )}
              
              <button
                onClick={handleGenerate}
                disabled={isGenerating || !inputCode.trim()}
                className="mt-4 w-full flex items-center justify-center space-x-2 bg-blue-600 hover:bg-blue-500 disabled:bg-gray-600 disabled:cursor-not-allowed text-white py-3 rounded-lg font-semibold transition-colors"
              >
                {isGenerating ? (
                  <span>Memproses...</span>
                ) : (
                  <>
                    <span>Generate Cloudflare Worker</span>
                    <ArrowRight size={18} />
                  </>
                )}
              </button>
            </div>
          </div>

          {/* RIGHT COLUMN: Output */}
          <div className="space-y-6">
            <div className="bg-[#1e1e1e] p-5 border border-gray-700 rounded-xl shadow-lg h-full flex flex-col">
              <h2 className="text-xl font-semibold mb-2 flex items-center text-green-400">
                <Cloud className="mr-2" size={20} />
                2. Hasil Cloudflare Worker
              </h2>
              
              {!workerCode ? (
                <div className="flex-grow flex items-center justify-center flex-col text-gray-500 border-2 border-dashed border-gray-700 rounded-lg p-6">
                  <Cloud size={48} className="mb-4 opacity-50" />
                  <p className="text-center">Klik tombol Generate untuk menghasilkan script Cloudflare Worker (worker.js)</p>
                </div>
              ) : (
                <div className="space-y-6">
                  <p className="text-sm text-gray-400">
                    Copy kode JavaScript ini dan paste di dalam dashboard <strong>Cloudflare Worker</strong> Anda. Script ini sudah berisi payload Python yang terenkripsi dan otomatis tereksekusi.
                  </p>
                  <CodeBlock filename="worker.js" content={workerCode} language="javascript" />
                  
                  <div className="border-t border-gray-700 pt-6">
                    <h3 className="text-lg font-medium text-yellow-400 mb-3 flex items-center">
                      <Terminal className="mr-2" size={18} />
                      Cara User Menjalankan:
                    </h3>
                    <div className="bg-[#121212] p-4 rounded border border-gray-700 font-mono text-sm space-y-3">
                      <p className="text-gray-400"># 1. User membuat file .env di Termux/VPS</p>
                      <p className="text-green-300">echo "URL_MINI=https://..." &gt; .env</p>
                      <p className="text-green-300">echo "KEY_MINI=sk-..." &gt;&gt; .env</p>
                      <div className="py-2"></div>
                      <p className="text-gray-400"># 2. User menjalankan eksekutor in-memory</p>
                      <p className="text-cyan-300">curl -sL https://NAMA_WORKER_ANDA.workers.dev | python3</p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}
