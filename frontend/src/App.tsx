import { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { GoldChart } from './components/GoldChart';
import { NewsBlackoutCard } from './components/NewsBlackoutCard';
import { PortfolioMetrics } from './components/PortfolioMetrics';
import { ActivePositionCard } from './components/ActivePositionCard';
import { ControlActions } from './components/ControlActions';
import { ExecutionLog } from './components/ExecutionLog';
import { Download, Smartphone, Settings } from 'lucide-react';

export function App() {
  const [data, setData] = useState<any>(null);
  const [candles, setCandles] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [deferredPrompt, setDeferredPrompt] = useState<any>(null);
  const [apiBase, setApiBase] = useState(() => localStorage.getItem('quantgold_api_base') || '');
  const [showConfig, setShowConfig] = useState(false);
  const [configInput, setConfigInput] = useState('');

  // Capture PWA install prompt for Android
  useEffect(() => {
    const handleBeforeInstall = (e: any) => {
      e.preventDefault();
      setDeferredPrompt(e);
    };
    window.addEventListener('beforeinstallprompt', handleBeforeInstall);
    return () => window.removeEventListener('beforeinstallprompt', handleBeforeInstall);
  }, []);

  const handleInstallClick = () => {
    if (deferredPrompt) {
      deferredPrompt.prompt();
      deferredPrompt.userChoice.then((choiceResult: any) => {
        if (choiceResult.outcome === 'accepted') {
          console.log('User installed the PWA app');
        }
        setDeferredPrompt(null);
      });
    } else {
      alert("To install as an App on Android:\n1. Open this link in Chrome\n2. Tap the Chrome 3-dots menu (⋮)\n3. Tap 'Add to Home screen' or 'Install App'");
    }
  };

  const getUrl = (path: string) => {
    if (!apiBase) return path;
    const base = apiBase.replace(/\/+$/, '');
    return `${base}${path}`;
  };

  const fetchStatus = async () => {
    try {
      const res = await fetch(getUrl('/api/status'));
      if (res.ok) {
        const json = await res.json();
        setData(json);
      }
    } catch (err) {
      console.error('Failed to fetch status:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchCandles = async () => {
    try {
      const res = await fetch(getUrl('/api/candles'));
      if (res.ok) {
        const json = await res.json();
        setCandles(json.candles || []);
      }
    } catch (err) {
      console.error('Failed to fetch candles:', err);
    }
  };

  const handleSaveApiBase = (newUrl: string) => {
    const trimmed = newUrl.trim();
    setApiBase(trimmed);
    localStorage.setItem('quantgold_api_base', trimmed);
    setShowConfig(false);
    fetchStatus();
    fetchCandles();
  };

  useEffect(() => {
    fetchStatus();
    fetchCandles();

    // Polling intervals: status every 3s, candles every 10s
    const statusInterval = setInterval(fetchStatus, 3000);
    const candleInterval = setInterval(fetchCandles, 10000);

    return () => {
      clearInterval(statusInterval);
      clearInterval(candleInterval);
    };
  }, [apiBase]);

  if (loading && !data) {
    return (
      <div className="min-h-screen bg-[#0B0E14] flex flex-col items-center justify-center text-slate-400 font-mono text-xs p-4">
        <div className="w-8 h-8 rounded-full border-2 border-amber-500 border-t-transparent animate-spin mb-3" />
        <span className="text-center">INITIALIZING QUANTGOLD OS ENGINE...</span>
        {apiBase && <span className="text-[10px] text-slate-500 mt-1">Connecting to: {apiBase}</span>}
        <button
          onClick={() => {
            const val = prompt('Enter Server / Tunnel URL (e.g. https://xxx.trycloudflare.com):', apiBase);
            if (val !== null) handleSaveApiBase(val);
          }}
          className="mt-4 px-3 py-1.5 rounded bg-[#1E2638] text-slate-300 text-xs font-mono hover:bg-[#2A344D]"
        >
          Change Server URL
        </button>
      </div>
    );
  }

  const market = data?.market || {
    price: 2650.0,
    bid: 2649.92,
    ask: 2650.08,
    spread_points: 16,
    day_change_percent: 0.0,
    last_updated: Date.now() / 1000,
  };

  const news = data?.news || {
    is_blackout: false,
    blackout_reason: '',
    blackout_remaining_seconds: 0,
    next_event: null,
    seconds_until_next_event: 0,
    upcoming_events: [],
  };

  const broker = data?.broker || {
    balance: 100.0,
    equity: 100.0,
    free_margin: 100.0,
    daily_pnl: 0.0,
    daily_pnl_pct: 0.0,
    win_rate: 0.0,
    profit_factor: 1.0,
    total_trades: 0,
    open_positions: [],
    recent_trades: [],
  };

  const activePosition = broker.open_positions?.[0] || null;

  return (
    <div className="min-h-screen bg-[#0B0E14] text-slate-100 flex flex-col selection:bg-amber-500/20">
      {/* PWA / APK Notification Bar */}
      <div className="bg-[#121824] border-b border-[#1E2638] px-4 py-2 flex items-center justify-between text-xs">
        <div className="flex items-center gap-2 text-slate-300">
          <Smartphone className="w-3.5 h-3.5 text-amber-400" />
          <span className="font-mono text-[11px]">Android App Ready • Instant Mobile Cockpit</span>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => {
              setConfigInput(apiBase);
              setShowConfig(!showConfig);
            }}
            title="Configure Server Endpoint"
            className="p-1 rounded bg-[#1E2638] hover:bg-[#2A344D] text-slate-400 hover:text-slate-200 transition-all cursor-pointer"
          >
            <Settings className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={handleInstallClick}
            className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold font-mono text-[10px] uppercase shadow transition-all cursor-pointer"
          >
            <Download className="w-3 h-3" />
            <span>Install App</span>
          </button>
        </div>
      </div>

      {/* Optional Server URL config modal */}
      {showConfig && (
        <div className="bg-[#182030] border-b border-[#2A364F] px-4 py-2.5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 text-xs font-mono">
          <div className="text-slate-300">
            <span>Server Endpoint: </span>
            <span className="text-amber-400">{apiBase || 'Local (Same Host)'}</span>
          </div>
          <div className="flex items-center gap-2 w-full sm:w-auto">
            <input
              type="text"
              placeholder="https://xxx.trycloudflare.com"
              value={configInput}
              onChange={(e) => setConfigInput(e.target.value)}
              className="bg-[#0B0E14] border border-[#2A364F] rounded px-2.5 py-1 text-slate-100 text-xs w-full sm:w-64 focus:outline-none focus:border-amber-500"
            />
            <button
              onClick={() => handleSaveApiBase(configInput)}
              className="px-3 py-1 rounded bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold"
            >
              Save
            </button>
            <button
              onClick={() => handleSaveApiBase('')}
              className="px-2 py-1 rounded bg-slate-700 hover:bg-slate-600 text-slate-200"
            >
              Reset
            </button>
          </div>
        </div>
      )}

      {/* Main Header */}
      <Header
        status={data?.status || 'ACTIVE'}
        price={market.price}
        bid={market.bid}
        ask={market.ask}
        spreadPoints={market.spread_points}
        dayChangePercent={market.day_change_percent}
      />

      {/* Dashboard Body */}
      <main className="flex-1 max-w-6xl w-full mx-auto p-3 sm:p-4 space-y-3">
        {/* Portfolio Stats */}
        <PortfolioMetrics
          balance={broker.balance}
          equity={broker.equity}
          freeMargin={broker.free_margin}
          dailyPnl={broker.daily_pnl}
          dailyPnlPct={broker.daily_pnl_pct}
          winRate={broker.win_rate}
          profitFactor={broker.profit_factor}
          totalTrades={broker.total_trades}
        />

        {/* Chart + News Blackout Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-3">
          <div className="lg:col-span-2">
            <GoldChart candles={candles} currentPrice={market.price} />
          </div>
          <div>
            <NewsBlackoutCard
              isBlackout={news.is_blackout}
              blackoutReason={news.blackout_reason}
              blackoutRemainingSec={news.blackout_remaining_seconds}
              nextEvent={news.next_event}
              secondsUntilNext={news.seconds_until_next_event}
              upcomingEvents={news.upcoming_events}
            />
          </div>
        </div>

        {/* Active Trade / Scanner + Controls */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
          <ActivePositionCard
            position={activePosition}
            strategySignalReason={data?.strategy?.reason}
          />
          <ControlActions
            status={data?.status || 'ACTIVE'}
            onRefresh={fetchStatus}
          />
        </div>

        {/* Trade History & Engine Logs */}
        <ExecutionLog
          recentTrades={broker.recent_trades || []}
          logs={data?.logs || []}
        />
      </main>

      {/* Footer */}
      <footer className="border-t border-[#1E2638] bg-[#0E121B] px-4 py-3 text-center text-[11px] font-mono text-slate-500">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>AURUM ENGINE • Systematic Trading Research & Execution</span>
          <div className="flex items-center gap-3">
            <span className="text-slate-400">Risk Model: 0.5% ATR Parity</span>
            <span>•</span>
            <span className="text-slate-400">Exness Pro Spread Model</span>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
