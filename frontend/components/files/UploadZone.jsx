import { useRef, useState } from 'react';

export default function UploadZone({ onFiles, uploading = false }) {
  const inputRef = useRef(null);
  const [dragging, setDragging] = useState(false);

  return (
    <div
      onClick={() => !uploading && inputRef.current.click()}
      onDragOver={(e) => { e.preventDefault(); if (!uploading) setDragging(true); }}
      onDragLeave={() => setDragging(false)}
      onDrop={(e) => {
        e.preventDefault(); setDragging(false);
        if (!uploading) onFiles([...e.dataTransfer.files]);
      }}
      className={`border-2 border-dashed rounded-xl p-6 text-center text-sm mb-6 transition
        ${uploading
          ? 'border-indigo-400 bg-indigo-50 text-indigo-600 cursor-wait'
          : dragging
            ? 'border-indigo-500 bg-indigo-50 text-indigo-600 cursor-pointer'
            : 'border-gray-300 bg-white/60 text-gray-500 cursor-pointer hover:border-indigo-400'}`}
    >
      <input ref={inputRef} type="file" multiple className="hidden"
        onChange={(e) => { onFiles([...e.target.files]); e.target.value = ''; }} />

      {uploading ? (
        <>
          <div className="mx-auto mb-2 w-8 h-8 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin" />
          Uploading… please wait
        </>
      ) : (
        <>
          <span className="text-2xl block mb-1">📥</span>
          Drag & drop files here, or click to browse
          <span className="text-xs text-gray-400 block mt-1">multiple files supported · max 50 MB each</span>
        </>
      )}
    </div>
  );
}