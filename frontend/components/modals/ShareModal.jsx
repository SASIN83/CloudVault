import { useState } from 'react';
import Modal from '../common/Modal';

export default function ShareModal({ item, onClose, onSubmit }) {
  const [email, setEmail] = useState('');
  if (!item) return null;
  return (
    <Modal open onClose={onClose} title={`🔗 Share “${item.name}”`}>
      <p className="text-xs text-gray-500 mb-4">
        Only a signed-in user with this exact email can open the file (via a 15-minute signed R2 URL).
      </p>
      <label className="text-xs font-semibold text-gray-600">Email address</label>
      <input type="email" value={email} onChange={(e) => setEmail(e.target.value)}
        placeholder="xyz@gmail.com" className="w-full border rounded-lg px-3 py-2 text-sm mt-1 mb-5" />
      <div className="flex gap-3">
        <button onClick={onClose} className="flex-1 border rounded-lg py-2 text-sm">Cancel</button>
        <button onClick={() => { onSubmit(email); setEmail(''); }}
          className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg py-2 text-sm font-semibold">Share</button>
      </div>
    </Modal>
  );
}