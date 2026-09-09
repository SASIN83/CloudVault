export default function EmptyState({ message = 'Nothing here yet' }) {
  return (
    <div className="text-center text-gray-400 py-16 text-sm">
      <span className="text-4xl block mb-3">🗂️</span>
      {message}
    </div>
  );
}