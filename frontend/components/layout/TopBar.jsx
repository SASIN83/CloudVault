import logo from '../../src/assets/logo.svg';

export default function TopBar({ search, onSearch, onMenu, userEmail, onLogout }) {
  return (
    <header className="fixed top-0 inset-x-0 h-14 bg-white border-b border-gray-200 flex items-center gap-3 px-4 z-40">
      <button className="lg:hidden text-2xl leading-none" onClick={onMenu}>☰</button>
      <div className="flex items-center gap-2 font-extrabold text-indigo-600 text-lg whitespace-nowrap">
        <img src={logo} alt="logo" className="w-6 h-6" /> CloudVault
      </div>
      <div className="flex-1 max-w-xl mx-auto">
        <input
          type="text" value={search} onChange={(e) => onSearch(e.target.value)}
          placeholder="🔍  Search files & folders…"
          className="w-full border border-gray-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
        />
      </div>
      <div className="flex items-center gap-2">
        <div className="w-8 h-8 rounded-full bg-indigo-600 text-white flex items-center justify-center text-xs font-bold">
          {userEmail?.[0]?.toUpperCase() || 'U'}
        </div>
        <span className="hidden md:block text-sm text-gray-600">{userEmail}</span>
        <button onClick={onLogout} className="text-xs text-gray-500 hover:text-red-500">Logout</button>
      </div>
    </header>
  );
}