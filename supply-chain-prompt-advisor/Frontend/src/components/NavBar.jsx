export default function NavBar({ user, onLogout }) {
  return (
    <header className="app-navbar">
      <div>
        <p className="app-overline">Enterprise supply chain AI</p>
        <h1>Supply Chain Prompt Advisor</h1>
      </div>
      <div className="nav-actions">
        <div className="user-pill">
          <span className="user-dot" aria-hidden="true" />
          {user?.username ?? 'Authenticated user'}
        </div>
        <button className="secondary-button" type="button" onClick={onLogout}>
          Logout
        </button>
      </div>
    </header>
  );
}
