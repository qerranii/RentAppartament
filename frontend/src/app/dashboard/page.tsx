'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/auth';
import { predictionsAPI } from '@/services/api';
import { Prediction, PredictionCreate } from '@/types';
import toast from 'react-hot-toast';
import Link from 'next/link';

export default function DashboardPage() {
  const { user } = useAuthStore();
  const router = useRouter();
  const [predictions, setPredictions] = useState<Prediction[]>([]);
  const [loading, setLoading] = useState(false);
  
  const [formData, setFormData] = useState({
    region: 'Москва и МО',
    address: 'Москва, ул. Примерная, 1',
    square: 50,
    floor: 2,
    max_floor: 5,
    metro: 'Красная площадь',
    rooms: 2,
    time: 10,
    time_type: 'walk',
    description: 'Комфортная квартира',
  });

  useEffect(() => {
    if (!user) router.push('/auth/login');
    loadPredictions();
  }, [user, router]);

  const loadPredictions = async () => {
    try {
      const { data } = await predictionsAPI.list(0, 20);
      setPredictions(data);
    } catch (err) {
      toast.error('Failed to load predictions');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const payload = {
        title: formData.address,
        region: formData.region,
        address: formData.address,
        square: Number(formData.square) || 50,
        floor: Number(formData.floor) || 1,
        max_floor: Number(formData.max_floor) || 5,
        metro: formData.metro,
        rooms: String(formData.rooms),
        time: Number(formData.time) || 10,
        time_type: formData.time_type,
        description: formData.description,
      };

      console.log('Sending payload:', payload);
      const { data } = await predictionsAPI.create(payload);
      
      const price = (data as any)?.predicted_price ?? (data as any)?.prediction ?? (data as any)?.price;
      if (price) {
        toast.success(`✅ Прогноз создан! Цена: ₽${Math.round(price).toLocaleString('ru-RU')}`);
      }
      
      await loadPredictions();
      
      setFormData({
        region: 'Москва и МО',
        address: 'Москва, ул. Примерная, 1',
        square: 50,
        floor: 2,
        max_floor: 5,
        metro: 'Красная площадь',
        rooms: 2,
        time: 10,
        time_type: 'walk',
        description: 'Комфортная квартира',
      });
    } catch (err: any) {
      toast.error(`❌ ${err?.message || 'Ошибка при создании прогноза'}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      <header className="bg-slate-800 border-b border-slate-700 py-4">
        <div className="max-w-7xl mx-auto px-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold">🏠 Прогноз цены на аренду</h1>
          <Link href="/auth/logout" className="text-red-400 hover:text-red-300">
            Выход
          </Link>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Form */}
          <div className="lg:col-span-1">
            <form onSubmit={handleSubmit} className="bg-slate-800 rounded-lg p-6 space-y-4">
              <h2 className="text-xl font-bold mb-6">📝 Заполните данные</h2>

              <div>
                <label className="block text-gray-300 text-sm font-medium mb-2">Регион</label>
                <input
                  type="text"
                  value={formData.region}
                  onChange={(e) => setFormData({...formData, region: e.target.value})}
                  className="w-full px-3 py-2 bg-slate-700 text-white border border-slate-600 rounded focus:outline-none focus:border-blue-500"
                  placeholder="Москва и МО"
                />
              </div>

              <div>
                <label className="block text-gray-300 text-sm font-medium mb-2">Адрес</label>
                <input
                  type="text"
                  value={formData.address}
                  onChange={(e) => setFormData({...formData, address: e.target.value})}
                  className="w-full px-3 py-2 bg-slate-700 text-white border border-slate-600 rounded focus:outline-none focus:border-blue-500"
                  placeholder="Москва, ул. Примерная, 1"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-gray-300 text-sm font-medium mb-2">Площадь м²</label>
                  <input
                    type="number"
                    min="5"
                    max="500"
                    value={formData.square}
                    onChange={(e) => setFormData({...formData, square: Number(e.target.value)})}
                    className="w-full px-3 py-2 bg-slate-700 text-white border border-slate-600 rounded focus:outline-none focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-gray-300 text-sm font-medium mb-2">Комнат</label>
                  <input
                    type="number"
                    min="1"
                    max="10"
                    value={formData.rooms}
                    onChange={(e) => setFormData({...formData, rooms: Number(e.target.value)})}
                    className="w-full px-3 py-2 bg-slate-700 text-white border border-slate-600 rounded focus:outline-none focus:border-blue-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-gray-300 text-sm font-medium mb-2">Этаж</label>
                  <input
                    type="number"
                    min="1"
                    max="100"
                    value={formData.floor}
                    onChange={(e) => setFormData({...formData, floor: Number(e.target.value)})}
                    className="w-full px-3 py-2 bg-slate-700 text-white border border-slate-600 rounded focus:outline-none focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-gray-300 text-sm font-medium mb-2">Макс этажей</label>
                  <input
                    type="number"
                    min="1"
                    max="100"
                    value={formData.max_floor}
                    onChange={(e) => setFormData({...formData, max_floor: Number(e.target.value)})}
                    className="w-full px-3 py-2 bg-slate-700 text-white border border-slate-600 rounded focus:outline-none focus:border-blue-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-gray-300 text-sm font-medium mb-2">Метро</label>
                <input
                  type="text"
                  value={formData.metro}
                  onChange={(e) => setFormData({...formData, metro: e.target.value})}
                  className="w-full px-3 py-2 bg-slate-700 text-white border border-slate-600 rounded focus:outline-none focus:border-blue-500"
                  placeholder="Красная площадь"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-gray-300 text-sm font-medium mb-2">До метро (мин)</label>
                  <input
                    type="number"
                    min="0"
                    max="120"
                    value={formData.time}
                    onChange={(e) => setFormData({...formData, time: Number(e.target.value)})}
                    className="w-full px-3 py-2 bg-slate-700 text-white border border-slate-600 rounded focus:outline-none focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-gray-300 text-sm font-medium mb-2">Тип пути</label>
                  <select
                    value={formData.time_type}
                    onChange={(e) => setFormData({...formData, time_type: e.target.value})}
                    className="w-full px-3 py-2 bg-slate-700 text-white border border-slate-600 rounded focus:outline-none focus:border-blue-500"
                  >
                    <option value="walk">Пешком</option>
                    <option value="transport">Транспорт</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-gray-300 text-sm font-medium mb-2">Описание</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({...formData, description: e.target.value})}
                  rows={3}
                  className="w-full px-3 py-2 bg-slate-700 text-white border border-slate-600 rounded focus:outline-none focus:border-blue-500"
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white font-bold py-2 rounded transition mt-6"
              >
                {loading ? '⏳ Загрузка...' : '✨ Получить прогноз'}
              </button>
            </form>
          </div>

          {/* Predictions List */}
          <div className="lg:col-span-2">
            <div className="space-y-4">
              <h2 className="text-xl font-bold">📊 Ваши прогнозы</h2>
              {predictions.length === 0 ? (
                <div className="bg-slate-800 rounded-lg p-6 text-center text-gray-400">
                  Прогнозов пока нет. Заполните форму слева! →
                </div>
              ) : (
                predictions.map((pred) => (
                  <div key={pred.id} className="bg-slate-800 rounded-lg p-4">
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <h3 className="font-bold text-lg">{pred.title}</h3>
                        <p className="text-gray-400 text-sm">{pred.metro}</p>
                      </div>
                      <div className="text-right">
                        <div className="text-2xl font-bold text-green-400">
                          ₽{Math.round(pred.predicted_price || 0).toLocaleString('ru-RU')}
                        </div>
                        <p className="text-gray-400 text-sm">сумма покупки</p>
                      </div>
                    </div>
                    <div className="grid grid-cols-3 gap-2 text-sm text-gray-300">
                      <div>📐 {pred.square}м²</div>
                      <div>🛏️ {pred.rooms_clean} комнат</div>
                      <div>📍 {pred.floor}/{pred.max_floor} этаж</div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
