export const formatBytes = (bytes) => {
  if (!bytes) return '—';
  const units = ['B', 'KB', 'MB', 'GB'];
  let i = 0, b = bytes;
  while (b >= 1024 && i < units.length - 1) { b /= 1024; i++; }
  return `${b.toFixed(b >= 10 || i === 0 ? 0 : 1)} ${units[i]}`;
};

export const formatDate = (iso) =>
  new Date(iso).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });

export const fileMeta = (item) => {
  if (item.is_folder) return { emoji: '📁', bg: 'bg-amber-100' };
  const ext = item.name.split('.').pop().toLowerCase();
  if (['png', 'jpg', 'jpeg', 'gif', 'svg', 'webp'].includes(ext)) return { emoji: '🖼️', bg: 'bg-purple-100' };
  if (['xls', 'xlsx', 'csv'].includes(ext)) return { emoji: '📊', bg: 'bg-green-100' };
  if (ext === 'pdf') return { emoji: '📕', bg: 'bg-red-100' };
  if (['zip', 'rar', '7z'].includes(ext)) return { emoji: '🗜️', bg: 'bg-gray-200' };
  return { emoji: '📄', bg: 'bg-blue-100' };
};

// Client-side preview of the "Keep both" name: new file (2).docx
export const suggestCopyName = (name, items) => {
  const taken = (n) => items.some((i) => !i.is_folder && i.name === n);
  if (!taken(name)) return name;
  const dot = name.lastIndexOf('.');
  const base = dot > 0 ? name.slice(0, dot) : name;
  const ext = dot > 0 ? name.slice(dot) : '';
  let c = 1;
  while (taken(`${base} (${c})${ext}`)) c++;
  return `${base} (${c})${ext}`;
};