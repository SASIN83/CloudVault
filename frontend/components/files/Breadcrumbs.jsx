export default function Breadcrumbs({ trail, onRoot, onCrumb, rootLabel = 'My Files' }) {
  return (
    <div className="flex items-center gap-1 text-sm font-medium flex-wrap">
      <button className="hover:text-indigo-600 text-gray-700" onClick={onRoot}>{rootLabel}</button>
      {trail.map((crumb, idx) => (
        <span key={crumb.id} className="flex items-center gap-1">
          <span className="text-gray-400">/</span>
          <button className="hover:text-indigo-600 text-gray-700" onClick={() => onCrumb(idx)}>{crumb.name}</button>
        </span>
      ))}
    </div>
  );
}