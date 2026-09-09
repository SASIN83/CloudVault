import { fileMeta, formatBytes, formatDate } from '../../utils/fileUtils';

export default function FileTable({ items, onClick, onMenu }) {
  return (
    <div className="bg-white border border-gray-200 rounded-xl overflow-hidden">
      <table className="w-full text-sm">
        <thead className="bg-gray-50 text-left text-xs text-gray-500">
          <tr>
            <th className="px-4 py-2">Name</th>
            <th className="px-4 py-2 hidden sm:table-cell">Size</th>
            <th className="px-4 py-2 hidden md:table-cell">Modified</th>
            <th className="px-2 py-2" />
          </tr>
        </thead>
        <tbody>
          {items.map((item) => {
            const { emoji } = fileMeta(item);
            return (
              <tr key={item.id} className="border-t border-gray-100 hover:bg-gray-50 cursor-pointer" onClick={() => onClick(item)}>
                <td className="px-4 py-2">{emoji} {item.name}</td>
                <td className="px-4 py-2 hidden sm:table-cell text-gray-500">{item.is_folder ? '—' : formatBytes(item.size)}</td>
                <td className="px-4 py-2 hidden md:table-cell text-gray-500">{formatDate(item.updated_at)}</td>
                <td className="px-2 py-2">
                  <button onClick={(e) => { e.stopPropagation(); onMenu(e, item); }}>⋮</button>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}