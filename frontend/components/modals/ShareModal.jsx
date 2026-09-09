import { useState } from 'react';
import Modal from '../common/Modal';

export default function ShareModal({ item, onClose, onShare, onUnshare }) {
  const [email, setEmail] = useState('');
  if (!item) return null;

  const submit = () => {
    const clean = email.trim().toLowerCase();
    if (!clean) return;
    onShare(clean);
    setEmail('');
  };

  return (
    <Modal open onClose={onClose} title={`🔗 Sharing “${item.name}”`}>
      {/* ── Current access list ── */}
      <div className="mb-4">
        <label className="block text-xs font-semibold text-gray-600 mb-2">People with access</label>
        {item.shared_emails?.length ? (
          <ul className="divide-y divide-gray-100 border border-gray-200 rounded-lg overflow-hidden">
            {item.shared_emails.map((em) => (
              <li key={em} className="flex items-center justify-between px-3 py-2 text-sm bg-white">
                <span className="truncate pr-2">{em}</span>
                <button
                  onClick={() => onUnshare(em)}
                  className="text-xs text-red-600 hover:text-red-700 font-semibold whitespace-nowrap"
                >
                  ✕ Remove
                </button>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-xs text-gray-400 border border-dashed border-gray-200 rounded-lg px-3 py-2">
            Not shared with anyone yet — only you can access this.
          </p>
        )}
      </div>

      {/* ── Add new person ── */}
      <label className="block text-xs font-semibold text-gray-600 mb-1">Share with</label>
      <div className="flex gap-2">
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && submit()}
          placeholder="xyz@gmail.com"
          className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
        />
        <button
          onClick={submit}
          className="bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg px-4 py-2 text-sm font-semibold"
        >
          Share
        </button>
      </div>

      <p className="mt-3 text-[11px] text-gray-400">
        🔒 Only a signed-in user with this exact email can open the item (via a 15-min signed S3 URL).
        Removing someone revokes access immediately.
      </p>
    </Modal>
  );
}