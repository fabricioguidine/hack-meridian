import { NavLink } from "react-router-dom";

import { ConnectButton } from "./ConnectButton";

export function Nav() {
  return (
    <header className="nav">
      <div className="nav__brand">
        ◈ POAP <span>on Soroban</span>
      </div>
      <nav className="nav__links">
        <NavLink to="/" end>
          Gallery
        </NavLink>
        <NavLink to="/collection">My Badges</NavLink>
        <NavLink to="/organizer">Organizer</NavLink>
      </nav>
      <ConnectButton />
    </header>
  );
}
