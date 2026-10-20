import { useState } from 'react';
import { Play, Pause, OctagonX, RotateCcw } from 'lucide-react';

interface ControlActionsProps {
  status: string;
  onRefresh: () => void;
}

export const ControlActions = ({ status, onRefresh }: ControlActionsProps) => {
  const [loading, setLoading] = useState(false);

  const handleAction = async (endpoint: string) => {
    try {
      setLoading(true);
      await fetch(`/api/control/${endpoint}`, { method: 'POST' });
      onRefresh();
    } catch (err) {
      console.error('Failed to trigger action:', err);
    } finally {
      setLoading(false);
    }
  };

  const isPaused = status === 'PAUSED' || status === 'EMERGENCY_STOP';

  return (
    <div className="bg-[#0E131F] border border-[#1E2638] rounded-xl p-4">
      <div className="flex items-center justify-between pb-3 border-b border-[#1E2638]">
        <h2 className="text-xs font-bold uppercase tracking-wider font-mono text-slate-200">
          Execution Cockpit & Command Controls
        </h2>
        <span className="text-[10px] font-mono text-slate-400">Direct IPC Gateway</span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5 mt-3">
        {/* Pause / Resume Button */}
        {isPaused ? (
          <button
            onClick={() => handleAction('resume')}
            disabled={loading}
            className="flex items-center justify-center gap-2 py-3 px-4 rounded-lg font-mono text-xs font-bold bg-emerald-600 hover:bg-emerald-500 text-white active:scale-98 transition-all cursor-pointer shadow-md"
          >
            <Play className="w-3.5 h-3.5 fill-current" />
            <span>ENGAGE ENGINE</span>
          </button>
        ) : (
          <button
            onClick={() => handleAction('pause')}
            disabled={loading}
            className="flex items-center justify-center gap-2 py-3 px-4 rounded-lg font-mono text-xs font-semibold bg-[#161D2C] hover:bg-[#1E273A] text-amber-300 border border-amber-500/30 active:scale-98 transition-all cursor-pointer"
          >
            <Pause className="w-3.5 h-3.5 fill-current" />
            <span>HALT ENGINE</span>
          </button>
        )}

        {/* Liquidate All Positions (Institutional Emergency Stop) */}
        <button
          onClick={() => {
            if (window.confirm("CONFIRM EMERGENCY LIQUIDATION:\nClose all active open positions and freeze order execution?")) {
              handleAction('emergency-flatten');
            }
          }}
          disabled={loading}
          className="flex items-center justify-center gap-2 py-3 px-4 rounded-lg font-mono text-xs font-semibold bg-rose-950/40 hover:bg-rose-900/50 text-rose-300 border border-rose-500/40 active:scale-98 transition-all cursor-pointer"
        >
          <OctagonX className="w-3.5 h-3.5 text-rose-400" />
          <span>LIQUIDATE ALL</span>
        </button>

        {/* Reset Demo $100 */}
        <button
          onClick={() => {
            if (window.confirm("Reset virtual account ledger back to $100.00 baseline?")) {
              handleAction('reset-demo');
            }
          }}
          disabled={loading}
          className="flex items-center justify-center gap-2 py-3 px-4 rounded-lg font-mono text-xs font-medium bg-[#121724] hover:bg-[#182030] text-slate-300 border border-[#1E2638] active:scale-98 transition-all cursor-pointer"
        >
          <RotateCcw className="w-3.5 h-3.5 text-slate-400" />
          <span>Reset Balance ($100)</span>
        </button>
      </div>
    </div>
  );
};
