import { History, Terminal } from 'lucide-react';

interface TradeRecordItem {
  id: string;
  symbol: string;
  side: string;
  lot: number;
  entry_price: number;
  exit_price: number;
  pnl: number;
  open_time: number;
  close_time: number;
  close_reason: string;
}

interface LogItem {
  time: number;
  time_str: string;
  level: string;
  message: string;
}

interface ExecutionLogProps {
  recentTrades: TradeRecordItem[];
  logs: LogItem[];
}

export const ExecutionLog = ({ recentTrades, logs }: ExecutionLogProps) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
      {/* Closed Trades History */}
      <div className="bg-[#0E131F] border border-[#1E2638] rounded-xl p-4">
        <div className="flex items-center justify-between pb-3 border-b border-[#1E2638]">
          <div className="flex items-center gap-2">
            <History className="w-4 h-4 text-amber-400" />
            <h2 className="text-xs font-bold uppercase tracking-wider font-mono text-slate-200">
              Closed Trades Audit Trail
            </h2>
          </div>
          <span className="text-[10px] font-mono text-slate-400">{recentTrades.length} records</span>
        </div>

        <div className="mt-3 space-y-2 max-h-56 overflow-y-auto pr-1">
          {recentTrades && recentTrades.length > 0 ? (
            recentTrades.map((t) => {
              const isProfit = t.pnl > 0;
              return (
                <div
                  key={t.id}
                  className="p-2.5 rounded-lg bg-[#121724] border border-[#1E2638] flex items-center justify-between text-xs font-mono"
                >
                  <div className="flex items-center gap-2">
                    <span
                      className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                        t.side === 'BUY'
                          ? 'bg-emerald-500/20 text-emerald-400'
                          : 'bg-rose-500/20 text-rose-400'
                      }`}
                    >
                      {t.side} {t.lot}L
                    </span>
                    <div>
                      <div className="text-slate-200 font-semibold">{t.symbol}</div>
                      <div className="text-[10px] text-slate-400">
                        {t.entry_price.toFixed(2)} → {t.exit_price.toFixed(2)}
                      </div>
                    </div>
                  </div>

                  <div className="text-right">
                    <div className={`font-bold ${isProfit ? 'text-emerald-400' : 'text-rose-400'}`}>
                      {isProfit ? '+' : ''}${t.pnl.toFixed(2)}
                    </div>
                    <div className="text-[9px] text-slate-400">{t.close_reason}</div>
                  </div>
                </div>
              );
            })
          ) : (
            <div className="py-8 text-center text-xs text-slate-500 font-mono">
              No executed trades yet. Bot is scanning.
            </div>
          )}
        </div>
      </div>

      {/* Real-time Engine Logs */}
      <div className="bg-[#0E131F] border border-[#1E2638] rounded-xl p-4">
        <div className="flex items-center justify-between pb-3 border-b border-[#1E2638]">
          <div className="flex items-center gap-2">
            <Terminal className="w-4 h-4 text-cyan-400" />
            <h2 className="text-xs font-bold uppercase tracking-wider font-mono text-slate-200">
              Quant Engine Telemetry
            </h2>
          </div>
          <span className="text-[10px] font-mono text-emerald-400 flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" /> Live
          </span>
        </div>

        <div className="mt-3 font-mono text-[11px] space-y-1.5 max-h-56 overflow-y-auto pr-1">
          {logs && logs.length > 0 ? (
            logs.map((l, idx) => (
              <div key={idx} className="flex items-start gap-2 text-slate-400 leading-tight">
                <span className="text-slate-500 shrink-0 text-[10px]">{l.time_str}</span>
                <span
                  className={`text-[10px] px-1 rounded font-bold shrink-0 ${
                    l.level === 'ORDER'
                      ? 'bg-emerald-500/20 text-emerald-400'
                      : l.level === 'WARN'
                      ? 'bg-amber-500/20 text-amber-400'
                      : l.level === 'CRITICAL'
                      ? 'bg-rose-500/20 text-rose-400'
                      : 'bg-slate-800 text-slate-400'
                  }`}
                >
                  {l.level}
                </span>
                <span className="text-slate-300 break-all">{l.message}</span>
              </div>
            ))
          ) : (
            <div className="py-8 text-center text-xs text-slate-500">Connecting to telemetry stream...</div>
          )}
        </div>
      </div>
    </div>
  );
};
