'use client';

import Navbar from '@/components/Navbar';
import './globals.css';
import { Toaster } from 'react-hot-toast';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <meta charSet="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>ApartmentRent - AI-Powered Rental Price Prediction</title>
        <meta name="description" content="Predict apartment rental prices with AI" />
      </head>
      <body className="bg-gray-50">
        <Navbar />
        {children}
        <Toaster position="bottom-right" />
      </body>
    </html>
  );
}
