import Modal from '../common/Modal';
import { suggestCopyName } from '../../utils/fileUtils';

export default function ConflictModal({ file, items, onResolve, onCancel }) {
  if (!file) return null;
  return (
    <Modal open onClose={onCancel} title="⚠️ File already exists">
      <p className="text-sm text-gray-600 mb-1">A file named <b>{file.name}</b> already exists in this folder.</p>
      <p className="text-xs text-gray-400 mb-5">
        “Keep both” will save it as <b className="text-indigo-600">{suggestCopyName(file.name, items)}</b>
      </p>
      <div className="flex gap-3">
        <button onClick={() => onResolve('replace')}
          className="flex-1 bg-red-500 hover:bg-red-600 text-white rounded-lg py-2 text-sm font-semibold">Replace</button>
        <button onClick={() => onResolve('rename')}
          className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg py-2 text-sm font-semibold">Keep both</button>
      </div>
    </Modal>
  );
}