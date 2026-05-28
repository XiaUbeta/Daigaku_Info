// Map to backend app/models/schemas.py

export interface University {
  id: number;
  name: string;
  name_en?: string;
  logo_url?: string;
  official_url?: string;
  x_handle?: string;
}

export interface RawNews {
  id: number;
  university_id: number;
  source_type: string;
  url: string;
  raw_text: string;
  scraped_at: string; // ISO format string
}

export interface ProcessedInfo {
  id: number;
  created_at: string; // ISO format string
  category: string; // 出愿情报, Open Campus, 讲座, 变更, 其他
  summary: string;
  important_dates?: string;
  raw_news: RawNews;
}
