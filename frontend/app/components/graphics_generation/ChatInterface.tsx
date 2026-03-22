import { useState, useEffect, useRef } from 'react';
import { Send, Image as ImageIcon, Video, Trash2, Loader2, Wand2 } from 'lucide-react';
import { graphicsGenerationApi, type GraphicsItem, COMFY_URL } from '~/services/graphicsGenerationApi';

function MediaDisplay({ item, onDelete }: { item: GraphicsItem, onDelete: (id: number) => void }) {
  const [actualUrl, setActualUrl] = useState<string | null>(null);
  const [isError, setIsError] = useState(false);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    const promptId = item.media_url;

    const check = async () => {
      try {
        const statusData = await graphicsGenerationApi.checkStatus(promptId);
        if (statusData && !statusData.status && Object.keys(statusData).length > 0) {
          // It's likely the outputs dictionary
          const nodeKeys = Object.keys(statusData);
          if (nodeKeys.length > 0) {
            const firstNode = statusData[nodeKeys[nodeKeys.length - 1]];
            const mediaList = firstNode.images || firstNode.gifs || firstNode.videos;
            if (mediaList && mediaList.length > 0) {
              const media = mediaList[0];
              const url = `${COMFY_URL}/view?filename=${media.filename}&type=${media.type}&subfolder=${media.subfolder}`;
              setActualUrl(url);
              clearInterval(interval);
            }
          }
        } else if (statusData && statusData.status === 'error') {
          setIsError(true);
          clearInterval(interval);
        }
      } catch (err) {
        console.error(err);
      }
    };

    if (promptId && !promptId.includes('view?filename=')) {
      // it's a prompt id, we should poll
      check();
      interval = setInterval(check, 3000);
    } else {
      setActualUrl(promptId);
    }

    return () => clearInterval(interval);
  }, [item.media_url]);

  return (
    <div style={{
      display: 'flex', flexDirection: 'column', gap: '8px',
      background: 'rgba(255,255,255,0.03)', padding: '16px', borderRadius: '16px',
      border: '1px solid var(--glass-border)', position: 'relative',
      width: '100%', maxWidth: '600px', alignSelf: 'center'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div style={{ flex: 1 }}>
          <p style={{ margin: 0, fontWeight: 600, color: 'var(--text-light)', fontSize: '0.95rem' }}>{item.original_prompt}</p>
          {item.improved_prompt && item.improved_prompt !== item.original_prompt && (
            <p style={{ margin: '4px 0 0 0', fontSize: '0.8rem', color: '#a78bfa', display: 'flex', alignItems: 'center', gap: '4px' }}>
              <Wand2 size={12} /> {item.improved_prompt}
            </p>
          )}
        </div>
        <button
          onClick={() => onDelete(item.id)}
          style={{
            background: 'none', border: 'none', color: '#4b5563', cursor: 'pointer',
            padding: '4px', borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center',
            transition: 'color 0.2s, background 0.2s', marginLeft: '12px'
          }}
          onMouseEnter={e => { e.currentTarget.style.color = '#ef4444'; e.currentTarget.style.background = 'rgba(239,68,68,0.1)'; }}
          onMouseLeave={e => { e.currentTarget.style.color = '#4b5563'; e.currentTarget.style.background = 'transparent'; }}
          title="Delete message"
        >
          <Trash2 size={18} />
        </button>
      </div>

      <div style={{
        marginTop: '8px', borderRadius: '12px', overflow: 'hidden',
        background: 'rgba(0,0,0,0.2)', minHeight: '200px', display: 'flex',
        alignItems: 'center', justifyContent: 'center', width: '100%'
      }}>
        {isError ? (
          <p style={{ color: '#ef4444', fontSize: '0.9rem' }}>Generation failed</p>
        ) : actualUrl ? (
          item.media_type === 'video' ? (
            <video src={actualUrl} autoPlay loop muted playsInline style={{ width: '100%', display: 'block' }} />
          ) : (
            <img src={actualUrl} alt={item.original_prompt} style={{ width: '100%', display: 'block' }} />
          )
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', alignItems: 'center', color: '#a78bfa' }}>
            <Loader2 size={24} className="animate-spin" />
            <span style={{ fontSize: '0.85rem', fontWeight: 500 }}>Generating {item.media_type}...</span>
          </div>
        )}
      </div>
    </div>
  );
}

export default function ChatInterface() {
  const [history, setHistory] = useState<GraphicsItem[]>([]);
  const [input, setInput] = useState('');
  const [mediaType, setMediaType] = useState<'image' | 'video'>('image');
  const [isLoading, setIsLoading] = useState(true);
  const [isEnhanceEnabled, setIsEnhanceEnabled] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isMobilePortrait, setIsMobilePortrait] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadHistory();
  }, []);

  useEffect(() => {
    if (typeof window === 'undefined') return;

    const mediaQuery = window.matchMedia('(max-width: 768px) and (orientation: portrait)');
    const updateViewMode = () => setIsMobilePortrait(mediaQuery.matches);
    updateViewMode();

    if (mediaQuery.addEventListener) {
      mediaQuery.addEventListener('change', updateViewMode);
    } else {
      mediaQuery.addListener(updateViewMode);
    }

    return () => {
      if (mediaQuery.removeEventListener) {
        mediaQuery.removeEventListener('change', updateViewMode);
      } else {
        mediaQuery.removeListener(updateViewMode);
      }
    };
  }, []);

  const loadHistory = async () => {
    try {
      const items = await graphicsGenerationApi.getHistory();
      setHistory(items.reverse()); // oldest first for chat flow
    } catch (err) {
      console.error('Failed to load history', err);
    } finally {
      setIsLoading(false);
    }
  };

  const scrollToBottom = () => {
    if (scrollRef.current && !isMobilePortrait) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [history, isMobilePortrait]);

  const handleSend = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!input.trim() || isGenerating) return;

    const originalInput = input;
    setInput('');
    setIsGenerating(true);

    // Add optimistic placeholder
    const optimisticItem: GraphicsItem = {
      id: Date.now(),
      created_at: new Date().toISOString(),
      original_prompt: originalInput,
      improved_prompt: originalInput,
      media_type: mediaType,
      media_url: '', // pending
    };
    setHistory(prev => [...prev, optimisticItem]);

    try {
      let finalPromptToUse = originalInput;
      
      if (isEnhanceEnabled) {
        try {
          const res = await graphicsGenerationApi.enhancePrompt(originalInput);
          finalPromptToUse = res.improved_prompt;
        } catch (enhanceErr) {
          console.error("Enhancement failed, using original prompt", enhanceErr);
          // Fallback to original prompt if enhancement fails
        }
      }

      const newItem = await graphicsGenerationApi.generateMedia(originalInput, finalPromptToUse, mediaType);
      setHistory(prev => prev.map(item => item.id === optimisticItem.id ? newItem : item));
    } catch (err) {
      console.error('Failed to generate media', err);
      // Remove optimistic item on failure
      setHistory(prev => prev.filter(item => item.id !== optimisticItem.id));
      setInput(originalInput);
      alert('Generation request failed.');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await graphicsGenerationApi.deleteItem(id);
      setHistory(prev => prev.filter(i => i.id !== id));
    } catch (err) {
      console.error('Failed to delete', err);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: isMobilePortrait ? 'auto' : '100%' }}>
      {/* Scrollable Feed */}
      <div 
        ref={scrollRef}
        style={{ 
          flex: isMobilePortrait ? '0 1 auto' : 1,
          overflowY: isMobilePortrait ? 'visible' : 'auto',
          padding: isMobilePortrait ? '12px' : '24px',
          paddingBottom: isMobilePortrait ? '128px' : '24px',
          display: 'flex',
          flexDirection: 'column',
          gap: isMobilePortrait ? '16px' : '24px',
        }}
      >
        {isLoading ? (
          <div style={{ margin: 'auto', color: 'var(--text-muted)' }}><Loader2 className="animate-spin" /></div>
        ) : history.length === 0 ? (
          <div style={{ margin: 'auto', color: 'var(--text-muted)', textAlign: 'center' }}>
            <Wand2 size={48} style={{ opacity: 0.2, margin: '0 auto 16px block' }} />
            <p>No generations yet.<br/>Type a description below to get started!</p>
          </div>
        ) : (
          history.map(item => (
            <MediaDisplay key={item.id} item={item} onDelete={handleDelete} />
          ))
        )}
      </div>

      {/* Input Area */}
      <div
        style={{
          background: 'rgba(1,22,39,0.78)',
          borderTop: '1px solid var(--glass-border)',
          padding: isMobilePortrait ? '12px 12px calc(12px + env(safe-area-inset-bottom, 0px))' : '16px 24px',
          position: isMobilePortrait ? 'sticky' : 'static',
          bottom: isMobilePortrait ? 0 : undefined,
          backdropFilter: isMobilePortrait ? 'blur(12px)' : 'none',
          zIndex: isMobilePortrait ? 20 : 'auto',
        }}
      >
        <form 
          onSubmit={handleSend}
          style={{ 
            display: 'flex',
            gap: '12px',
            alignItems: isMobilePortrait ? 'stretch' : 'flex-end',
            flexDirection: isMobilePortrait ? 'column' : 'row',
            maxWidth: '800px',
            margin: '0 auto',
            width: '100%',
          }}
        >
          {isMobilePortrait && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', width: '100%' }}>
              {/* Enhance Button */}
              <button
                type="button"
                onClick={() => setIsEnhanceEnabled(prev => !prev)}
                style={{
                  background: isEnhanceEnabled ? 'linear-gradient(135deg, #818cf8, #c084fc)' : 'rgba(0,0,0,0.3)',
                  border: isEnhanceEnabled ? '2px solid #a78bfa' : '2px solid transparent',
                  borderRadius: '50%',
                  width: '48px',
                  height: '48px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: isEnhanceEnabled ? 'white' : 'var(--text-muted)',
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                  flexShrink: 0,
                  boxShadow: isEnhanceEnabled ? '0 0 15px rgba(167, 139, 250, 0.5)' : 'none',
                }}
                title={isEnhanceEnabled ? "Prompt enhancement enabled" : "Enable AI prompt enhancement"}
              >
                <Wand2 size={20} />
              </button>

              {/* Media Type Toggle */}
              <div
                style={{
                  display: 'flex',
                  background: 'rgba(0,0,0,0.3)',
                  borderRadius: '10px',
                  padding: '4px',
                  border: '1px solid var(--glass-border)',
                  flex: 1,
                }}
              >
                <button
                  type="button"
                  onClick={() => setMediaType('image')}
                  style={{
                    flex: 1,
                    minHeight: '40px',
                    padding: '8px 12px',
                    border: 'none',
                    borderRadius: '6px',
                    background: mediaType === 'image' ? '#a78bfa' : 'transparent',
                    color: mediaType === 'image' ? '#fff' : 'var(--text-muted)',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '6px',
                    fontSize: '0.85rem',
                    fontWeight: 600,
                    transition: 'all 0.2s',
                  }}
                >
                  <ImageIcon size={14} /> Image
                </button>
                <button
                  type="button"
                  onClick={() => setMediaType('video')}
                  style={{
                    flex: 1,
                    minHeight: '40px',
                    padding: '8px 12px',
                    border: 'none',
                    borderRadius: '6px',
                    background: mediaType === 'video' ? '#a78bfa' : 'transparent',
                    color: mediaType === 'video' ? '#fff' : 'var(--text-muted)',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '6px',
                    fontSize: '0.85rem',
                    fontWeight: 600,
                    transition: 'all 0.2s',
                  }}
                >
                  <Video size={14} /> Video
                </button>
              </div>
            </div>
          )}

          {/* Text Input */}
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <textarea
              value={input}
              onChange={e => setInput(e.target.value)}
              placeholder="Describe what you want to generate in 1-3 sentences..."
              rows={isMobilePortrait ? 3 : 2}
              style={{
                width: '100%',
                padding: '12px 16px',
                borderRadius: '14px',
                background: 'rgba(0,0,0,0.2)',
                border: '1px solid var(--glass-border)',
                color: 'var(--text-light)',
                fontSize: isMobilePortrait ? '1rem' : '0.95rem',
                fontFamily: 'inherit',
                outline: 'none',
                resize: 'none',
                lineHeight: '1.4',
              }}
              onKeyDown={e => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSend();
                }
              }}
            />
          </div>

          {isMobilePortrait ? (
            <button
              type="submit"
              disabled={!input.trim() || isGenerating}
              style={{
                width: '100%',
                minHeight: '48px',
                background: 'var(--primary)',
                color: '#fff',
                border: 'none',
                borderRadius: '12px',
                padding: '12px 16px',
                fontWeight: 700,
                cursor: (!input.trim() || isGenerating) ? 'not-allowed' : 'pointer',
                fontSize: '0.95rem',
                opacity: (!input.trim() || isGenerating) ? 0.6 : 1,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
              }}
            >
              {isGenerating ? <Loader2 size={18} className="animate-spin" /> : <Send size={16} />}
              {isGenerating ? 'Sending...' : 'Send'}
            </button>
          ) : (
            <>
              {/* Enhance Button */}
              <button
                type="button"
                onClick={() => setIsEnhanceEnabled(prev => !prev)}
                style={{
                  background: isEnhanceEnabled ? 'linear-gradient(135deg, #818cf8, #c084fc)' : 'rgba(0,0,0,0.3)',
                  border: isEnhanceEnabled ? '2px solid #a78bfa' : '2px solid transparent',
                  borderRadius: '50%',
                  width: '44px',
                  height: '44px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: isEnhanceEnabled ? 'white' : 'var(--text-muted)',
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                  flexShrink: 0,
                  boxShadow: isEnhanceEnabled ? '0 0 15px rgba(167, 139, 250, 0.5)' : 'none',
                }}
                title={isEnhanceEnabled ? "Prompt enhancement enabled" : "Enable AI prompt enhancement"}
                onMouseEnter={e => { e.currentTarget.style.transform = 'scale(1.05)'; }}
                onMouseLeave={e => e.currentTarget.style.transform = 'scale(1)'}
              >
                <Wand2 size={20} />
              </button>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', flexShrink: 0 }}>
                {/* Media Type Slider/Toggle */}
                <div
                  style={{
                    display: 'flex',
                    background: 'rgba(0,0,0,0.3)',
                    borderRadius: '10px',
                    padding: '4px',
                    border: '1px solid var(--glass-border)',
                  }}
                >
                  <button
                    type="button"
                    onClick={() => setMediaType('image')}
                    style={{
                      flex: 1,
                      padding: '6px 12px',
                      border: 'none',
                      borderRadius: '6px',
                      background: mediaType === 'image' ? '#a78bfa' : 'transparent',
                      color: mediaType === 'image' ? '#fff' : 'var(--text-muted)',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px',
                      fontSize: '0.8rem',
                      fontWeight: 600,
                      transition: 'all 0.2s',
                    }}
                  >
                    <ImageIcon size={14} /> Image
                  </button>
                  <button
                    type="button"
                    onClick={() => setMediaType('video')}
                    style={{
                      flex: 1,
                      padding: '6px 12px',
                      border: 'none',
                      borderRadius: '6px',
                      background: mediaType === 'video' ? '#a78bfa' : 'transparent',
                      color: mediaType === 'video' ? '#fff' : 'var(--text-muted)',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px',
                      fontSize: '0.8rem',
                      fontWeight: 600,
                      transition: 'all 0.2s',
                    }}
                  >
                    <Video size={14} /> Video
                  </button>
                </div>

                <button
                  type="submit"
                  disabled={!input.trim() || isGenerating}
                  style={{
                    background: 'var(--primary)',
                    color: '#fff',
                    border: 'none',
                    borderRadius: '10px',
                    padding: '10px 16px',
                    fontWeight: 600,
                    cursor: (!input.trim() || isGenerating) ? 'not-allowed' : 'pointer',
                    fontSize: '0.9rem',
                    opacity: (!input.trim() || isGenerating) ? 0.6 : 1,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '6px',
                    transition: 'background 0.2s',
                  }}
                >
                  {isGenerating ? <Loader2 size={16} className="animate-spin" /> : <Send size={16} />}
                  {isGenerating ? 'Sending...' : 'Send'}
                </button>
              </div>
            </>
          )}
        </form>
      </div>
    </div>
  );
}
