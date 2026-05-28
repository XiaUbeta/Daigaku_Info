import { useState, useEffect } from 'react';
import { api } from './api';
import type { University, ProcessedInfo } from './types';
import { Layout } from './components/Layout';
import { FilterBar } from './components/FilterBar';
import { Timeline } from './components/Timeline';
import { AlertCircle } from 'lucide-react';

function App() {
  const [universities, setUniversities] = useState<University[]>([]);
  const [news, setNews] = useState<ProcessedInfo[]>([]);
  const [activeUniversityId, setActiveUniversityId] = useState<number | null>(null);
  
  const [isLoadingUniversities, setIsLoadingUniversities] = useState(true);
  const [isLoadingNews, setIsLoadingNews] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch universities on mount
  useEffect(() => {
    const fetchUniversities = async () => {
      try {
        setIsLoadingUniversities(true);
        const data = await api.getUniversities();
        setUniversities(data);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch universities:', err);
        setError('无法加载大学列表，请稍后再试。');
      } finally {
        setIsLoadingUniversities(false);
      }
    };

    fetchUniversities();
  }, []);

  // Fetch news when active university changes
  useEffect(() => {
    const fetchNews = async () => {
      try {
        setIsLoadingNews(true);
        const data = await api.getNews(activeUniversityId);
        setNews(data);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch news:', err);
        setError('无法加载情报数据，请稍后再试。');
      } finally {
        setIsLoadingNews(false);
      }
    };

    fetchNews();
  }, [activeUniversityId]);

  return (
    <Layout>
      {error && (
        <div className="mb-6 bg-red-50 border-l-4 border-red-500 p-4 rounded-md flex items-start">
          <AlertCircle className="w-5 h-5 text-red-500 mr-3 mt-0.5" />
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      {!isLoadingUniversities && universities.length > 0 && (
        <div className="mb-8">
          <FilterBar
            universities={universities}
            activeId={activeUniversityId}
            onSelect={setActiveUniversityId}
          />
        </div>
      )}

      <div className="mt-4">
        <Timeline 
          news={news} 
          universities={universities} 
          isLoading={isLoadingNews} 
        />
      </div>
    </Layout>
  );
}

export default App;
