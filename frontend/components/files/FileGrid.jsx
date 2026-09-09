import FileCard from './FileCard';
import FileTable from './FileTable';
import EmptyState from '../common/EmptyState';

export default function FileGrid({ items, mode, view, loading, error, onItemClick, onMenu }) {
  if (loading) return <div className="text-center text-gray-400 py-16 text-sm">Loading…</div>;

  if (error) return (
    <div className="bg-red-50 border border-red-200 text-red-700 rounded-xl px-4 py-6 text-sm text-center">
      ⚠️ Could not load your files: <b>{error}</b>
      <div className="text-xs text-red-500 mt-2">
        Make sure the backend is running (<code>python run.py</code>) and you're logged in with the account that owns these files.
      </div>
    </div>
  );

  if (!items.length) return <EmptyState message="Nothing here yet. Drop some files above!" />;

  if (mode === 'list') return <FileTable items={items} onClick={onItemClick} onMenu={onMenu} />;
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
      {items.map((item) => (
        <FileCard key={item.id} item={item} view={view} onClick={() => onItemClick(item)} onMenu={onMenu} />
      ))}
    </div>
  );
}