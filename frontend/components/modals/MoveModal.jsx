import { useEffect, useState } from 'react';
import Modal from '../common/Modal';
import api from '../../api/cloud-vault';

export default function MoveModal({ item, onClose, onSubmit }) {
  const [options, setOptions] = useState([]);
  const [target, setTarget] = useState(null);

  useEffect(() => {
    if (!item) return;
    api.get('/api/files/folder-options', { params: { exclude: item.is_folder ? item.id : undefined } })
      .then(({ data }) => setOptions(data));
  }, [item]);

  if (!item) return null;
  return (
    <Modal open onClose={onClose} title="📂 Move to folder">
      <select value={target ?? ''} onChange={(e) => setTarget(e.target.value === '' ? null : Number(e.target.value))}
        className="w-full border rounded-lg px-3 py-2 text-sm mb-5">
        {options.map((o) => <option key={o.id ?? 'root'} value={o.id ?? ''}>{o.name}</option>)}
      </select>
      <div className="flex gap-3">
        <button onClick={onClose} className="flex-1 border rounded-lg py-2 text-sm">Cancel</button>
        <button onClick={() => onSubmit(target)}
          className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg py-2 text-sm font-semibold">Move</button>
      </div>
    </Modal>
  );
}