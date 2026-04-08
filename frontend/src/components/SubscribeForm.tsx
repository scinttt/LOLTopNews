import React, { useState } from 'react';
import { subscribe } from '../services/api';

const SubscribeForm: React.FC = () => {
  const [email, setEmail] = useState('');
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [message, setMessage] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim()) return;

    setStatus('loading');
    try {
      const result = await subscribe(email.trim());
      setStatus('success');
      setMessage(
        result.action === 'already_active'
          ? 'You are already subscribed!'
          : 'Subscribed! You will receive email notifications for new patch analyses.'
      );
      setEmail('');
    } catch {
      setStatus('error');
      setMessage('Subscription failed. Please try again.');
    }
  };

  return (
    <div className="subscribe-form">
      <h3 className="subscribe-title">Subscribe to Patch Updates</h3>
      {status === 'success' ? (
        <p className="subscribe-success">{message}</p>
      ) : (
        <form onSubmit={handleSubmit} className="subscribe-input-group">
          <input
            type="email"
            value={email}
            onChange={(e) => { setEmail(e.target.value); setStatus('idle'); }}
            placeholder="your@email.com"
            className="subscribe-input"
            required
          />
          <button
            type="submit"
            disabled={status === 'loading'}
            className="subscribe-button"
          >
            {status === 'loading' ? '...' : 'Subscribe'}
          </button>
        </form>
      )}
      {status === 'error' && <p className="subscribe-error">{message}</p>}
      {status === 'idle' && (
        <p className="subscribe-hint">Get notified when a new patch analysis is published.</p>
      )}
    </div>
  );
};

export default SubscribeForm;
