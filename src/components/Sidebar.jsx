import {
  LayoutDashboard,
  ScanSearch,
  Database,
  ShieldCheck,
  BarChart3,
  Settings,
  CircleHelp,
} from "lucide-react";

import { NavLink } from "react-router-dom";

const menuItems = [
  {
    label: "Dashboard",
    icon: LayoutDashboard,
    path: "/",
  },
  {
    label: "Scan Data",
    icon: ScanSearch,
    path: "/scan",
  },
  {
    label: "Fragments",
    icon: Database,
    path: "/fragments",
  },
  {
    label: "Evidence",
    icon: ShieldCheck,
    path: "/evidence",
  },
  {
    label: "Analytics",
    icon: BarChart3,
    path: "/analytics",
  },
];

function Sidebar() {
  return (
    <aside className="sidebar">

      {/* BRAND */}
      <div className="brand">
        <div className="brand-mark">
          R
        </div>

        <div>
          <h1>
            ReFrag<span> AI</span>
          </h1>

          <p>
            DATA RECOVERY
          </p>
        </div>
      </div>


      {/* NAVIGATION */}
      <nav className="sidebar-nav">

        <p className="nav-label">
          WORKSPACE
        </p>

        {menuItems.map((item) => {
          const Icon = item.icon;

          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `nav-item ${isActive ? "active" : ""}`
              }
            >
              <Icon size={19} />

              <span>
                {item.label}
              </span>
            </NavLink>
          );
        })}


        <div className="nav-divider" />


        <p className="nav-label">
          SYSTEM
        </p>

        <button className="nav-item">
          <Settings size={19} />

          <span>
            Settings
          </span>
        </button>

        <button className="nav-item">
          <CircleHelp size={19} />

          <span>
            Documentation
          </span>
        </button>

      </nav>


      {/* STATUS */}
      <div className="system-status">

        <div className="status-dot" />

        <div>
          <strong>
            System Online
          </strong>

          <span>
            Local forensic engine
          </span>
        </div>

      </div>

    </aside>
  );
}

export default Sidebar;