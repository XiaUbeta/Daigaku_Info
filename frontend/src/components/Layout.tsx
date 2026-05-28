import React from 'react';
import { GraduationCap } from 'lucide-react';

export const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <div className="min-h-screen bg-gray-50 font-sans">
      <header className="bg-white shadow-sm sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="bg-primary/10 p-2 rounded-lg text-primary">
              <GraduationCap className="h-6 w-6" />
            </div>
            <h1 className="text-xl font-bold text-gray-900 tracking-tight">
              日本大学升学情报
            </h1>
          </div>
          <span className="text-xs font-medium bg-green-100 text-green-800 px-2.5 py-1 rounded-full border border-green-200">
            Real-time
          </span>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {children}
      </main>
    </div>
  );
};
