import { Bell, AlertTriangle, CheckCircle2 } from 'lucide-react';

interface NewsEventItem {
  title: string;
  country: string;
  date: string;
  impact: string;
  forecast?: string;
  previous?: string;
  timestamp: number;
}

interface NewsProps {
  isBlackout: boolean;
  blackoutReason: string;
  blackoutRemainingSec: number;
  nextEvent: NewsEventItem | null;
  secondsUntilNext: number;
  upcomingEvents: NewsEventItem[];
}

export const NewsBlackoutCard = ({
  isBlackout,
  blackoutReason,
  blackoutRemainingSec,
  nextEvent,
  secondsUntilNext,
  upcomingEvents
}: NewsProps) => {
  const formatCountdown = (totalSec: number) => {
    if (totalSec <= 0) return '00m 00s';
    const hrs = Math.floor(totalSec / 3600);
    const mins = Math.floor((totalSec % 3600) / 60);
    const secs = totalSec % 60;
    if (hrs > 0) {
      return `${hrs}h ${mins}m ${secs}s`;
    }
    return `${mins}m ${secs}s`;
  };

  return (
    <div className={`rounded-xl border transition-all ${
      isBlackout
        ? 'bg-amber-950/20 border-amber-500/50 shadow-[0_0_20px_rgba(245,158,11,0.15)]'
        : 'bg-[#0E131F] border-[#1E2638]'
    }`}>
      <div className="p-4">
        {/* Title Bar */}
        <div className="flex items-center justify-between pb-3 border-b border-[#1E2638]">
          <div className="flex items-center gap-2">
            <Bell className={`w-4 h-4 ${isBlackout ? 'text-amber-400 animate-bounce' : 'text-slate-400'}`} />
            <h2 className="text-xs font-bold uppercase tracking-wider font-mono text-slate-200">
              Macro News & Economic Calendar Gate
            </h2>
          </div>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#182030] text-slate-300">
            USD Feed
          </span>
        </div>

        {/* Status Banner */}
        {isBlackout ? (
          <div className="mt-3 p-3 rounded-lg bg-amber-500/15 border border-amber-500/40 flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold text-amber-300 uppercase tracking-wide">
                  Active News Blackout
                </span>
                <span className="text-xs font-mono font-semibold px-2 py-0.5 rounded bg-amber-500/20 text-amber-200">
                  {formatCountdown(blackoutRemainingSec)} remaining
                </span>
              </div>
              <p className="text-xs text-amber-200/90 mt-1 font-mono">{blackoutReason}</p>
              <p className="text-[11px] text-amber-300/70 mt-1">
                New order entries are strictly blocked to prevent lethal spread widening & slippage.
              </p>
            </div>
          </div>
        ) : (
          <div className="mt-3 p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
              <div>
                <span className="text-xs font-bold text-emerald-300 font-mono">Market Corridor Safe</span>
                <p className="text-[11px] text-slate-400">Spread is normal. Strategy execution permitted.</p>
              </div>
            </div>
            {nextEvent && (
              <div className="text-right font-mono">
                <div className="text-[10px] text-slate-400">Next US Event in</div>
                <div className="text-xs font-bold text-slate-200">{formatCountdown(secondsUntilNext)}</div>
              </div>
            )}
          </div>
        )}

        {/* Upcoming US Events List */}
        <div className="mt-4">
          <div className="text-[11px] font-mono uppercase text-slate-400 tracking-wider mb-2">
            Tracked High & Medium US Releases
          </div>
          <div className="space-y-1.5">
            {upcomingEvents && upcomingEvents.length > 0 ? (
              upcomingEvents.slice(0, 3).map((ev, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between px-3 py-2 rounded-lg bg-[#121724] border border-[#1E2638] text-xs font-mono"
                >
                  <div className="flex items-center gap-2 overflow-hidden">
                    <span
                      className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                        ev.impact === 'High'
                          ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                          : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                      }`}
                    >
                      {ev.impact.toUpperCase()}
                    </span>
                    <span className="truncate text-slate-200 font-medium">{ev.title}</span>
                  </div>
                  <div className="text-right text-[11px] text-slate-400 shrink-0 ml-2">
                    {new Date(ev.timestamp * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </div>
                </div>
              ))
            ) : (
              <div className="text-xs text-slate-400 py-2 text-center font-mono">
                No high-impact US news scheduled for today.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
