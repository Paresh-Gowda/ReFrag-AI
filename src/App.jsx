import { BrowserRouter, Routes, Route } from "react-router-dom";

import Sidebar from "./components/Sidebar";
import Topbar from "./components/Topbar";

import Dashboard from "./pages/Dashboard";
import ScanData from "./pages/ScanData";
import Fragments from "./pages/Fragments";
import Evidence from "./pages/Evidence";
import Analytics from "./pages/Analytics";

import "./App.css";

function App() {
  return (
    <BrowserRouter>
      <div className="app-shell">
        <Sidebar />

        <main className="main-content">
          <Topbar />

          <Routes>
            <Route path="/" element={<Dashboard />} />

            <Route path="/scan" element={<ScanData />} />

            <Route path="/fragments" element={<Fragments />} />

            <Route path="/evidence" element={<Evidence />} />

            <Route path="/analytics" element={<Analytics />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
export default App;
