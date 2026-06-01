import { Route, Routes } from "react-router-dom";

import { Nav } from "./components/Nav";
import { Collection } from "./pages/Collection";
import { EventDetail } from "./pages/EventDetail";
import { Gallery } from "./pages/Gallery";
import { Organizer } from "./pages/Organizer";
import { WalletProvider } from "./wallet-context";

export default function App() {
  return (
    <WalletProvider>
      <Nav />
      <main className="container">
        <Routes>
          <Route path="/" element={<Gallery />} />
          <Route path="/collection" element={<Collection />} />
          <Route path="/organizer" element={<Organizer />} />
          <Route path="/event/:id" element={<EventDetail />} />
        </Routes>
      </main>
      <footer className="footer">POAP on Soroban · testnet POC</footer>
    </WalletProvider>
  );
}
