import React from 'react';
import { Wallet, TrendingUp, ShieldCheck, PieChart } from 'lucide-react';

interface MetricsProps {
  balance: number;
  equity: number;
  freeMargin: number;
  dailyPnl: number;
  dailyPnlPct: number;
  winRate: number;
  profitFactor: number;
  totalTrades: number;
}

export const PortfolioMetrics: React.FC<MetricsProps> = ({
  balance,
  equity,
  freeMargin,
  dailyPnl,
  dailyPnlPct,
  winRate,
  profitFactor,
  totalTrades
}) => {
  const isProfit = dailyPnl >= 0;

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-2.5">
      {/* Balance & Equity */}
      <div className="bg-[#0E131F] border border-[#1E2638] rounded-xl p-3.5 flex flex-col justify-between">
        <div className="flex items-center justify-between text-slate-400 text-xs">
          <span className="font-mono uppercase text-[11px] font-medium">Balance</span>
          <Wallet className="w-4 h-4 text-slate-400" />
        </div>
        <div className="mt-2">
          <div className="text-lg font-bold font-mono text-slate-100 tracking-tight">
            ${balance.toFixed(2)}
          </div>
          <div className="text-[11px] font-mono text-slate-400 mt-0.5">
            Equity: <span className="text-slate-200 font-semibold">${equity.toFixed(2)}</span>
          </div>
        </div>
      </div>

      {/* Daily PnL */}
      <div className="bg-[#0E131F] border border-[#1E2638] rounded-xl p-3.5 flex flex-col justify-between">
        <div className="flex items-center justify-between text-slate-400 text-xs">
          <span className="font-mono uppercase text-[11px] font-medium">Today's P&L</span>
          <TrendingUp className={`w-4 h-4 ${isProfit ? 'text-emerald-400' : 'text-rose-400'}`} />
        </div>
        <div className="mt-2">
          <div className={`text-lg font-bold font-mono tracking-tight ${isProfit ? 'text-emerald-400' : 'text-rose-400'}`}>
            {isProfit ? '+' : ''}${dailyPnl.toFixed(2)}
          </div>
          <div className={`text-[11px] font-mono mt-0.5 ${isProfit ? 'text-emerald-400/80' : 'text-rose-400/80'}`}>
            {isProfit ? '+' : ''}{dailyPnlPct.toFixed(2)}% of capital
          </div>
        </div>
      </div>

      {/* Margin Level */}
      <div className="bg-[#0E131F] border border-[#1E2638] rounded-xl p-3.5 flex flex-col justify-between">
        <div className="flex items-center justify-between text-slate-400 text-xs">
          <span className="font-mono uppercase text-[11px] font-medium">Free Margin</span>
          <ShieldCheck className="w-4 h-4 text-amber-400" />
        </div>
        <div className="mt-2">
          <div className="text-lg font-bold font-mono text-slate-100 tracking-tight">
            ${freeMargin.toFixed(2)}
          </div>
          <div className="text-[11px] font-mono text-slate-400 mt-0.5">
            1:200 Exness Buffer
          </div>
        </div>
      </div>

      {/* Quant Stats */}
      <div className="bg-[#0E131F] border border-[#1E2638] rounded-xl p-3.5 flex flex-col justify-between">
        <div className="flex items-center justify-between text-slate-400 text-xs">
          <span className="font-mono uppercase text-[11px] font-medium">Win Rate</span>
          <PieChart className="w-4 h-4 text-cyan-400" />
        </div>
        <div className="mt-2">
          <div className="text-lg font-bold font-mono text-slate-100 tracking-tight">
            {winRate}%
          </div>
          <div className="text-[11px] font-mono text-slate-400 mt-0.5">
            PF: <span className="text-slate-200 font-semibold">{profitFactor}</span> | {totalTrades} trades
          </div>
        </div>
      </div>
    </div>
  );
};
