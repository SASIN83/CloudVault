const NAV = [
  { id: 'mine', label: 'My Files', icon: '📂' },
  { id: 'shared', label: 'Shared with me', icon: '🔗' },
  { id: 'recent', label: 'Recent', icon: '🕒' },
  { id: 'trash', label: 'Trash', icon: '🗑️' },
];

export default function Sidebar({ view, onView, onNewFolder, open, onClose }) {
  return (
    <>
      {open && <div className="fixed inset-0 bg-black/40 z-30 lg:hidden" onClick={onClose} />}
      <aside className={`fixed left-0 top-14 bottom-0 w-64 bg-white border-r border-gray-200 p-4 z-30
        flex flex-col gap-4 transition-transform lg:translate-x-0
        ${open ? 'translate-x-0' : '-translate-x-full'}`}>
        <button onClick={onNewFolder}
          className="w-full bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg py-2 text-sm font-semibold">
          ＋ New Folder
        </button>
        <nav className="flex flex-col gap-1 text-sm">
          {NAV.map((n) => (
            <button key={n.id} onClick={() => { onView(n.id); onClose(); }}
              className={`px-3 py-2 rounded-lg text-left hover:bg-gray-100
                ${view === n.id ? 'bg-indigo-50 text-indigo-700 font-semibold' : ''}`}>
              {n.icon} {n.label}
            </button>
          ))}
        </nav>
        <div className="mt-auto border-t pt-4 text-xs text-gray-500">
            <div className="flex justify-between mb-1"><span>AWS S3 Storage</span><span>5 GB</span></div>
            <div className="h-2 bg-gray-200 rounded-full"><div className="h-2 bg-indigo-500 rounded-full" style={{ width: '2%' }} /></div>
            <p className="mt-2">🔒 Private bucket · signed URLs only</p>
        </div>
      </aside>
    </>
  );
}