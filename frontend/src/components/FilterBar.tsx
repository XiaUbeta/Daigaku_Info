import React from 'react';
import type { University } from '../types';

interface FilterBarProps {
  universities: University[];
  activeId: number | null;
  onSelect: (id: number | null) => void;
}

export const FilterBar: React.FC<FilterBarProps> = ({
  universities,
  activeId,
  onSelect,
}) => {
  return (
    <div className="flex flex-wrap gap-2.5 mb-4">
      <button
        onClick={() => onSelect(null)}
        className={`px-4 py-1.5 rounded-md text-sm font-bold transition-colors ${
          activeId === null
            ? 'bg-primary text-white shadow-sm'
            : 'bg-white text-gray-600 hover:bg-gray-100 border border-gray-200'
        }`}
      >
        全部情报
      </button>
      
      {universities.map((uni) => (
        <button
          key={uni.id}
          onClick={() => onSelect(uni.id)}
          className={`px-4 py-1.5 rounded-md text-sm font-bold transition-colors ${
            activeId === uni.id
              ? 'bg-primary text-white shadow-sm'
              : 'bg-white text-gray-600 hover:bg-gray-100 border border-gray-200'
          }`}
        >
          {uni.name}
        </button>
      ))}
    </div>
  );
};
