'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/auth';
import Link from 'next/link';

export default function Home() {
  const { user } = useAuthStore();
  const router = useRouter();

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 text-white">
      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-4 py-20">
        <div className="text-center">
          <h1 className="text-5xl font-bold mb-6">
            🏠 Predict Apartment Rental Prices
          </h1>
          <p className="text-xl text-gray-300 mb-8">
            AI-powered platform for accurate rental price estimation using machine learning
          </p>

          {!user ? (
            <div className="flex justify-center gap-4">
              <Link
                href="/auth/register"
                className="bg-gradient-to-r from-blue-600 to-purple-600 px-8 py-3 rounded-lg font-semibold hover:from-blue-700 hover:to-purple-700 transition"
              >
                Get Started
              </Link>
              <Link
                href="/auth/login"
                className="bg-white text-slate-900 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition"
              >
                Login
              </Link>
            </div>
          ) : (
            <Link
              href="/dashboard"
              className="bg-gradient-to-r from-blue-600 to-purple-600 px-8 py-3 rounded-lg font-semibold hover:from-blue-700 hover:to-purple-700 transition inline-block"
            >
              Go to Dashboard
            </Link>
          )}
        </div>
      </section>

      {/* Features */}
      <section className="bg-slate-800 py-16">
        <div className="max-w-7xl mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12">Why Choose Us?</h2>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-slate-700 p-6 rounded-lg">
              <h3 className="text-xl font-bold mb-3">⚡ AI-Powered</h3>
              <p>Advanced machine learning model trained on thousands of properties</p>
            </div>
            <div className="bg-slate-700 p-6 rounded-lg">
              <h3 className="text-xl font-bold mb-3">🎯 Accurate</h3>
              <p>Get precise price predictions based on location, size, and amenities</p>
            </div>
            <div className="bg-slate-700 p-6 rounded-lg">
              <h3 className="text-xl font-bold mb-3">📊 Analytics</h3>
              <p>View detailed analytics and trends for your predictions</p>
            </div>
          </div>
        </div>
      </section>

      {/* Examples */}
      <section className="max-w-7xl mx-auto px-4 py-16">
        <h2 className="text-3xl font-bold text-center mb-12">How It Works</h2>
        <div className="grid md:grid-cols-3 gap-8">
          <div className="text-center">
            <div className="bg-blue-600 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl">1️⃣</span>
            </div>
            <h3 className="font-bold mb-2">Add Property Details</h3>
            <p className="text-gray-400">Enter location, size, rooms, and other details</p>
          </div>
          <div className="text-center">
            <div className="bg-purple-600 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl">2️⃣</span>
            </div>
            <h3 className="font-bold mb-2">Upload Images</h3>
            <p className="text-gray-400">Add photos for better price estimation</p>
          </div>
          <div className="text-center">
            <div className="bg-pink-600 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl">3️⃣</span>
            </div>
            <h3 className="font-bold mb-2">Get Prediction</h3>
            <p className="text-gray-400">Receive accurate rental price estimate</p>
          </div>
        </div>
      </section>
    </div>
  );
}
