import { useEffect, useState } from 'react';
import { Clock, Plus, Trash2, CalendarClock } from 'lucide-react';
import { schedulerApi } from '~/services/schedulerApi';
import type { CronJob } from '~/services/schedulerApi';

export default function SchedulerPage() {
  const [jobs, setJobs] = useState<CronJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);

  // Form State
  const [taskType, setTaskType] = useState('dutch');
  const [hour, setHour] = useState('12');
  const [minute, setMinute] = useState('00');
  const [ampm, setAmpm] = useState('AM');
  const [inputNumber, setInputNumber] = useState('1');

  const fetchJobs = async () => {
    try {
      setLoading(true);
      const data = await schedulerApi.getJobs();
      setJobs(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJobs();
  }, []);

  const handleAddJob = async (e: React.FormEvent) => {
    e.preventDefault();
    const schedule_time = `${hour.padStart(2, '0')}:${minute.padStart(2, '0')} ${ampm}`;
    const newJob: CronJob = {
      task_type: taskType,
      schedule_time,
      input_number: parseInt(inputNumber) || 1,
    };
    try {
      await schedulerApi.createJob(newJob);
      setShowForm(false);
      fetchJobs();
    } catch (e) {
      console.error(e);
      alert('Failed to add job');
    }
  };

  const handleDelete = async (id?: string) => {
    if (!id) return;
    try {
      await schedulerApi.deleteJob(id);
      fetchJobs();
    } catch (e) {
      console.error(e);
      alert('Failed to delete job');
    }
  };

  return (
    <div className="page-container" style={{ padding: '100px 4% 40px', maxWidth: '1000px', margin: '0 auto', minHeight: '100vh' }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '40px' }}>
        <div>
          <h1 style={{ 
            fontSize: '2.5rem', 
            fontWeight: 800, 
            background: 'linear-gradient(to right, #4ade80, #3b82f6)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            marginBottom: '10px',
            display: 'flex',
            alignItems: 'center',
            gap: '12px'
          }}>
            <CalendarClock size={36} color="#4ade80" /> Background Tasks
          </h1>
          <p style={{ color: 'var(--text-muted)' }}>Manage automated generations and cron jobs</p>
        </div>
        
        <button 
          onClick={() => setShowForm(!showForm)}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            background: 'var(--primary)',
            color: '#fff',
            border: 'none',
            padding: '12px 20px',
            borderRadius: '12px',
            fontWeight: 600,
            cursor: 'pointer',
            boxShadow: '0 8px 20px rgba(74, 222, 128, 0.3)',
            transition: 'transform 0.2s',
          }}
          onMouseEnter={(e) => e.currentTarget.style.transform = 'scale(1.05)'}
          onMouseLeave={(e) => e.currentTarget.style.transform = 'scale(1)'}
        >
          {showForm ? 'Cancel' : <><Plus size={18} /> New Job</>}
        </button>
      </header>

      {showForm && (
        <form onSubmit={handleAddJob} style={{
          background: 'rgba(255,255,255,0.03)',
          border: '1px solid var(--glass-border)',
          borderRadius: '16px',
          padding: '24px',
          marginBottom: '40px',
          display: 'grid',
          gap: '20px',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          animation: 'fadeIn 0.3s ease'
        }}>
          <div>
            <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-muted)', fontSize: '0.9rem' }}>Task Type</label>
            <select 
              value={taskType} 
              onChange={e => setTaskType(e.target.value)}
              style={{ width: '100%', padding: '12px', borderRadius: '8px', background: 'rgba(0,0,0,0.2)', border: '1px solid var(--glass-border)', color: 'var(--text-light)', outline: 'none' }}
            >
              <option value="dutch">Dutch Exercises</option>
              <option value="thenews">News Articles</option>
              <option value="graphics_image">Graphics (Images)</option>
              <option value="graphics_video">Graphics (Videos)</option>
            </select>
          </div>

          <div>
            <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-muted)', fontSize: '0.9rem' }}>Time (12 hr)</label>
            <div style={{ display: 'flex', gap: '8px' }}>
              <select value={hour} onChange={e => setHour(e.target.value)} style={{ flex: 1, padding: '12px', borderRadius: '8px', background: 'rgba(0,0,0,0.2)', border: '1px solid var(--glass-border)', color: 'var(--text-light)', outline: 'none' }}>
                {Array.from({length: 12}, (_, i) => (i + 1).toString()).map(h => <option key={h} value={h}>{h}</option>)}
              </select>
              <select value={minute} onChange={e => setMinute(e.target.value)} style={{ flex: 1, padding: '12px', borderRadius: '8px', background: 'rgba(0,0,0,0.2)', border: '1px solid var(--glass-border)', color: 'var(--text-light)', outline: 'none' }}>
                {['00', '15', '30', '45'].map(m => <option key={m} value={m}>{m}</option>)}
              </select>
              <select value={ampm} onChange={e => setAmpm(e.target.value)} style={{ flex: 1, padding: '12px', borderRadius: '8px', background: 'rgba(0,0,0,0.2)', border: '1px solid var(--glass-border)', color: 'var(--text-light)', outline: 'none' }}>
                <option value="AM">AM</option>
                <option value="PM">PM</option>
              </select>
            </div>
          </div>

          <div>
            <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-muted)', fontSize: '0.9rem' }}>Input Number</label>
            <input 
              type="number" 
              min="1" 
              value={inputNumber} 
              onChange={e => setInputNumber(e.target.value)}
              style={{ width: '100%', padding: '12px', borderRadius: '8px', background: 'rgba(0,0,0,0.2)', border: '1px solid var(--glass-border)', color: 'var(--text-light)', outline: 'none' }}
            />
          </div>

          <div style={{ display: 'flex', alignItems: 'flex-end' }}>
            <button type="submit" style={{ width: '100%', padding: '12px', borderRadius: '8px', background: 'var(--primary)', color: '#fff', border: 'none', fontWeight: 600, cursor: 'pointer' }}>
              Schedule Job
            </button>
          </div>
        </form>
      )}

      <div>
        <h2 style={{ fontSize: '1.2rem', marginBottom: '20px', color: 'var(--text-light)', borderBottom: '1px solid var(--glass-border)', paddingBottom: '10px' }}>Active Jobs</h2>
        
        {loading ? (
          <p style={{ color: 'var(--text-muted)' }}>Loading jobs...</p>
        ) : jobs.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '60px 0', background: 'rgba(255,255,255,0.01)', borderRadius: '16px', border: '1px dashed var(--glass-border)' }}>
            <Clock size={48} color="var(--text-muted)" style={{ marginBottom: '16px', opacity: 0.5 }} />
            <p style={{ color: 'var(--text-muted)' }}>No scheduled background tasks found.</p>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {jobs.map(job => (
              <div key={job.id} style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                padding: '20px',
                background: 'rgba(0,0,0,0.2)',
                border: '1px solid var(--glass-border)',
                borderRadius: '12px',
                boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
              }}>
                <div>
                  <h3 style={{ fontSize: '1.1rem', marginBottom: '6px', fontWeight: 600, color: 'var(--text-light)' }}>
                    {job.task_type === 'dutch' && '🇳🇱 Dutch Exercises'}
                    {job.task_type === 'thenews' && '📰 News Generation'}
                    {job.task_type === 'graphics_image' && '🎨 Graphics (Image)'}
                    {job.task_type === 'graphics_video' && '🎥 Graphics (Video)'}
                  </h3>
                  <div style={{ display: 'flex', gap: '16px', color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><Clock size={14} /> At {job.schedule_time} daily</span>
                    <span style={{ background: 'rgba(255,255,255,0.1)', padding: '2px 8px', borderRadius: '4px' }}>Input Parameter: {job.input_number}</span>
                  </div>
                </div>
                
                <button 
                  onClick={() => handleDelete(job.id)}
                  style={{
                    background: 'rgba(239, 68, 68, 0.1)',
                    color: '#ef4444',
                    border: '1px solid rgba(239, 68, 68, 0.2)',
                    padding: '10px',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    transition: 'all 0.2s',
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(239, 68, 68, 0.2)'}
                  onMouseLeave={(e) => e.currentTarget.style.background = 'rgba(239, 68, 68, 0.1)'}
                >
                  <Trash2 size={18} />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
      
      <style>{`
        @keyframes fadeIn { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }
      `}</style>
    </div>
  );
}
