import React from 'react';
import { Swiper, SwiperSlide } from 'swiper/react';
import { Navigation, Pagination } from 'swiper/modules';
import 'swiper/css';
import 'swiper/css/navigation';
import 'swiper/css/pagination';
import { MEDIA_BASE } from '~/services/newsApi';

export interface ImageInfo {
  image_id: string;
  img_path: string;
  status: string;
}

export interface BreakdownSentence {
  english: string;
  dutch: string;
  explanation: string;
  highlighted_words: string[];
  underlined_verb: string;
}

export interface NewsItem {
  id: number;
  theme: string;
  question: string;
  output_captions: string[];
  images_info: ImageInfo[];
  breakdown_sentences?: BreakdownSentence[];
}

export default function NewsCard({ item }: { item: NewsItem }) {
  const images = item.images_info.filter((img) => ['done', 'passed'].includes(img.status) && img.img_path);

  return (
    <div
      className="glass"
      style={{
        maxWidth: 520,
        margin: '0 auto 32px',
        overflow: 'hidden',
        borderRadius: 24,
        transition: 'transform 0.25s, box-shadow 0.25s',
        boxShadow: '0 4px 32px rgba(0,0,0,0.3)',
      }}
      onMouseEnter={(e) => {
        (e.currentTarget as HTMLDivElement).style.transform = 'scale(1.01)';
        (e.currentTarget as HTMLDivElement).style.boxShadow = '0 12px 48px rgba(96,165,250,0.15)';
      }}
      onMouseLeave={(e) => {
        (e.currentTarget as HTMLDivElement).style.transform = 'scale(1)';
        (e.currentTarget as HTMLDivElement).style.boxShadow = '0 4px 32px rgba(0,0,0,0.3)';
      }}
    >
      {/* Header */}
      <div style={{ padding: '16px 20px', display: 'flex', alignItems: 'center', gap: '12px' }}>
        <div style={{
          width: 40, height: 40, borderRadius: '50%',
          background: 'linear-gradient(135deg, #FB923C, #EC4899)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          color: '#fff', fontWeight: 900, fontSize: '1rem',
        }}>
          {item.theme[0]?.toUpperCase()}
        </div>
        <div>
          <div style={{ fontWeight: 700, fontSize: '0.95rem', color: 'var(--text-light)' }}>{item.theme}</div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 2 }}>{item.question}</div>
        </div>
      </div>

      {/* Image Carousel */}
      <div style={{ aspectRatio: '1 / 1', background: 'rgba(255,255,255,0.03)', position: 'relative' }}>
        {images.length > 0 ? (
          <Swiper
            modules={[Navigation, Pagination]}
            navigation
            pagination={{ clickable: true }}
            style={{ height: '100%', width: '100%' }}
          >
            {images.map((img) => {
              const src = `${MEDIA_BASE}/api/news/image?img_path=${encodeURIComponent(img.img_path)}&skip_zrok_interstitial=true`;
              return (
                <SwiperSlide key={img.image_id}>
                  <img
                    src={src}
                    alt={item.theme}
                    style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                    onError={(e) => { (e.currentTarget as HTMLImageElement).style.display = 'none'; }}
                  />
                </SwiperSlide>
              );
            })}
          </Swiper>
        ) : (
          <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)', fontStyle: 'italic', fontSize: '0.9rem' }}>
            Images being generated...
          </div>
        )}
      </div>

      {/* Captions */}
      <div style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {(() => {
          const captionsArray = Array.isArray(item.output_captions)
            ? item.output_captions
            : typeof item.output_captions === 'string'
              ? (item.output_captions as string).split('\n').filter((s: string) => s.trim().length > 0)
              : [];
          return captionsArray.map((caption: string, idx: number) => {
            const isGrammar = caption.startsWith('[Grammar Breakdown]:');
            const text = isGrammar ? caption.replace('[Grammar Breakdown]:', '').trim() : caption;
            if (isGrammar) {
              return (
                <div key={idx} style={{
                  padding: '10px 14px', borderRadius: 12,
                  background: 'rgba(96,165,250,0.08)', borderLeft: '3px solid #60a5fa',
                  color: '#93c5fd', fontSize: '0.82rem', fontStyle: 'italic',
                }}>
                  <span style={{ fontWeight: 700, marginRight: 6 }}>💡 Regel:</span>{text}
                </div>
              );
            }
            return (
              <p key={idx} style={{
                fontSize: idx % 2 === 0 ? '0.95rem' : '0.82rem',
                fontWeight: idx % 2 === 0 ? 600 : 400,
                color: idx % 2 === 0 ? 'var(--text-light)' : 'var(--text-muted)',
                lineHeight: 1.6,
              }}>
                {text}
              </p>
            );
          });
        })()}

        {item.breakdown_sentences && item.breakdown_sentences.length > 0 && (
          <div style={{
            marginTop: 12, padding: '16px', borderRadius: 14,
            background: 'rgba(96,165,250,0.06)', border: '1px solid rgba(96,165,250,0.15)',
          }}>
            <h4 style={{ color: '#93c5fd', marginBottom: 10, fontSize: '0.85rem' }}>🧠 Grammar Spotlight</h4>
            {item.breakdown_sentences.map((b, idx) => (
              <div key={idx} style={{ marginBottom: 12, fontSize: '0.85rem' }}>
                <p style={{ fontStyle: 'italic', color: '#bfdbfe', marginBottom: 4 }}>"{b.dutch}"</p>
                <p style={{ color: '#93c5fd', lineHeight: 1.5 }}>{b.explanation}</p>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <div style={{
        padding: '12px 20px 16px',
        borderTop: '1px solid var(--glass-border)',
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
      }}>
        <div style={{ display: 'flex', gap: '14px' }}>
          <button style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: '1.4rem', transition: 'transform 0.2s' }}
            onMouseEnter={(e) => (e.currentTarget.style.transform = 'scale(1.2)')}
            onMouseLeave={(e) => (e.currentTarget.style.transform = 'scale(1)')}>
            ❤️
          </button>
          <button style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: '1.4rem', transition: 'transform 0.2s' }}
            onMouseEnter={(e) => (e.currentTarget.style.transform = 'scale(1.2)')}
            onMouseLeave={(e) => (e.currentTarget.style.transform = 'scale(1)')}>
            💬
          </button>
        </div>
        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>#{item.id}</span>
      </div>
    </div>
  );
}
