import {
  LayoutDashboard,
  ScanSearch,
  Database,
  ShieldCheck,
  BarChart3,
  Settings,
  CircleHelp,
} from "lucide-react";

const menuItems = [
  {
    label: "Dashboard",
    icon: LayoutDashboard,
    active: true,
  },
  {
    label: "Scan Data",
    icon: ScanSearch,
  },
  {
    label: "Fragments",
    icon: Database,
  },
  {
    label: "Evidence",
    icon: ShieldCheck,
  },
  {
    label: "Analytics",
    icon: BarChart3,
  },
];

function Sidebar() {
  return (
    <aside className="sidebar">

      <div className="brand">
        <div className="brand-mark">R</div>

        <div>
          <h1>ReFrag<span> AI</span></h1>
          <p>DATA RECOVERY</p>
        </div>
      </div>

      <nav className="sidebar-nav">

        <p className="nav-label">WORKSPACE</p>

        {menuItems.map((item) => {
          const Icon = item.icon;

          return (
            <button
              key={item.label}
              className={`nav-item ${item.active ? "active" : ""}`}
            >
              <Icon size={19} />
              <span>{item.label}</span>
            </button>
          );
        })}

        <div className="nav-divider" />

        <p className="nav-label">SYSTEM</p>

        <button className="nav-item">
          <Settings size={19} />
          <span>Settings</span>
        </button>

        <button className="nav-item">
          <CircleHelp size={19} />
          <span>Documentation</span>
        </button>

      </nav>

      <div className="system-status">
        <div className="status-dot" />

        <div>
          <strong>System Online</strong>
          <span>Local forensic engine</span>
        </div>
      </div>

    </aside>
  );
}

export default Sidebar;