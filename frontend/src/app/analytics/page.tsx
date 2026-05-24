'use client';

import { useEffect, useState } from 'react';
import { predictionsAPI } from '@/services/api';
import { Prediction } from '@/types';
import toast from 'react-hot-toast';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

export default function AnalyticsPage() {
  const [analytics, setAnalytics] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    try {
      const { data } = await predictionsAPI.getAnalytics();
      setAnalytics(data);
    } catch (err) {
      console.error('Analytics load error', err);
      toast.error('Failed to load analytics');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-100 flex items-center justify-center">
        <div className="text-2xl text-gray-600">Loading analytics...</div>
      </div>
    );
  }

  if (!analytics) {
    return (
      <div className="min-h-screen bg-slate-100 flex items-center justify-center">
        <div className="text-2xl text-gray-600">No data available</div>
      </div>
    );
  }

  // Defensive data shaping
  const priceStats = analytics?.price_stats ?? { avg_price: 0, min_price: 0, max_price: 0 };
  const avgPriceNum = Number(priceStats.avg_price ?? 0);
  const minPriceNum = Number(priceStats.min_price ?? 0);
  const maxPriceNum = Number(priceStats.max_price ?? 0);

  const byDistrictRaw = analytics?.by_district ?? [];
  const byDistrict = Array.isArray(byDistrictRaw)
    ? byDistrictRaw.map((d: any) => ({
        district: d?.district ?? '',
        avg_price: Number(d?.avg_price ?? 0),
        count: Number(d?.count ?? 0),
      }))
    : [];

  return (
    <div className="min-h-screen bg-slate-100 py-8">
      <div className="max-w-7xl mx-auto px-4">
        <h1 className="text-4xl font-bold text-gray-900 mb-8">Analytics</h1>

        {/* Stats Cards */}
        <div className="grid md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-gray-600 text-sm">Total Predictions</p>
            <p className="text-3xl font-bold text-blue-600">{analytics.total_predictions ?? 0}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-gray-600 text-sm">Average Price</p>
            <p className="text-3xl font-bold text-green-600">${avgPriceNum.toFixed(0)}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-gray-600 text-sm">Min Price</p>
            <p className="text-3xl font-bold text-yellow-600">${minPriceNum.toFixed(0)}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-gray-600 text-sm">Max Price</p>
            <p className="text-3xl font-bold text-red-600">${maxPriceNum.toFixed(0)}</p>
          </div>
        </div>

        {/* Charts */}
        <div className="grid md:grid-cols-2 gap-8">
          {/* District Distribution */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold mb-4">By District</h2>
            {byDistrict.length === 0 ? (
              <div className="text-gray-600">No district data available</div>
            ) : (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={byDistrict}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="district" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="avg_price" fill="#3B82F6" />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>

          {/* Count by District */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold mb-4">Predictions by District</h2>
            {byDistrict.length === 0 ? (
              <div className="text-gray-600">No district data available</div>
            ) : (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={byDistrict}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="district" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="count" fill="#8B5CF6" />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
