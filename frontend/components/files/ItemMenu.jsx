export default function ItemMenu({ x, y, onClose, actions }) {
  return (
    <div className="fixed inset-0 z-50" onClick={onClose}>
      <div
        className="absolute bg-white border border-gray-200 rounded-xl shadow-xl py-1 w-48 text-sm"
        style={{ left: Math.min(x, window.innerWidth - 200), top: Math.min(y, window.innerHeight - 300) }}
        onClick={(e) => e.stopPropagation()}
      >
        {actions.map((a) => (
          <button key={a.label} onClick={() => { onClose(); a.run(); }}
            className={`w-full text-left px-4 py-2 hover:bg-gray-100 ${a.danger ? 'text-red-600 hover:bg-red-50' : ''}`}>
            {a.icon} {a.label}
          </button>
        ))}
      </div>
    </div>
  );
}