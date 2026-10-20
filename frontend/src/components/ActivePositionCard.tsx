import React from 'react';
import { Target, Shield, ArrowUpRight, ArrowDownRight, Compass } from 'lucide-react';

interface PositionData {
  id: string;
  symbol: string;
  side: string;
  lot: number;
  entry_price: number;
  current_price: number;
  sl_price: number;
  tp_price: number;
  floating_pnl: number;
  open_time: number;
  reason: string;
}

interface ActivePositionProps {
  position: PositionData | null;
  strategySignalReason?: string;
}

export const ActivePositionCard: React.FC<ActivePositionProps> = ({ position, strategySignalReason }) => {
  if (!position) {
    return (
      <div className="bg-[#0E131F] border border-[#1E2638] rounded-xl p-4">
        <div className="flex items-center gap-2 pb-2.5 border-b border-[#1E2638]">
          <Compass className="w-4 h-4 text-cyan-400" />
          <h2 className="text-xs font-bold uppercase tracking-wider font-mono text-slate-200">
            Active Position & Tactical Scanner
          </h2>
        </div>
        <div className="mt-3.5 py-4 flex flex-col items-center justify-center text-center">
          <div className="w-9 h-9 rounded-full bg-slate-800/60 border border-slate-700/60 flex items-center justify-center text-slate-400 mb-2">
            <Compass className="w-4 h-4 animate-spin" />
          </div>
          <span className="text-xs font-semibold text-slate-300 font-mono">No Open Exposure (Flat)</span>
          <p className="text-[11px] text-slate-400 max-w-sm mt-1 font-mono">
            {strategySignalReason || "Strategy engine is scanning M5 Donchian channels & ATR thresholds for high-confluence entry..."}
          </p>
        </div>
      </div>
    );
  }

  const isBuy = position.side === 'BUY';
  const isPnlPositive = position.floating_pnl >= 0;

  return (
    <div className="bg-[#0E131F] border border-cyan-500/30 rounded-xl p-4 shadow-[0_0_15px_rgba(6,182,212,0.07)]">
      <div className="flex items-center justify-between pb-3 border-b border-[#1E2638]">
        <div className="flex items-center gap-2">
          <div className={`p-1 rounded font-bold flex items-center gap-1 text-xs font-mono ${
            isBuy ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
          }`}>
            {isBuy ? <ArrowUpRight className="w-3.5 h-3.5" /> : <ArrowDownRight className="w-3.5 h-3.5" />}
            <span>{position.side} {position.lot} LOT</span>
          </div>
          <span className="text-xs font-bold font-mono text-slate-100">{position.symbol}</span>
        </div>

        <div className="text-right font-mono">
          <div className={`text-base font-bold ${isPnlPositive ? 'text-emerald-400' : 'text-rose-400'}`}>
            {isPnlPositive ? '+' : ''}${position.floating_pnl.toFixed(2)}
          </div>
          <div className="text-[10px] text-slate-400">Floating P&L</div>
        </div>
      </div>

      {/* Entry, Current, SL, TP Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mt-3 pt-1 text-xs font-mono">
        <div className="bg-[#121724] border border-[#1E2638] rounded-lg p-2">
          <div className="text-[10px] text-slate-400">Entry Price</div>
          <div className="text-xs font-bold text-slate-200 mt-0.5">${position.entry_price.toFixed(2)}</div>
        </div>

        <div className="bg-[#121724] border border-[#1E2638] rounded-lg p-2">
          <div className="text-[10px] text-slate-400">Current Price</div>
          <div className="text-xs font-bold text-slate-200 mt-0.5">${position.current_price.toFixed(2)}</div>
        </div>

        <div className="bg-[#121724] border border-[#1E2638] rounded-lg p-2">
          <div className="text-[10px] text-rose-400 flex items-center gap-1">
            <Shield className="w-3 h-3" /> Stop Loss
          </div>
          <div className="text-xs font-bold text-rose-300 mt-0.5">${position.sl_price.toFixed(2)}</div>
        </div>

        <div className="bg-[#121724] border border-[#1E2638] rounded-lg p-2">
          <div className="text-[10px] text-emerald-400 flex items-center gap-1">
            <Target className="w-3 h-3" /> Take Profit
          </div>
          <div className="text-xs font-bold text-emerald-300 mt-0.5">${position.tp_price.toFixed(2)}</div>
        </div>
      </div>

      {/* Trade Logic Reasoning */}
      <div className="mt-3 p-2.5 rounded-lg bg-[#141A29] border border-[#1E2638] text-[11px] font-mono text-slate-300">
        <span className="text-cyan-400 font-semibold">Entry Thesis: </span>
        {position.reason}
      </div>
    </div>
  );
};
