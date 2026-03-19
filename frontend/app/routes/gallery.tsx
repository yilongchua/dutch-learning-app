import { useEffect, useState, useRef, useCallback } from 'react';
import { galleryApi, MEDIA_BASE } from '~/services/galleryApi';
import { Image, PlayCircle } from 'lucide-react';

export default function GalleryPage() {
  const [images, setImages] = useState<string[]>([]);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const observer = useRef<IntersectionObserver | null>(null);
  
  const ITEMS_PER_PAGE = 12;

  useEffect(() => {
    const fetchGallery = async () => {
      try {
        setLoading(true);
        const res = await galleryApi.getGallery();
        setImages(res.images);
      } catch (e) {
        console.error("Failed to load gallery", e);
      } finally {
        setLoading(false);
      }
    };
    fetchGallery();
  }, []);

  const displayedImages = images.slice(0, page * ITEMS_PER_PAGE);
  const hasMore = displayedImages.length < images.length;

  const lastElementRef = useCallback(
    (node: HTMLElement | null) => {
      if (loading) return;
      if (observer.current) observer.current.disconnect();
      observer.current = new IntersectionObserver((entries) => {
        if (entries[0].isIntersecting && hasMore) {
          setPage((prevPage) => prevPage + 1);
        }
      });
      if (node) observer.current.observe(node);
    },
    [loading, hasMore]
  );

  const isVideo = (url: string) => url.endsWith(".mp4");

  return (
    <div className="page-container" style={{ padding: '100px 4% 40px', maxWidth: '1400px', margin: '0 auto', minHeight: '100vh' }}>
      <header style={{ marginBottom: '40px', textAlign: 'center' }}>
        <h1 style={{ 
          fontSize: '2.5rem', 
          fontWeight: 800, 
          background: 'linear-gradient(to right, #a78bfa, #60a5fa)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          marginBottom: '10px'
        }}>
          Media Gallery
        </h1>
        <p style={{ color: 'var(--text-muted)' }}>Explore all generated images and videos</p>
      </header>

      {loading && images.length === 0 ? (
        <div style={{ textAlign: 'center', color: 'var(--text-muted)' }}>Loading...</div>
      ) : (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
          gap: '24px',
          paddingBottom: '40px'
        }}>
          {displayedImages.map((src, index) => {
            const isLast = index === displayedImages.length - 1;
            const fullUrl = `${MEDIA_BASE}${src}`;
            
            return (
              <div
                key={src}
                ref={isLast ? lastElementRef : null}
                style={{
                  borderRadius: '16px',
                  overflow: 'hidden',
                  background: 'rgba(255,255,255,0.02)',
                  border: '1px solid var(--glass-border)',
                  aspectRatio: '1/1',
                  position: 'relative',
                  boxShadow: '0 8px 30px rgba(0,0,0,0.2)',
                  transition: 'transform 0.3s ease, box-shadow 0.3s ease',
                  cursor: 'pointer'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'translateY(-5px)';
                  e.currentTarget.style.boxShadow = '0 12px 40px rgba(0,0,0,0.4)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = '0 8px 30px rgba(0,0,0,0.2)';
                }}
              >
                {isVideo(src) ? (
                  <>
                    <video 
                      src={fullUrl} 
                      autoPlay 
                      loop 
                      muted 
                      playsInline
                      style={{ width: '100%', height: '100%', objectFit: 'cover' }} 
                    />
                    <div style={{ position: 'absolute', top: 10, right: 10, background: 'rgba(0,0,0,0.6)', padding: '6px', borderRadius: '50%' }}>
                      <PlayCircle size={18} color="#fff" />
                    </div>
                  </>
                ) : (
                  <>
                    <img 
                      src={fullUrl} 
                      alt="Generated Media" 
                      style={{ width: '100%', height: '100%', objectFit: 'cover' }} 
                      loading="lazy"
                    />
                    <div style={{ position: 'absolute', top: 10, right: 10, background: 'rgba(0,0,0,0.6)', padding: '6px', borderRadius: '50%' }}>
                      <Image size={18} color="#fff" />
                    </div>
                  </>
                )}
              </div>
            );
          })}
        </div>
      )}
      
      {!hasMore && images.length > 0 && (
         <div style={{ textAlign: 'center', color: 'var(--text-muted)', marginTop: '20px' }}>
           You've reached the end of the gallery.
         </div>
      )}
      {images.length === 0 && !loading && (
         <div style={{ textAlign: 'center', color: 'var(--text-muted)', marginTop: '20px' }}>
           No images found.
         </div>
      )}
    </div>
  );
}
