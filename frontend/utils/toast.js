// Framework-free toast notifications. Works from any component, no provider needed.
let container = null;

function getContainer() {
  if (!container) {
    container = document.createElement('div');
    container.style.cssText =
      'position:fixed;bottom:20px;right:20px;z-index:9999;display:flex;flex-direction:column;gap:8px;pointer-events:none;';
    document.body.appendChild(container);
  }
  return container;
}

export function toast(message, type = 'success') {
  const colors = { success: '#16a34a', error: '#dc2626', info: '#111827' };
  const icons = { success: '✅', error: '⚠️', info: 'ℹ️' };

  const el = document.createElement('div');
  el.style.cssText =
    `background:${colors[type] || colors.info};color:#fff;font-size:14px;padding:12px 16px;` +
    'border-radius:12px;box-shadow:0 10px 25px rgba(0,0,0,.25);display:flex;align-items:center;gap:8px;' +
    'max-width:320px;opacity:0;transform:translateY(8px);transition:all .25s ease;';
  el.innerHTML = '<span></span><span></span>';
  el.children[0].textContent = icons[type] || icons.info;
  el.children[1].textContent = message;

  getContainer().appendChild(el);
  requestAnimationFrame(() => {
    el.style.opacity = '1';
    el.style.transform = 'translateY(0)';
  });
  setTimeout(() => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(8px)';
    setTimeout(() => el.remove(), 300);
  }, 4000);
}

export default toast;