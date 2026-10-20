import { Activity, ShieldAlert, PauseCircle } from 'lucide-react';

interface HeaderProps {
  status: string;
  price: number;
  bid: number;
  ask: number;
  spreadPoints: number;
  dayChangePercent: number;
}

export const Header = ({
  status,
  price,
  bid,
  ask,
  spreadPoints,
  dayChangePercent,
}: HeaderProps) => {
  const getStatusBadge = () => {
    switch (status) {
      case 'ACTIVE':
        return (
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-[11px] font-mono font-medium tracking-wide">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse-dot" />
            <span>ACTIVE // SCANNING</span>
          </div>
        );
      case 'NEWS_BLACKOUT':
        return (
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-amber-500/10 border border-amber-500/30 text-amber-400 text-[11px] font-mono font-medium tracking-wide">
            <ShieldAlert className="w-3.5 h-3.5 text-amber-400" />
            <span>NEWS LOCKOUT // HALTED</span>
          </div>
        );
      case 'CIRCUIT_BREAKER':
        return (
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-rose-500/10 border border-rose-500/40 text-rose-400 text-[11px] font-mono font-bold tracking-wide animate-pulse">
            <span className="w-1.5 h-1.5 rounded-full bg-rose-500" />
            <span>DRAWDOWN CIRCUIT // TRIPPED</span>
          </div>
        );
      case 'PAUSED':
        return (
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-slate-800/80 border border-slate-700/60 text-slate-400 text-[11px] font-mono font-medium tracking-wide">
            <PauseCircle className="w-3.5 h-3.5" />
            <span>MANUAL HALT // PAUSED</span>
          </div>
        );
      case 'EMERGENCY_STOP':
        return (
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-red-600/20 border border-red-500 text-red-400 text-[11px] font-mono font-bold tracking-wide">
            <ShieldAlert className="w-3.5 h-3.5" />
            <span>EMERGENCY HALT</span>
          </div>
        );
      default:
        return (
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-slate-800 text-slate-300 text-[11px] font-mono">
            <Activity className="w-3 h-3" />
            <span>{status}</span>
          </div>
        );
    }
  };

  const isPositive = dayChangePercent >= 0;

  return (
    <header className="border-b border-[#1E2638] bg-[#0E121B]/95 backdrop-blur-md sticky top-0 z-50 px-4 py-3">
      <div className="max-w-6xl mx-auto flex flex-col md:flex-row md:items-center justify-between gap-3">
        {/* Top bar: Brand + Status */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-amber-500/10 border border-amber-500/30 flex items-center justify-center font-bold text-amber-400 shadow-inner font-mono">
              Au
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <h1 className="text-sm font-bold tracking-wider text-slate-100 uppercase font-mono">Aurum Terminal</h1>
                <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-[#182030] text-amber-400/90 border border-amber-500/20">QUANT LAB</span>
              </div>
              <p className="text-[10px] text-slate-400 font-mono">XAUUSD Volatility & Liquidity Engine</p>
            </div>
          </div>
          <div>{getStatusBadge()}</div>
        </div>

        {/* Live Price Ticker */}
        <div className="flex items-center justify-between md:justify-end gap-4 bg-[#121724] border border-[#1E2638] rounded-xl px-3.5 py-2">
          <div>
            <div className="text-[10px] text-slate-400 uppercase tracking-wider font-mono flex items-center gap-1.5">
              <span>XAU/USD Spot</span>
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 inline-block animate-ping" />
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-xl font-bold font-mono text-slate-50 tracking-tight">
                ${price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </span>
              <span className={`text-xs font-mono font-medium ${isPositive ? 'text-emerald-400' : 'text-rose-400'}`}>
                {isPositive ? '+' : ''}{dayChangePercent}%
              </span>
            </div>
          </div>

          <div className="border-l border-[#1E2638] pl-3 text-right font-mono">
            <div className="text-[10px] text-slate-400">
              Spread: <span className="text-amber-400 font-semibold">{spreadPoints} pts</span>
            </div>
            <div className="text-[10px] text-slate-300">
              Bid {bid.toFixed(2)} | Ask {ask.toFixed(2)}
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};
