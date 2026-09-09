import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import useFiles from '../hooks/useFiles';
import { useAuth } from '../context/AuthContext';
import toast from '../utils/toast';

import TopBar from '../components/layout/TopBar';
import Sidebar from '../components/layout/Sidebar';
import Breadcrumbs from '../components/files/Breadcrumbs';
import UploadZone from '../components/files/UploadZone';
import FileGrid from '../components/files/FileGrid';
import ItemMenu from '../components/files/ItemMenu';
import ConflictModal from '../components/modals/ConflictModal';
import ShareModal from '../components/modals/ShareModal';
import MoveModal from '../components/modals/MoveModal';
import NewFolderModal from '../components/modals/NewFolderModal';

const TITLES = { shared: 'Shared with me', recent: 'Recent', trash: 'Trash' };

export default function FileManagerPage() {
  const fm = useFiles();
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [mode, setMode] = useState('grid');
  const [trail, setTrail] = useState([]);
  const [foreign, setForeign] = useState(false);   // browsing a folder owned by someone else
  const [menu, setMenu] = useState(null);
  const [shareTarget, setShareTarget] = useState(null);
  const [moveTarget, setMoveTarget] = useState(null);
  const [folderModal, setFolderModal] = useState(false);
  const [uploading, setUploading] = useState(false);

  const run = async (fn, successMsg) => {
    try {
      await fn();
      if (successMsg) toast(successMsg);
    } catch (e) {
      toast(e.response?.data?.detail || e.message || 'Something went wrong', 'error');
    }
  };

  const openFolder = (item) => {
    fm.openFolder(item.id);
    setForeign(!!item.owner_email);
    setTrail((t) => [...t, { id: item.id, name: item.name }]);
  };
  const goRoot = () => { fm.openFolder(null); setForeign(false); setTrail([]); };
  const goCrumb = (idx) => { fm.openFolder(trail[idx].id); setTrail((t) => t.slice(0, idx + 1)); };
  const changeView = (v) => { fm.changeView(v); setForeign(false); setTrail([]); };

  const handleUpload = async (files) => {
    setUploading(true);
    try {
      const res = await fm.uploadFiles(files);
      if (res.uploaded > 0) toast(`✅ ${res.uploaded} file${res.uploaded > 1 ? 's' : ''} uploaded successfully`);
      if (res.conflicts > 0) toast(`⚠️ ${res.conflicts} duplicate file${res.conflicts > 1 ? 's' : ''} — choose an action`, 'error');
    } catch (e) {
      toast(e.response?.data?.detail || 'Upload failed — is the backend running & S3 configured?', 'error');
    } finally {
      setUploading(false);
    }
  };

  const handleItemClick = (item) => {
    if (fm.view === 'trash') return;
    if (item.is_folder) return openFolder(item);
    run(() => fm.downloadItem(item.id), '🔐 Signed S3 URL generated — download started');
  };

  const resolveConflict = async (action) => {
    try {
      await fm.resolveConflict(action);
      toast(action === 'replace' ? '🔁 File replaced' : '📄 Saved as a new copy');
    } catch (e) {
      toast(e.response?.data?.detail || 'Could not resolve duplicate', 'error');
    }
  };

  const menuActions = (item) => {
    // Not my file (shared with me / inside someone's shared folder) → view-only
    if (item.owner_email) {
      return [{ icon: '⬇', label: 'Download', run: () => run(() => fm.downloadItem(item.id), '🔐 Download started') }];
    }
    if (fm.view === 'trash') return [
      { icon: '♻️', label: 'Restore', run: () => run(() => fm.restoreItem(item.id), '♻️ Restored') },
      { icon: '🗑', label: 'Delete forever', danger: true, run: () => window.confirm('Delete forever?') && run(() => fm.deleteForever(item.id), '🗑 Deleted forever') },
    ];
    return [
      { icon: '⬇', label: 'Download', run: () => run(() => fm.downloadItem(item.id), '🔐 Download started') },
      { icon: '🔗', label: 'Share…', run: () => setShareTarget(item) },
      ...(item.is_folder ? [] : [{ icon: '⧉', label: 'Copy', run: () => run(() => fm.copyItem(item.id), '⧉ Copied') }]),
      { icon: '📂', label: 'Move to…', run: () => setMoveTarget(item) },
      { icon: '✏️', label: 'Rename', run: () => run(async () => { const n = window.prompt('Rename to:', item.name); if (n) await fm.renameItem(item.id, n); }, '✏️ Renamed') },
      { icon: '🗑', label: 'Delete', danger: true, run: () => run(() => fm.deleteItem(item.id), '🗑 Moved to Trash') },
    ];
  };

  return (
    <>
      <TopBar search={fm.search} onSearch={fm.setSearch} userEmail={user?.email}
        onMenu={() => setSidebarOpen(true)}
        onLogout={() => { logout(); navigate('/login'); }} />
      <Sidebar view={fm.view} onView={changeView} open={sidebarOpen}
        onClose={() => setSidebarOpen(false)} onNewFolder={() => setFolderModal(true)} />

      <main className="pt-14 lg:pl-64 min-h-screen bg-gray-50">
        <div className="p-4 lg:p-6 max-w-7xl mx-auto">
          <div className="flex flex-wrap items-center gap-3 mb-4">
            <div className="flex-1 min-w-[200px]">
              {(fm.view === 'mine' || fm.folderId !== null) ? (
                <Breadcrumbs trail={trail} onRoot={goRoot} onCrumb={goCrumb}
                  rootLabel={fm.view === 'shared' ? 'Shared with me' : 'My Files'} />
              ) : (
                <span className="text-sm font-semibold text-gray-700">{TITLES[fm.view]}</span>
              )}
            </div>
            <select value={fm.sort} onChange={(e) => fm.setSort(e.target.value)}
              className="border border-gray-300 rounded-lg px-3 py-2 text-sm bg-white">
              <option value="name">Sort: Name (A–Z)</option>
              <option value="date">Sort: Date (newest)</option>
            </select>
            <div className="flex border border-gray-300 rounded-lg overflow-hidden text-sm">
              <button onClick={() => setMode('grid')} className={`px-3 py-2 ${mode === 'grid' ? 'bg-indigo-600 text-white' : 'bg-white'}`}>▦</button>
              <button onClick={() => setMode('list')} className={`px-3 py-2 ${mode === 'list' ? 'bg-indigo-600 text-white' : 'bg-white'}`}>☰</button>
            </div>
          </div>

          {fm.view === 'mine' && !foreign && <UploadZone onFiles={handleUpload} uploading={uploading} />}

          <FileGrid items={fm.items} mode={mode} view={fm.view} loading={fm.loading} error={fm.error}
            onItemClick={handleItemClick}
            onMenu={(e, item) => setMenu({ x: e.clientX, y: e.clientY, item })} />
        </div>
      </main>

      {menu && <ItemMenu x={menu.x} y={menu.y} onClose={() => setMenu(null)} actions={menuActions(menu.item)} />}

      <ConflictModal file={fm.conflictQueue[0]} items={fm.items}
        onResolve={resolveConflict} onCancel={fm.cancelConflicts} />
      <ShareModal item={shareTarget} onClose={() => setShareTarget(null)}
        onSubmit={(email) => run(async () => { await fm.shareItem(shareTarget.id, email); setShareTarget(null); }, `🔗 Shared with ${email}`)} />
      <MoveModal item={moveTarget} onClose={() => setMoveTarget(null)}
        onSubmit={(target) => run(async () => { await fm.moveItem(moveTarget.id, target); setMoveTarget(null); }, '📂 Moved')} />
      <NewFolderModal open={folderModal} onClose={() => setFolderModal(false)}
        onSubmit={(name) => run(() => fm.createFolder(name), `📁 Folder "${name}" created`)} />
    </>
  );
}