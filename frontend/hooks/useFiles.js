import { useState, useEffect, useCallback } from 'react';
import api from '../api/cloud-vault';

export default function useFiles() {
  const [view, setView] = useState('mine');
  const [folderId, setFolderId] = useState(null);
  const [search, setSearch] = useState('');
  const [sort, setSort] = useState('name');
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [conflictQueue, setConflictQueue] = useState([]);

  const fetchItems = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      let url;
      if (folderId !== null) {
        url = `/api/files/${folderId}?sort_by=${sort}&search=${encodeURIComponent(search)}`;
      } else if (view === 'shared') url = '/api/files/shared';
      else if (view === 'recent') url = '/api/files/recent';
      else if (view === 'trash') url = '/api/files/trash';
      else url = `/api/files/0?sort_by=${sort}&search=${encodeURIComponent(search)}`;

      const { data } = await api.get(url);
      setItems(data);
    } catch (e) {
      console.error('Failed to load files:', e);
      const msg = e.response?.status === 401
        ? 'Session expired — please log in again'
        : (e.response?.data?.detail || e.message || 'Cannot reach the backend');
      setError(msg);
      setItems([]);
    } finally {
      setLoading(false);
    }
  }, [view, folderId, sort, search]);

  useEffect(() => { fetchItems(); }, [fetchItems]);

  const uploadOne = async (file, action) => {
    const fd = new FormData();
    fd.append('file', file);
    await api.post(`/api/files/upload/${folderId ?? 0}?conflict_action=${action}`, fd);
  };

  const uploadFiles = async (files) => {
    const conflicts = [];
    let uploaded = 0;
    for (const file of files) {
      const exists = items.some((i) => !i.is_folder && i.name === file.name);
      if (exists) conflicts.push(file);
      else { await uploadOne(file, 'rename'); uploaded++; }
    }
    if (conflicts.length) setConflictQueue((q) => [...q, ...conflicts]);
    await fetchItems();
    return { uploaded, conflicts: conflicts.length };
  };

  const resolveConflict = async (action) => {
    const [file, ...rest] = conflictQueue;
    await uploadOne(file, action);
    setConflictQueue(rest);
    if (rest.length === 0) await fetchItems();
  };

  const cancelConflicts = () => setConflictQueue([]);

  const createFolder = async (name) => { await api.post('/api/files/folders', { name, parent_id: folderId }); await fetchItems(); };
  const renameItem = async (id, name) => { await api.post(`/api/files/${id}/rename`, { name }); await fetchItems(); };
  const moveItem = async (id, target) => { await api.post(`/api/files/${id}/move`, { parent_id: target }); await fetchItems(); };
  const copyItem = async (id) => { await api.post(`/api/files/${id}/copy`); await fetchItems(); };
  const deleteItem = async (id) => { await api.delete(`/api/files/${id}`); await fetchItems(); };
  const restoreItem = async (id) => { await api.post(`/api/files/${id}/restore`); await fetchItems(); };
  const deleteForever = async (id) => { await api.delete(`/api/files/${id}/permanent`); await fetchItems(); };
  const shareItem = async (id, email) => api.post(`/api/files/${id}/share`, { email });
  const downloadItem = async (id) => {
    const { data } = await api.get(`/api/files/${id}/download`);
    window.open(data.url, '_blank');
  };

  const openFolder = (id) => { setFolderId(id); setSearch(''); };
  const changeView = (v) => { setView(v); setFolderId(null); setSearch(''); };

  return {
    view, folderId, search, sort, items, loading, error, conflictQueue,
    setSearch, setSort, openFolder, changeView,
    uploadFiles, resolveConflict, cancelConflicts,
    createFolder, renameItem, moveItem, copyItem,
    deleteItem, restoreItem, deleteForever, shareItem, downloadItem,
  };
}