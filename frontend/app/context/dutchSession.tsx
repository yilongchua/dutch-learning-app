import { createContext, useContext, useEffect, useMemo, useState } from 'react';

type PersistedExercise = Record<string, any> | null;
type PersistedResult = Record<string, any> | null;

interface WritingSessionState {
  exercise: PersistedExercise;
  text: string;
  result: PersistedResult;
}

interface SpeakingSessionState {
  exercise: PersistedExercise;
  result: PersistedResult;
  hasRecording: boolean;
}

interface ListeningSessionState {
  exercise: PersistedExercise;
  selected: string | null;
  showResult: boolean;
  playbackSpeed: number;
}

interface DutchSessionState {
  currentTheme: string;
  writing: WritingSessionState;
  speaking: SpeakingSessionState;
  listening: ListeningSessionState;
}

interface DutchSessionContextValue {
  state: DutchSessionState;
  hydrated: boolean;
  speakingAudioBlob: Blob | null;
  setCurrentTheme: (theme: string) => void;
  setWritingState: (next: Partial<WritingSessionState>) => void;
  resetWritingState: () => void;
  setSpeakingState: (next: Partial<SpeakingSessionState>) => void;
  resetSpeakingState: () => void;
  setListeningState: (next: Partial<ListeningSessionState>) => void;
  resetListeningState: () => void;
  setSpeakingAudioBlob: (blob: Blob | null) => void;
}

const STORAGE_KEY = 'dutch_session_v1';

const defaultState: DutchSessionState = {
  currentTheme: 'Dagelijkse routine',
  writing: { exercise: null, text: '', result: null },
  speaking: { exercise: null, result: null, hasRecording: false },
  listening: { exercise: null, selected: null, showResult: false, playbackSpeed: 1 },
};

const DutchSessionContext = createContext<DutchSessionContextValue | null>(null);

export function DutchSessionProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<DutchSessionState>(defaultState);
  const [hydrated, setHydrated] = useState(false);
  const [speakingAudioBlob, setSpeakingAudioBlob] = useState<Blob | null>(null);

  useEffect(() => {
    if (typeof window === 'undefined') return;

    fetch('/db_version.json')
      .then(res => {
        if (!res.ok) throw new Error('No db_version.json found');
        return res.json();
      })
      .then(data => {
        const currentVersion = window.localStorage.getItem('db_version');
        if (currentVersion && currentVersion !== String(data.last_reset)) {
          window.localStorage.removeItem(STORAGE_KEY);
          window.localStorage.setItem('db_version', String(data.last_reset));
          window.location.reload();
        } else if (!currentVersion && data.last_reset) {
          window.localStorage.setItem('db_version', String(data.last_reset));
        }
      })
      .catch(err => {
        // Ignore if file doesn't exist
      });
  }, []);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    try {
      const raw = window.localStorage.getItem(STORAGE_KEY);
      if (raw) {
        const parsed = JSON.parse(raw);
        setState({
          ...defaultState,
          ...parsed,
          writing: { ...defaultState.writing, ...(parsed?.writing || {}) },
          speaking: { ...defaultState.speaking, ...(parsed?.speaking || {}) },
          listening: { ...defaultState.listening, ...(parsed?.listening || {}) },
        });
      }
    } catch (err) {
      console.error('Failed to restore Dutch session state:', err);
    } finally {
      setHydrated(true);
    }
  }, []);

  useEffect(() => {
    if (!hydrated || typeof window === 'undefined') return;
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  }, [state, hydrated]);

  const value = useMemo<DutchSessionContextValue>(
    () => ({
      state,
      hydrated,
      speakingAudioBlob,
      setCurrentTheme: (theme: string) => setState((prev) => ({ ...prev, currentTheme: theme })),
      setWritingState: (next) =>
        setState((prev) => ({ ...prev, writing: { ...prev.writing, ...next } })),
      resetWritingState: () =>
        setState((prev) => ({ ...prev, writing: { ...defaultState.writing } })),
      setSpeakingState: (next) =>
        setState((prev) => ({ ...prev, speaking: { ...prev.speaking, ...next } })),
      resetSpeakingState: () => {
        setSpeakingAudioBlob(null);
        setState((prev) => ({ ...prev, speaking: { ...defaultState.speaking } }));
      },
      setListeningState: (next) =>
        setState((prev) => ({ ...prev, listening: { ...prev.listening, ...next } })),
      resetListeningState: () =>
        setState((prev) => ({ ...prev, listening: { ...defaultState.listening } })),
      setSpeakingAudioBlob,
    }),
    [state, hydrated, speakingAudioBlob]
  );

  return <DutchSessionContext.Provider value={value}>{children}</DutchSessionContext.Provider>;
}

export function useDutchSession() {
  const context = useContext(DutchSessionContext);
  if (!context) {
    throw new Error('useDutchSession must be used within DutchSessionProvider');
  }
  return context;
}
