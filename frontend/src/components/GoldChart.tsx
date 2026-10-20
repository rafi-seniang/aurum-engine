import { useEffect, useRef } from 'react';
import {
  createChart,
  CandlestickSeries,
  type IChartApi,
  type ISeriesApi,
  type CandlestickData,
  type Time
} from 'lightweight-charts';
import { BarChart2 } from 'lucide-react';

interface CandleData {
  time: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

interface GoldChartProps {
  candles: CandleData[];
  currentPrice: number;
}

export const GoldChart = ({ candles }: GoldChartProps) => {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const seriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null);

  useEffect(() => {
    if (!chartContainerRef.current) return;

    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: 340,
      layout: {
        background: { color: '#0E131F' },
        textColor: '#94A3B8',
        fontSize: 11,
      },
      grid: {
        vertLines: { color: 'rgba(30, 41, 59, 0.4)' },
        horzLines: { color: 'rgba(30, 41, 59, 0.4)' },
      },
      crosshair: {
        vertLine: { color: '#64748B', width: 1, style: 3 },
        horzLine: { color: '#64748B', width: 1, style: 3 },
      },
      timeScale: {
        borderColor: '#1E293B',
        timeVisible: true,
        secondsVisible: false,
      },
      rightPriceScale: {
        borderColor: '#1E293B',
        scaleMargins: {
          top: 0.1,
          bottom: 0.1,
        },
      },
    });

    const series = chart.addSeries(CandlestickSeries, {
      upColor: '#10B981',
      downColor: '#EF4444',
      borderVisible: false,
      wickUpColor: '#10B981',
      wickDownColor: '#EF4444',
    });

    chartRef.current = chart;
    seriesRef.current = series;

    const handleResize = () => {
      if (chartContainerRef.current && chartRef.current) {
        chartRef.current.applyOptions({
          width: chartContainerRef.current.clientWidth,
        });
      }
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
    };
  }, []);

  useEffect(() => {
    if (!seriesRef.current || !candles || candles.length === 0) return;

    const formatted: CandlestickData<Time>[] = [];
    let lastTime = 0;

    for (const c of candles) {
      if (c.time > lastTime) {
        formatted.push({
          time: c.time as Time,
          open: c.open,
          high: c.high,
          low: c.low,
          close: c.close,
        });
        lastTime = c.time;
      }
    }

    if (formatted.length > 0) {
      seriesRef.current.setData(formatted);
      chartRef.current?.timeScale().fitContent();
    }
  }, [candles]);

  return (
    <div className="bg-[#0E131F] border border-[#1E2638] rounded-xl overflow-hidden shadow-lg">
      <div className="px-4 py-2.5 border-b border-[#1E2638] flex items-center justify-between bg-[#121726]">
        <div className="flex items-center gap-2">
          <BarChart2 className="w-4 h-4 text-amber-400" />
          <span className="text-xs font-bold text-slate-200 uppercase tracking-wider font-mono">XAUUSD M5</span>
          <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 font-mono">5 MIN</span>
          <span className="text-[10px] px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-300 font-mono border border-amber-500/20">DONCHIAN BREAKOUT</span>
        </div>
        <div className="flex items-center gap-3 text-xs font-mono">
          <span className="text-slate-400 text-[11px]">Real-time Feed: <span className="text-emerald-400 font-semibold">Active</span></span>
        </div>
      </div>
      <div ref={chartContainerRef} className="w-full relative" />
    </div>
  );
};
