import { useState } from 'react';
import type { Route } from './+types/news';
import NewsFeed from '~/components/thenews/NewsFeed';
import { Search, RefreshCw, Sparkles } from 'lucide-react';
import { newsApi } from '~/services/newsApi';

export function meta({}: Route.MetaArgs) {
  return [
    { title: 'The News — Dutch B1 Feed' },
    { name: 'description', content: 'AI-generated Dutch B1 news articles with bilingual captions and grammar breakdowns.' },
  ];
}

export default function NewsPage() {
  const [topic, setTopic] = useState('');
  const [input, setInput] = useState('');

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setTopic(input.trim());
  };

  const [isGenerating, setIsGenerating] = useState(false);

  const handleGenerate = async () => {
    setIsGenerating(true);
    try {
      const res = await newsApi.generateContent();
      alert(res.message);
    } catch (err) {
      console.error(err);
      alert('Failed to trigger generation. Check console for details.');
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="page-container">
      {/* Page Header */}
      <div style={{ marginBottom: '40px', textAlign: 'center' }}>
        <h1 style={{ marginBottom: '8px' }}>
          The{' '}
          <span style={{ background: 'linear-gradient(90deg, #60a5fa, #818cf8)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            News
          </span>
        </h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '1rem', marginBottom: '28px' }}>
          Dutch B1 articles crafted by AI, ready for your daily reading practice
        </p>

        {/* Search bar */}
        <form onSubmit={handleSearch} style={{ display: 'flex', gap: '10px', maxWidth: '480px', margin: '0 auto' }}>
          <div style={{ flex: 1, position: 'relative' }}>
            <Search size={16} style={{ position: 'absolute', left: 14, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Filter by topic (e.g. Klimaat, Sport)..."
              minLength={2}
              style={{
                width: '100%',
                padding: '11px 14px 11px 40px',
                borderRadius: 12,
                border: '1px solid var(--glass-border)',
                background: 'var(--card-bg)',
                color: 'var(--text-light)',
                fontSize: '0.9rem',
                fontFamily: 'inherit',
                outline: 'none',
              }}
            />
          </div>
          <button type="submit" className="btn btn-primary" style={{ padding: '11px 22px', borderRadius: 12, whiteSpace: 'nowrap' }}>
            Search
          </button>
          
          <button 
            type="button" 
            onClick={handleGenerate}
            disabled={isGenerating}
            className="btn" 
            style={{ 
              padding: '11px 22px', 
              borderRadius: 12, 
              whiteSpace: 'nowrap',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              background: 'rgba(96,165,250,0.1)',
              border: '1px solid rgba(96,165,250,0.3)',
              color: '#60a5fa',
              cursor: isGenerating ? 'not-allowed' : 'pointer',
              opacity: isGenerating ? 0.6 : 1
            }}
          >
            <RefreshCw size={16} className={isGenerating ? 'animate-spin' : ''} />
            {isGenerating ? 'Generating...' : 'Generate New'}
          </button>
        </form>

        {topic && (
          <div style={{ marginTop: 16, display: 'flex', alignItems: 'center', gap: 10, justifyContent: 'center' }}>
            <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Showing results for:</span>
            <span style={{ padding: '4px 14px', borderRadius: 999, background: 'rgba(96,165,250,0.12)', color: '#60a5fa', fontWeight: 700, fontSize: '0.85rem' }}>
              {topic}
            </span>
            <button onClick={() => { setTopic(''); setInput(''); }} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', fontSize: '0.8rem' }}>
              ✕ Clear
            </button>
          </div>
        )}
      </div>

      <NewsFeed topic={topic} />
    </div>
  );
}
