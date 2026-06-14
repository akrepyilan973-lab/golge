import React, { useEffect, useState } from 'react';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { TrendingUp, DollarSign, Activity, Award } from 'lucide-react';
import apiClient from '@/api/client';

interface PortfolioStats {
  total_trades: number;
  winning_trades: number;
  losing_trades: number;
  win_rate: number;
  total_profit: number;
  avg_return_pct: number;
  current_open_trades: number;
  largest_win: number;
  largest_loss: number;
  consecutive_wins: number;
  consecutive_losses: number;
}

export default function Dashboard() {
  const [stats, setStats] = useState<PortfolioStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [chartData, setChartData] = useState<any[]>([]);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await apiClient.get('/api/statistics/portfolio');
      setStats(response.data);
      
      // Mock chart data
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

  if (loading) {
    return <div className="flex items-center justify-center h-screen">Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 p-8">
      <h1 className="text-3xl font-bold text-white mb-8">Trading Dashboard</h1>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {/* Total Profit */}
        <div className="bg-slate-700 rounded-lg p-6 shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-300 text-sm">Total Profit</p>
              <p className="text-2xl font-bold text-green-400 mt-2">
                ${stats?.total_profit.toFixed(2)}
              </p>
            </div>
            <DollarSign className="text-green-400 w-8 h-8" />
          </div>
        </div>

        {/* Win Rate */}
        <div className="bg-slate-700 rounded-lg p-6 shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-300 text-sm">Win Rate</p>
              <p className="text-2xl font-bold text-blue-400 mt-2">
                {stats?.win_rate.toFixed(1)}%
              </p>
            </div>
            <TrendingUp className="text-blue-400 w-8 h-8" />
          </div>
        </div>

        {/* Total Trades */}
        <div className="bg-slate-700 rounded-lg p-6 shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-300 text-sm">Total Trades</p>
              <p className="text-2xl font-bold text-purple-400 mt-2">
                {stats?.total_trades}
              </p>
            </div>
            <Activity className="text-purple-400 w-8 h-8" />
          </div>
        </div>

        {/* Open Trades */}
        <div className="bg-slate-700 rounded-lg p-6 shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-300 text-sm">Open Trades</p>
              <p className="text-2xl font-bold text-orange-400 mt-2">
                {stats?.current_open_trades}
              </p>
            </div>
            <Award className="text-orange-400 w-8 h-8" />
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Profit Chart */}
        <div className="bg-slate-700 rounded-lg p-6 shadow-lg">
          <h2 className="text-xl font-bold text-white mb-4">Monthly Profit</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#444" />
              <XAxis dataKey="date" stroke="#888" />
              <YAxis stroke="#888" />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="profit" stroke="#10b981" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Trades Chart */}
        <div className="bg-slate-700 rounded-lg p-6 shadow-lg">
          <h2 className="text-xl font-bold text-white mb-4">Monthly Trades</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#444" />
              <XAxis dataKey="date" stroke="#888" />
              <YAxis stroke="#888" />
              <Tooltip />
              <Legend />
              <Bar dataKey="trades" fill="#6366f1" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}