import { useEffect, useState } from 'react';
import { newsApi } from '~/services/newsApi';
import NewsCard, { type NewsItem } from './NewsCard';

export default function NewsFeed({ topic }: { topic: string }) {
  const [items, setItems] = useState<NewsItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;

    const fetchNews = async () => {
      try {
        if (mounted && items.length === 0) setLoading(true);
        const data = await newsApi.getNewsItems();
        if (!mounted) return;

        setItems((prev) => {
          if (prev.length === 0) return data;
          const map = new Map<number, NewsItem>(data.map((d: NewsItem) => [d.id, d]));
          const updated = prev.map((p) => map.get(p.id) || p);
          const fresh = data.filter((d: NewsItem) => !prev.some((p) => p.id === d.id));
          return [...fresh, ...updated];
        });
        setError(null);
      } catch {
        if (mounted && items.length === 0) setError('Could not load news feed. Is the backend running on port 8010?');
      } finally {
        if (mounted) setLoading(false);
      }
    };

    fetchNews();
    const interval = setInterval(fetchNews, 30000);
    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, [topic]);

  if (loading && items.length === 0) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '80px 20px', gap: 16 }}>
        <div style={{ width: 48, height: 48, borderRadius: '50%', border: '4px solid rgba(96,165,250,0.3)', borderTopColor: '#60a5fa', animation: 'spin 0.8s linear infinite' }} />
        <p style={{ color: 'var(--text-muted)', fontWeight: 500 }}>Loading your B1 news feed...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ textAlign: 'center', padding: '80px 20px' }}>
        <div style={{ maxWidth: 400, margin: '0 auto', background: 'rgba(231,29,54,0.08)', border: '1px solid rgba(231,29,54,0.2)', borderRadius: 16, padding: '24px' }}>
          <p style={{ fontWeight: 700, color: 'var(--error)', marginBottom: 8 }}>Connection Error</p>
          <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>{error}</p>
        </div>
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '80px 20px', color: 'var(--text-muted)' }}>
        No news items found yet. Content is being generated.
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 560, margin: '0 auto', padding: '0 16px 40px' }}>
      {items.map((item) => (
        <NewsCard key={item.id} item={item} />
      ))}
    </div>
  );
}
