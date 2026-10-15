"use client";
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
import { useEffect, useState, useRef } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

interface StatsType {
  dump_truck: number;
  excavator: number;
  bulldozer: number;
  car: number;
  motor_grader: number;
  latency_ms: number;
  model_version: string;
  logs: string[];
}

export default function Home() {
  const [stats, setStats] = useState<StatsType>({
    dump_truck: 0,
    excavator: 0,
    bulldozer: 0,
    car: 0,
    motor_grader: 0,
    latency_ms: 0,
    model_version: "Loading...",
    logs: []
  });

  const [isConnected, setIsConnected] = useState(false);
  const [videoKey, setVideoKey] = useState(0);
  const prevConnectionRef = useRef(false);

  // 1. State baru untuk mengontrol kemunculan Custom Modal Konfirmasi & Notifikasi
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [isResetting, setIsResetting] = useState(false);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/stats`);
        if (response.ok) {
          const data = await response.json();
          setStats(data);
          setIsConnected(true);

          if (!prevConnectionRef.current) {
            setVideoKey(Date.now());
            prevConnectionRef.current = true;
          }
        } else {
          setIsConnected(false);
          prevConnectionRef.current = false;
        }
      } catch (error) {
        setIsConnected(false);
        prevConnectionRef.current = false;
      }
    };

    const interval = setInterval(fetchStats, 1000);
    return () => clearInterval(interval);
  }, []);

  // 2. Fungsi eksekusi Reset yang dipanggil dari dalam Modal
  const confirmResetData = async () => {
    setIsResetting(true);
    try {
      await fetch(`${API_BASE_URL}/reset`, {
        method: "POST"
      });
      setShowConfirmModal(false); // Tutup modal setelah sukses
    } catch (error) {
      console.error("Gagal mereset data:", error);
    } finally {
      setIsResetting(false);
    }
  };

  const chartData = [
    { name: 'Dump Truck', total: stats.dump_truck, color: '#fbbf24' },
    { name: 'Excavator', total: stats.excavator, color: '#34d399' },
    { name: 'Bulldozer', total: stats.bulldozer, color: '#60a5fa' },
    { name: 'Motor Grader', total: stats.motor_grader, color: '#2dd4bf' },
    { name: 'Car', total: stats.car, color: '#c084fc' }
  ];

  return (
    <div className="min-h-screen bg-slate-900 text-white p-6 relative">

      {/* HEADER */}
      <header className="mb-8 border-b border-slate-700 pb-4 flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold text-blue-400">Mining Vehicle Monitor</h1>
          <p className="text-slate-400">Mining Vehicle AI Detection - Proof of Concept</p>
        </div>

        {/* Tombol memicu Custom Modal */}
        <button
          onClick={() => setShowConfirmModal(true)}
          className="bg-red-500/10 text-red-400 border border-red-500/50 hover:bg-red-500/20 px-4 py-2 rounded-lg text-sm font-semibold transition-all flex items-center gap-2 group cursor-pointer shadow-lg shadow-red-500/5"
          title="Kosongkan semua statistik dan log"
        >
          <svg className="w-4 h-4 group-hover:-rotate-180 transition-transform duration-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Reset Data
        </button>
      </header>

      {/* --- KONTEN UTAMA --- */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-slate-800 rounded-xl overflow-hidden border border-slate-700 shadow-lg">
          <div className="bg-slate-950 p-3 border-b border-slate-700 flex justify-between items-center">
            <h2 className="font-semibold flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-red-500 animate-pulse' : 'bg-slate-600'}`}></span>
              LIVE: PIT-01 Camera
            </h2>
            <span className="text-xs bg-blue-900 text-blue-300 px-2 py-1 rounded">YOLOv8 Active</span>
          </div>
          <div className="aspect-video bg-black relative flex items-center justify-center">
            {isConnected ? (
              <img
                key={videoKey}
                src={`${API_BASE_URL}/video_feed?t=${videoKey}`}
                alt="CCTV Stream"
                className="w-full h-full object-contain"
              />
            ) : (
              <div className="flex flex-col items-center text-slate-500">
                <svg className="w-12 h-12 mb-4 animate-pulse text-red-500/50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M18.364 5.636a9 9 0 010 12.728m0 0l-2.829-2.829m2.829 2.829L21 21M15.536 8.464a5 5 0 010 7.072m0 0l-2.829-2.829m-4.243 2.829a4.978 4.978 0 01-1.414-2.83m-1.414 5.658a9 9 0 01-2.167-9.238m7.824 2.167a1 1 0 111.414 1.414m-1.414-1.414L3 3m8.293 8.293l1.414 1.414" />
                </svg>
                <p className="text-lg font-medium text-slate-400">Koneksi Kamera Terputus</p>
                <p className="text-sm mt-1">Menunggu server AI diaktifkan kembali...</p>
              </div>
            )}
          </div>
        </div>

        <div className="flex flex-col gap-6">
          <div className="bg-slate-800 p-6 rounded-xl border border-slate-700 shadow-lg">
            <h2 className="text-xl font-semibold mb-4 text-slate-200">Vehicle Counter Real-Time</h2>
            <div className="space-y-4">
              <div className="bg-slate-700/50 p-4 rounded-lg flex justify-between items-center border border-slate-600 transition-all">
                <span className="text-slate-300 font-medium">Dump Truck</span>
                <span className="text-2xl font-bold text-amber-400">{stats.dump_truck}</span>
              </div>
              <div className="bg-slate-700/50 p-4 rounded-lg flex justify-between items-center border border-slate-600 transition-all">
                <span className="text-slate-300 font-medium">Excavator</span>
                <span className="text-2xl font-bold text-emerald-400">{stats.excavator}</span>
              </div>
              <div className="bg-slate-700/50 p-4 rounded-lg flex justify-between items-center border border-slate-600 transition-all">
                <span className="text-slate-300 font-medium">Bulldozer</span>
                <span className="text-2xl font-bold text-blue-400">{stats.bulldozer}</span>
              </div>
              <div className="bg-slate-700/50 p-4 rounded-lg flex justify-between items-center border border-slate-600 transition-all">
                <span className="text-slate-300 font-medium">Motor Grader</span>
                <span className="text-2xl font-bold text-teal-400">{stats.motor_grader}</span>
              </div>
              <div className="bg-slate-700/50 p-4 rounded-lg flex justify-between items-center border border-slate-600 transition-all">
                <span className="text-slate-300 font-medium">Car</span>
                <span className="text-2xl font-bold text-purple-400">{stats.car}</span>
              </div>
            </div>
          </div>

          <div className="bg-slate-800 p-6 rounded-xl border border-slate-700 shadow-lg flex-1">
            <h2 className="text-xl font-semibold mb-4 text-slate-200">System Status</h2>
            <ul className="space-y-3 text-sm">
              <li className="flex justify-between items-center">
                <span className="text-slate-400">AI Model</span>
                <span className="text-green-400 bg-green-400/10 px-2 py-1 rounded">{stats.model_version}</span>
              </li>
              <li className="flex justify-between items-center">
                <span className="text-slate-400">API Connection</span>
                {isConnected ? (
                  <span className="text-blue-400 flex items-center gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-pulse"></span>
                    Connected
                  </span>
                ) : (
                  <span className="text-red-400 flex items-center gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-red-400"></span>
                    Disconnected
                  </span>
                )}
              </li>
              <li className="flex justify-between items-center">
                <span className="text-slate-400">Server Latency</span>
                <span className={`${stats.latency_ms > 100 ? 'text-amber-400' : 'text-slate-200'} font-mono`}>
                  ~{stats.latency_ms} ms
                </span>
              </li>
            </ul>
          </div>
        </div>
      </div>

      {/* --- KONTEN BAWAH --- */}
      <div className="mt-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-slate-800 rounded-xl border border-slate-700 shadow-lg p-6">
          <h2 className="text-xl font-semibold mb-4 text-slate-200 flex items-center gap-2">
            <svg className="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 10h16M4 14h16M4 18h16"></path>
            </svg>
            Live Activity Log
          </h2>

          <div className="bg-slate-900 rounded-lg p-4 h-[250px] overflow-y-auto border border-slate-700 font-mono text-sm space-y-2">
            {stats.logs && stats.logs.length > 0 ? (
              stats.logs.map((log, index) => {
                const timeString = log.substring(0, 10);
                const messageString = log.substring(10);
                return (
                  <div key={index} className="text-slate-300 border-b border-slate-800 pb-2 last:border-0 last:pb-0 animate-fade-in">
                    <span className="text-emerald-400 mr-2">{timeString}</span>
                    {messageString}
                  </div>
                );
              })
            ) : (
              <div className="text-slate-500 italic flex h-full items-center justify-center">
                Menunggu aktivitas deteksi kendaraan...
              </div>
            )}
          </div>
        </div>

        <div className="bg-slate-800 rounded-xl border border-slate-700 shadow-lg p-6 flex flex-col">
          <h2 className="text-xl font-semibold mb-4 text-slate-200 flex items-center gap-2">
            <svg className="w-5 h-5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
            </svg>
            Distribusi Kendaraan
          </h2>

          <div className="flex-1 w-full min-h-[250px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <XAxis dataKey="name" stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} allowDecimals={false} />
                <Tooltip
                  cursor={{ fill: '#334155' }}
                  contentStyle={{
                    backgroundColor: '#0f172a',
                    border: '1px solid #334155',
                    borderRadius: '8px'
                  }}
                  labelStyle={{ color: '#94a3b8', fontWeight: 'bold', marginBottom: '4px' }}
                  itemStyle={{ color: '#f8fafc', fontWeight: '600' }} // Memaksa teks "total : 12" menjadi putih terang
                />
                <Bar dataKey="total" radius={[4, 4, 0, 0]}>
                  {chartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* --- 3. KOMPONEN CUSTOM MODAL KONFIRMASI --- */}
      {showConfirmModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4 animate-fade-in">
          <div className="bg-slate-800 border border-slate-700 rounded-2xl max-w-md w-full p-6 shadow-2xl transform transition-all scale-100">

            {/* Ikon Peringatan */}
            <div className="flex items-center justify-center w-14 h-14 rounded-full bg-red-500/10 border border-red-500/20 text-red-400 mb-5 mx-auto">
              <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>

            {/* Teks Konfirmasi */}
            <h3 className="text-xl font-bold text-center text-white mb-2">
              Reset Semua Statistik?
            </h3>
            <p className="text-slate-400 text-center text-sm mb-6 leading-relaxed">
              Tindakan ini akan mengosongkan seluruh hitungan kendaraan, grafik analitik, dan riwayat aktivitas kembali ke nol. Data yang dihapus tidak dapat dikembalikan.
            </p>

            {/* Tombol Aksi */}
            <div className="flex gap-3">
              <button
                onClick={() => setShowConfirmModal(false)}
                disabled={isResetting}
                className="flex-1 px-4 py-2.5 bg-slate-700 hover:bg-slate-600 text-slate-200 rounded-xl font-medium transition-colors text-sm cursor-pointer"
              >
                Batal
              </button>
              <button
                onClick={confirmResetData}
                disabled={isResetting}
                className="flex-1 px-4 py-2.5 bg-red-500 hover:bg-red-600 text-white rounded-xl font-medium transition-colors text-sm shadow-lg shadow-red-500/25 flex items-center justify-center gap-2 cursor-pointer"
              >
                {isResetting ? "Mereset..." : "Ya, Reset Data"}
              </button>
            </div>

          </div>
        </div>
      )}

    </div>
  );
}