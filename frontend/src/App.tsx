import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import { Home, FileCode, Play, Calendar, Wrench } from 'lucide-react'
import FlowsPage from './pages/FlowsPage'
import ExecutionsPage from './pages/ExecutionsPage'
import SchedulesPage from './pages/SchedulesPage'
import MCPToolsPage from './pages/MCPToolsPage'
import HomePage from './pages/HomePage'

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-900 text-white">
        {/* Navigation */}
        <nav className="bg-gray-800 border-b border-gray-700">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16">
              <div className="flex items-center">
                <h1 className="text-xl font-bold">CrewAI Flow Manager</h1>
              </div>
              <div className="flex space-x-4">
                <Link to="/" className="flex items-center px-3 py-2 rounded-md hover:bg-gray-700">
                  <Home className="w-5 h-5 mr-2" />
                  Home
                </Link>
                <Link to="/flows" className="flex items-center px-3 py-2 rounded-md hover:bg-gray-700">
                  <FileCode className="w-5 h-5 mr-2" />
                  Flows
                </Link>
                <Link to="/executions" className="flex items-center px-3 py-2 rounded-md hover:bg-gray-700">
                  <Play className="w-5 h-5 mr-2" />
                  Executions
                </Link>
                <Link to="/schedules" className="flex items-center px-3 py-2 rounded-md hover:bg-gray-700">
                  <Calendar className="w-5 h-5 mr-2" />
                  Schedules
                </Link>
                <Link to="/mcp-tools" className="flex items-center px-3 py-2 rounded-md hover:bg-gray-700">
                  <Wrench className="w-5 h-5 mr-2" />
                  MCP Tools
                </Link>
              </div>
            </div>
          </div>
        </nav>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/flows" element={<FlowsPage />} />
            <Route path="/executions" element={<ExecutionsPage />} />
            <Route path="/schedules" element={<SchedulesPage />} />
            <Route path="/mcp-tools" element={<MCPToolsPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App
