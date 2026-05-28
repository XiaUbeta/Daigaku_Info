import React from 'react';
import type { ProcessedInfo, University } from '../types';
import { format, parseISO } from 'date-fns';
import { ExternalLink, Calendar, Building2, Tag } from 'lucide-react';

interface NewsCardProps {
  info: ProcessedInfo;
  university?: University;
}

const getCategoryColor = (category: string) => {
  switch (category) {
    case '出愿情报':
      return 'bg-red-100 text-red-800 border-red-200';
    case 'Open Campus':
      return 'bg-blue-100 text-blue-800 border-blue-200';
    case '讲座':
      return 'bg-purple-100 text-purple-800 border-purple-200';
    case '变更':
      return 'bg-amber-100 text-amber-800 border-amber-200';
    default:
      return 'bg-gray-100 text-gray-800 border-gray-200';
  }
};

export const NewsCard: React.FC<NewsCardProps> = ({ info, university }) => {
  const publishedDate = format(parseISO(info.raw_news.scraped_at), 'yyyy-MM-dd HH:mm');

  return (
    <div className="bg-white rounded-lg border-2 border-gray-100 p-4 hover:border-primary/30 transition-colors">
      <div className="flex flex-wrap items-center gap-2 mb-3">
        {university && (
          <span className="text-sm font-bold text-gray-900 bg-gray-100 px-2 py-0.5 rounded">
            {university.name}
          </span>
        )}
        <span className={`text-xs font-bold px-2 py-0.5 rounded border ${getCategoryColor(info.category)}`}>
          {info.category}
        </span>
        <span className="text-xs text-gray-500 ml-auto font-mono">
          {publishedDate}
        </span>
      </div>

      <div className="mb-4">
        <p className="text-gray-900 leading-snug font-medium text-base">
          {info.summary}
        </p>
      </div>

      {info.important_dates && info.important_dates !== "无" && info.important_dates !== "未提及" && (
        <div className="mb-3 bg-red-50/50 border-l-4 border-red-400 p-3">
          <div className="flex items-center text-red-700 font-bold text-sm mb-1">
            <Calendar className="w-4 h-4 mr-1.5" />
            重要日期与事项
          </div>
          <div className="text-sm text-red-900 whitespace-pre-wrap font-semibold leading-relaxed">
            {info.important_dates}
          </div>
        </div>
      )}

      <div className="pt-3 border-t border-dashed border-gray-200 flex justify-end">
        <a
          href={info.raw_news.url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-xs font-bold text-primary hover:underline flex items-center"
        >
          查看官方原文 <ExternalLink className="w-3 h-3 ml-1" />
        </a>
      </div>
    </div>
  );
};
