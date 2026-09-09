import { fileMeta, formatBytes, formatDate } from '../../utils/fileUtils';

export default function FileCard({ item, view, onClick, onMenu }) {
  const { emoji, bg } = fileMeta(item);
  return (
    <div onClick={onClick}
      className="group relative border border-gray-200 rounded-xl bg-white p-4 flex flex-col items-center gap-2 hover:shadow-md hover:border-indigo-300 cursor-pointer transition">
      <div className={`w-12 h-12 rounded-xl ${bg} flex items-center justify-center text-2xl`}>{emoji}</div>
      <div className="text-sm font-medium text-center break-words line-clamp-2 w-full">{item.name}</div>
      <div className="text-[11px] text-gray-400">
        {item.is_folder ? 'Folder' : formatBytes(item.size)} · {formatDate(item.updated_at)}
      </div>
      {item.shared_emails?.length > 0 &&
        <span className="text-[10px] bg-indigo-50 text-indigo-600 px-2 py-0.5 rounded-full">🔗 shared</span>}
      {view === 'shared' && item.owner_email &&
        <span className="text-[10px] bg-green-50 text-green-600 px-2 py-0.5 rounded-full">by {item.owner_email}</span>}
      <button
        onClick={(e) => { e.stopPropagation(); onMenu(e, item); }}
        className="absolute top-2 right-2 w-7 h-7 rounded-lg hover:bg-gray-100 opacity-100 lg:opacity-0 lg:group-hover:opacity-100">
        ⋮
      </button>
    </div>
  );
}