export default function TopBar({ onMenuToggle }) {
  return (
    <header className="topbar">
      <button className="hamburger" onClick={onMenuToggle}>☰</button>
      <h1>PlanViejo</h1>
      <div className="topbar-spacer" />
    </header>
  );
}
