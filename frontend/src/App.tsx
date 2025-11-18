import { BrowserRouter as Router, Routes, Route, Navigate, NavLink } from 'react-router-dom'
import Dashboard from './components/Dashboard/Dashboard'
import MapView from './pages/MapView'
import ThreatPanel from './components/ThreatPanel'
import SitrepPanel from './components/SitrepPanel'
import TrackingPanel from './components/TrackingPanel'
import { LayoutDashboard, Map, Shield, AlertTriangle, FileText, Radio } from 'lucide-react'

function App() {
  return (
    <Router>
      <div className="h-full flex flex-col">
        {/* Navigation */}
        <nav className="bg-tactical-surface border-b border-tactical-border">
          <div className="flex items-center justify-between px-6 py-3">
            {/* Logo */}
            <div className="flex items-center space-x-3">
              <Shield className="w-6 h-6 text-tactical-primary" />
              <span className="text-lg font-bold text-tactical-primary font-mono">
                TACTICAL AEGIS
              </span>
            </div>

            {/* Navigation Links */}
            <div className="flex items-center space-x-1">
              <NavLink
                to="/dashboard"
                className={({ isActive }) =>
                  `flex items-center space-x-2 px-4 py-2 rounded transition-colors ${
                    isActive
                      ? 'bg-tactical-primary text-black font-semibold'
                      : 'text-tactical-text hover:bg-tactical-hover'
                  }`
                }
              >
                <LayoutDashboard className="w-4 h-4" />
                <span className="text-sm font-mono">DASHBOARD</span>
              </NavLink>

              <NavLink
                to="/map"
                className={({ isActive }) =>
                  `flex items-center space-x-2 px-4 py-2 rounded transition-colors ${
                    isActive
                      ? 'bg-tactical-primary text-black font-semibold'
                      : 'text-tactical-text hover:bg-tactical-hover'
                  }`
                }
              >
                <Map className="w-4 h-4" />
                <span className="text-sm font-mono">MAP</span>
              </NavLink>

              <NavLink
                to="/threats"
                className={({ isActive }) =>
                  `flex items-center space-x-2 px-4 py-2 rounded transition-colors ${
                    isActive
                      ? 'bg-tactical-primary text-black font-semibold'
                      : 'text-tactical-text hover:bg-tactical-hover'
                  }`
                }
              >
                <AlertTriangle className="w-4 h-4" />
                <span className="text-sm font-mono">THREATS</span>
              </NavLink>

              <NavLink
                to="/sitrep"
                className={({ isActive }) =>
                  `flex items-center space-x-2 px-4 py-2 rounded transition-colors ${
                    isActive
                      ? 'bg-tactical-primary text-black font-semibold'
                      : 'text-tactical-text hover:bg-tactical-hover'
                  }`
                }
              >
                <FileText className="w-4 h-4" />
                <span className="text-sm font-mono">SITREP</span>
              </NavLink>

              <NavLink
                to="/tracking"
                className={({ isActive }) =>
                  `flex items-center space-x-2 px-4 py-2 rounded transition-colors ${
                    isActive
                      ? 'bg-tactical-primary text-black font-semibold'
                      : 'text-tactical-text hover:bg-tactical-hover'
                  }`
                }
              >
                <Radio className="w-4 h-4" />
                <span className="text-sm font-mono">TRACKING</span>
              </NavLink>
            </div>
          </div>
        </nav>

        {/* Routes */}
        <div className="flex-1 overflow-hidden">
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/map" element={<MapView />} />
            <Route path="/threats" element={<ThreatPanel />} />
            <Route path="/sitrep" element={<SitrepPanel />} />
            <Route path="/tracking" element={<TrackingPanel />} />
          </Routes>
        </div>
      </div>
    </Router>
  )
}

export default App
