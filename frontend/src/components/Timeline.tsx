import React from 'react';
import type { ProcessedInfo, University } from '../types';
import { NewsCard } from './NewsCard';

interface TimelineProps {
  news: ProcessedInfo[];
  universities: University[];
  isLoading: boolean;
}

export const Timeline: React.FC<TimelineProps> = ({ news, universities, isLoading }) => {
  if (isLoading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="animate-pulse bg-white rounded-xl border border-gray-100 p-5 h-48"></div>
        ))}
      </div>
    );
  }

  if (news.length === 0) {
    return (
      <div className="text-center py-16 bg-white rounded-xl border border-gray-100">
        <div className="text-gray-400 mb-2 text-5xl">📭</div>
        <h3 className="text-lg font-medium text-gray-900">暂无情报</h3>
        <p className="text-gray-500 text-sm mt-1">目前还没有收集到相关的升学信息</p>
      </div>
    );
  }

  // Create a map for quick university lookup
  const uniMap = new Map(universities.map(u => [u.id, u]));

  return (
    <div className="space-y-8 relative before:absolute before:inset-0 before:left-4 before:-translate-x-px before:h-full before:w-0.5 before:bg-gray-200">
      {news.map((item) => (
        <div key={item.id} className="relative pl-10">
          {/* Timeline marker */}
          <div className="absolute left-0 top-1.5 flex items-center justify-center w-8 h-8 rounded-full border-4 border-white bg-primary text-white shadow-sm z-10">
            <div className="w-1.5 h-1.5 bg-white rounded-full"></div>
          </div>
          
          {/* Card container */}
          <div className="w-full">
            <NewsCard info={item} university={uniMap.get(item.raw_news.university_id)} />
          </div>
        </div>
      ))}
    </div>
  );
};
