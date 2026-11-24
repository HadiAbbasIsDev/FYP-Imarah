// Use: the shared navigation for desktop browsers and the installed mobile PWA.
// Copyright (c) 2026 Imarah.tech. All rights reserved.
import { useEffect, useState } from "react";
import {
  Activity,
  ArrowUpRight,
  Building2,
  ChevronDown,
  ChevronRight,
  FlaskConical,
  HardHat,
  LayoutDashboard,
  Map,
  Menu,
  PanelLeftClose,
  Route as RouteIcon,
  ScanLine,
  WifiOff,
} from "lucide-react";
import { NavLink, Route, Routes, useLocation, Link } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import {
  InspectionDetail,
  InspectionList,
  NewInspection,
} from "./pages/Inspections";
import ModelLab from "./pages/ModelLab";
import {
  Monitoring,
  Roadmap,
  SiteManagement,
  UrbanAnalysis,
} from "./pages/FutureModules";
import { EmptyState } from "./components/UI";

const links = [
  { to: "/", label: "Overview", icon: LayoutDashboard },
  { to: "/inspections", label: "Inspections", icon: ScanLine },
  { to: "/models", label: "Model lab", icon: FlaskConical },
  { to: "/site", label: "Site management", icon: HardHat, preview: true },
  {
    to: "/monitoring",
    label: "Building monitoring",
    icon: Activity,
    preview: true,
  },
  { to: "/urban", label: "Urban analysis", icon: Map, preview: true },
];

export default function App() {
  const location = useLocation();
  const [menuOpen, setMenuOpen] = useState(false);
  const [offline, setOffline] = useState(!navigator.onLine);
  const [installEvent, setInstallEvent] = useState<
    (Event & { prompt: () => Promise<void> }) | null
  >(null);
  useEffect(() => {
    setMenuOpen(false);
    window.scrollTo(0, 0);
  }, [location.pathname]);
  useEffect(() => {
    const update = () => setOffline(!navigator.onLine);
    const install = (event: Event) => {
      event.preventDefault();
      setInstallEvent(event as Event & { prompt: () => Promise<void> });
    };
    window.addEventListener("online", update);
    window.addEventListener("offline", update);
    window.addEventListener("beforeinstallprompt", install);
    return () => {
      window.removeEventListener("online", update);
      window.removeEventListener("offline", update);
      window.removeEventListener("beforeinstallprompt", install);
    };
  }, []);
  const current =
    links.find((link) =>
      link.to === "/"
        ? location.pathname === "/"
        : location.pathname.startsWith(link.to),
    )?.label || "Project roadmap";
  return (
    <div className="app-shell">
      {menuOpen && (
        <button
          className="sidebar-backdrop"
          onClick={() => setMenuOpen(false)}
          aria-label="Close navigation"
        />
      )}
      <aside className={`sidebar ${menuOpen ? "open" : ""}`}>
        <Link className="brand" to="/">
          <img src="/icon.svg" alt="" />
          <span>
            imarah<span className="brand-dot">.</span>
            <small>BUILDING INTELLIGENCE</small>
          </span>
        </Link>
        <button
          className="icon-button mobile-close"
          onClick={() => setMenuOpen(false)}
          aria-label="Close menu"
        >
          <PanelLeftClose size={20} />
        </button>
        <div className="workspace">
          <span className="workspace-icon">
            <Building2 size={18} />
          </span>
          <div>
            FYP workspace<small>FAST · Karachi</small>
          </div>
          <ChevronDown size={15} />
        </div>
        <div className="nav-label">WORKSPACE</div>
        <nav aria-label="Main navigation">
          {links.map((link, i) => (
            <div key={link.to}>
              {i === 3 && (
                <div className="nav-label secondary-label">
                  THE BIGGER PICTURE
                </div>
              )}
              <NavLink
                end={link.to === "/"}
                to={link.to}
                className={({ isActive }) =>
                  `nav-item ${isActive ? "active" : ""}`
                }
              >
                <link.icon size={19} />
                <span>{link.label}</span>
                {link.preview && (
                  <span className="preview-dot" title="Concept preview" />
                )}
              </NavLink>
            </div>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <div className="phase-card">
            <span className="phase-dot" /> PHASE 01{" "}
            <h3>A strong foundation.</h3>
            <p>
              September 2026
              <br />
              From proposal to prototype.
            </p>
            <Link to="/roadmap">
              Explore our roadmap <ArrowUpRight size={16} />
            </Link>
          </div>
          <NavLink
            to="/roadmap"
            className={({ isActive }) => `nav-item ${isActive ? "active" : ""}`}
          >
            <RouteIcon size={19} />
            Project roadmap
          </NavLink>
          <div className="team-profile">
            <span className="avatar">IT</span>
            <div>
              Imarah team<small>Student research workspace</small>
            </div>
          </div>
        </div>
      </aside>
      <div className="main-shell">
        <header className="topbar">
          <div className="breadcrumb">
            <button
              className="icon-button mobile-menu"
              onClick={() => setMenuOpen(true)}
              aria-label="Open navigation"
            >
              <Menu size={21} />
            </button>
            <span>Workspace</span>
            <ChevronRight size={14} />
            <strong>{current}</strong>
          </div>
          <div className="topbar-right">
            {installEvent && (
              <button
                className="install-button"
                onClick={() => {
                  void installEvent.prompt();
                  setInstallEvent(null);
                }}
              >
                Install app <ArrowUpRight size={14} />
              </button>
            )}
            <span className="prototype-label">
              <i /> Phase 1 prototype
            </span>
            <span className="topbar-divider" />
            <span className="avatar small">IT</span>
          </div>
        </header>
        {offline && (
          <div className="offline-banner" role="status">
            <WifiOff size={17} />
            You’re offline. The app shell is available; inspections and model
            runs need the local server.
          </div>
        )}
        <main id="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/inspections" element={<InspectionList />} />
            <Route path="/inspections/new" element={<NewInspection />} />
            <Route path="/inspections/:id" element={<InspectionDetail />} />
            <Route path="/models" element={<ModelLab />} />
            <Route path="/site" element={<SiteManagement />} />
            <Route path="/monitoring" element={<Monitoring />} />
            <Route path="/urban" element={<UrbanAnalysis />} />
            <Route path="/roadmap" element={<Roadmap />} />
            <Route
              path="*"
              element={
                <EmptyState
                  title="This page hasn’t been built."
                  description="Head back to your workspace to continue."
                  action={
                    <Link className="button primary" to="/">
                      Go to overview
                    </Link>
                  }
                />
              }
            />
          </Routes>
        </main>
        <footer className="footer">
          <span>Thoughtfully built for safer spaces.</span>
          <span>© 2026 Imarah.tech · All rights reserved.</span>
        </footer>
      </div>
    </div>
  );
}
