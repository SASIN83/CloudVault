import { useState } from 'react';
import Modal from '../common/Modal';

export default function NewFolderModal({ open, onClose, onSubmit }) {
  const [name, setName] = useState('');
  const submit = () => { if (name.trim()) { onSubmit(name.trim()); setName(''); onClose(); } };
  return (
    <Modal open={open} onClose={onClose} title="📁 Create folder">
      <input value={name} onChange={(e) => setName(e.target.value)}
        onKeyDown={(e) => e.key === 'Enter' && submit()}
        placeholder="Folder name" className="w-full border rounded-lg px-3 py-2 text-sm mb-5" autoFocus />
      <div className="flex gap-3">
        <button onClick={onClose} className="flex-1 border rounded-lg py-2 text-sm">Cancel</button>
        <button onClick={submit}
          className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg py-2 text-sm font-semibold">Create</button>
      </div>
    </Modal>
  );
}