import React, { useEffect, useState } from 'react';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { TrendingUp, DollarSign, Activity, Award, Settings, Play, Square } from 'lucide-react';
import axios from 'axios';

const API_URL = 'http://localhost:8000';

interface PortfolioStats {
  total_trades: number;
  winning_trades: number;
  losing_trades: number;
  win_rate: number;
  total_profit: number;
  avg_return_pct: number;
  current_open_trades: number;
}

function App() {
  const [stats, setStats] = useState<PortfolioStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [botRunning, setBotRunning] = useState(false);
  const [chartData, setChartData] = useState<any[]>([]);

  useEffect(() => {
    fetchStats();
    const interval = setInterval(fetchStats, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/statistics/portfolio`);
      setStats(response.data);
      
      setChartData([
        { date: 'Jan', profit: 1200, trades: 4 },
        { date: 'Feb', profit: 3200, trades: 6 },
        { date: 'Mar', profit: 2800, trades: 5 },
        { date: 'Apr', profit: 3908, trades: 8 },
        { date: 'May', profit: 4800, trades: 7 },
        { date: 'Jun', profit: 3800, trades: 6 },
      ]);
    } catch (error) {
      console.error('Error fetching stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const pieData = [
    { name: 'Winning', value: stats?.winning_trades || 0, fill: '#10b981' },
    { name: 'Losing', value: stats?.losing_trades || 0, fill: '#ef4444' },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gradient-to-br from-slate-900 to-slate-800">
        <div className="text-center">
          <div className="w-16 h-16 bg-gradient-to-r from-orange-400 to-orange-600 rounded-lg mx-auto mb-4 flex items-center justify-center">
            <span className="text-white font-bold text-3xl">T</span>
          </div>
          <p className="text-white text-2xl font-bold">TradingBot</p>
          <p className="text-gray-400 mt-2">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800">
      {/* Header */}
      <header className="bg-slate-800 shadow-lg border-b border-slate-700 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-r from-orange-400 to-orange-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-lg">T</span>
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">TradingBot</h1>
              <p className="text-xs text-gray-400">v1.0.0 - Personal Edition</p>
            </div>
          </div>
          
          <div className="flex items-center gap-4">
            <div className={`px-4 py-2 rounded-lg text-sm font-semibold flex items-center gap-2 ${
              botRunning 
                ? 'bg-green-900 text-green-200' 
                : 'bg-red-900 text-red-200'
            }`}>
              <div className={`w-2 h-2 rounded-full ${
                botRunning ? 'bg-green-400' : 'bg-red-400'
              } animate-pulse`}></div>
              {botRunning ? 'Running' : 'Stopped'}
            </div>
            <button className="p-2 hover:bg-slate-700 rounded-lg transition">
              <Settings className="w-5 h-5 text-gray-300" />
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Total Profit */}
          <div className="bg-gradient-to-br from-slate-700 to-slate-800 rounded-lg p-6 shadow-lg border border-slate-600 hover:border-orange-400 transition">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-300 text-sm font-medium">Total Profit</p>
                <p className={`text-3xl font-bold mt-2 ${
                  (stats?.total_profit || 0) >= 0 ? 'text-green-400' : 'text-red-400'
                }`}>
                  ${stats?.total_profit.toFixed(2) || '0.00'}
                </p>
              </div>
              <DollarSign className="text-green-400 w-10 h-10 opacity-70" />
            </div>
          </div>

          {/* Win Rate */}
          <div className="bg-gradient-to-br from-slate-700 to-slate-800 rounded-lg p-6 shadow-lg border border-slate-600 hover:border-orange-400 transition">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-300 text-sm font-medium">Win Rate</p>
                <p className="text-3xl font-bold text-blue-400 mt-2">
                  {stats?.win_rate.toFixed(1) || '0.0'}%
                </p>
              </div>
              <TrendingUp className="text-blue-400 w-10 h-10 opacity-70" />
            </div>
          </div>

          {/* Total Trades */}
          <div className="bg-gradient-to-br from-slate-700 to-slate-800 rounded-lg p-6 shadow-lg border border-slate-600 hover:border-orange-400 transition">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-300 text-sm font-medium">Total Trades</p>
                <p className="text-3xl font-bold text-purple-400 mt-2">
                  {stats?.total_trades || '0'}
                </p>
              </div>
              <Activity className="text-purple-400 w-10 h-10 opacity-70" />
            </div>
          </div>

          {/* Open Trades */}
          <div className="bg-gradient-to-br from-slate-700 to-slate-800 rounded-lg p-6 shadow-lg border border-slate-600 hover:border-orange-400 transition">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-300 text-sm font-medium">Open Trades</p>
                <p className="text-3xl font-bold text-orange-400 mt-2">
                  {stats?.current_open_trades || '0'}
                </p>
              </div>
              <Award className="text-orange-400 w-10 h-10 opacity-70" />
            </div>
          </div>
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Profit Chart */}
          <div className="lg:col-span-2 bg-slate-700 rounded-lg p-6 shadow-lg border border-slate-600">
            <h2 className="text-xl font-bold text-white mb-4">📈 Monthly Performance</h2>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                <XAxis dataKey="date" stroke="#888" />
                <YAxis stroke="#888" />
                <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #475569' }} />
                <Legend />
                <Line type="monotone" dataKey="profit" stroke="#10b981" strokeWidth={2} dot={{ fill: '#10b981' }} />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Win/Loss Pie */}
          <div className="bg-slate-700 rounded-lg p-6 shadow-lg border border-slate-600">
            <h2 className="text-xl font-bold text-white mb-4">🎯 Win/Loss</h2>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie data={pieData} cx="50%" cy="50%" labelLine={false} label={({ name, value }) => `${name}: ${value}`} outerRadius={80} dataKey="value">
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                  ))}
                </Pie>
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-4 mb-8 flex-wrap">
          <button 
            onClick={() => setBotRunning(!botRunning)}
            className={`flex items-center gap-2 font-bold py-3 px-8 rounded-lg shadow-lg transition transform hover:scale-105 ${
              botRunning
                ? 'bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 text-white'
                : 'bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white'
            }`}
          >
            {botRunning ? (
              <>
                <Square className="w-5 h-5" /> Stop Bot
              </>
            ) : (
              <>
                <Play className="w-5 h-5" /> Start Bot
              </>
            )}
          </button>
          <button className="bg-gradient-to-r from-slate-600 to-slate-700 hover:from-slate-700 hover:to-slate-800 text-white font-bold py-3 px-8 rounded-lg shadow-lg transition flex items-center gap-2">
            <Settings className="w-5 h-5" /> Settings
          </button>
        </div>

        {/* Info Box */}
        <div className="bg-slate-700 border-l-4 border-orange-400 rounded-lg p-6 mb-8">
          <h3 className="text-white font-bold mb-2">ℹ️ Getting Started</h3>
          <ul className="text-gray-300 text-sm space-y-1">
            <li>✅ Configure your Binance API keys in Settings</li>
            <li>✅ Choose your trading strategies</li>
            <li>✅ Set risk management parameters</li>
            <li>✅ Click "Start Bot" to begin trading</li>
          </ul>
        </div>

        {/* Footer */}
        <footer className="text-center text-gray-400 text-sm py-4 border-t border-slate-700 mt-8">
          <p>TradingBot v1.0.0 | Personal Edition for Akrepyilan973</p>
          <p className="mt-2 text-xs">© 2024 All Rights Reserved | Powered by React + Electron + FastAPI</p>
        </footer>
      </main>
    </div>
  );
}

export default App;
