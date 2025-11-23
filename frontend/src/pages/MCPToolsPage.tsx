import { useEffect, useState, useRef } from 'react'
import { RefreshCw, Search, Plus, Edit, Trash2, Upload, Download, Server } from 'lucide-react'
import { mcpToolsApi, mcpServersApi } from '../services/api'
import { MCPTool, MCPServer } from '../types'

function MCPToolsPage() {
  const [tools, setTools] = useState<MCPTool[]>([])
  const [servers, setServers] = useState<MCPServer[]>([])
  const [filteredTools, setFilteredTools] = useState<MCPTool[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [showServerModal, setShowServerModal] = useState(false)
  const [editingServer, setEditingServer] = useState<MCPServer | null>(null)
  const [showImportModal, setShowImportModal] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [serverFormData, setServerFormData] = useState({
    name: '',
    command: '',
    args: '[]',
    env: '{}',
    type: 'stdio',
    url: '',
    is_active: true,
  })

  useEffect(() => {
    loadTools()
    loadServers()
  }, [])

  useEffect(() => {
    if (searchTerm) {
      setFilteredTools(
        tools.filter(
          (tool) =>
            tool.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
            tool.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
            tool.server.toLowerCase().includes(searchTerm.toLowerCase())
        )
      )
    } else {
      setFilteredTools(tools)
    }
  }, [searchTerm, tools])

  const loadTools = async () => {
    try {
      const response = await mcpToolsApi.getAll()
      setTools(response.data.tools)
      setFilteredTools(response.data.tools)
    } catch (error) {
      console.error('Error loading MCP tools:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadServers = async () => {
    try {
      const response = await mcpServersApi.getAll()
      setServers(response.data)
    } catch (error) {
      console.error('Error loading MCP servers:', error)
    }
  }

  const handleCreateServer = async () => {
    try {
      const data = {
        ...serverFormData,
        args: serverFormData.args ? JSON.parse(serverFormData.args) : [],
        env: serverFormData.env ? JSON.parse(serverFormData.env) : {},
      }
      await mcpServersApi.create(data)
      setShowServerModal(false)
      resetServerForm()
      loadServers()
      loadTools()
      alert('MCP Server created successfully')
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Error creating MCP server')
    }
  }

  const handleUpdateServer = async () => {
    if (!editingServer) return
    try {
      const data = {
        ...serverFormData,
        args: serverFormData.args ? JSON.parse(serverFormData.args) : [],
        env: serverFormData.env ? JSON.parse(serverFormData.env) : {},
      }
      await mcpServersApi.update(editingServer.id, data)
      setShowServerModal(false)
      setEditingServer(null)
      resetServerForm()
      loadServers()
      loadTools()
      alert('MCP Server updated successfully')
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Error updating MCP server')
    }
  }

  const handleDeleteServer = async (id: number) => {
    if (!confirm('Are you sure you want to delete this MCP server?')) return
    try {
      await mcpServersApi.delete(id)
      loadServers()
      loadTools()
    } catch (error) {
      alert('Error deleting MCP server')
    }
  }

  const openCreateServerModal = () => {
    resetServerForm()
    setEditingServer(null)
    setShowServerModal(true)
  }

  const openEditServerModal = (server: MCPServer) => {
    setServerFormData({
      name: server.name,
      command: server.command,
      args: JSON.stringify(server.args || [], null, 2),
      env: JSON.stringify(server.env || {}, null, 2),
      type: server.type,
      url: server.url || '',
      is_active: server.is_active,
    })
    setEditingServer(server)
    setShowServerModal(true)
  }

  const resetServerForm = () => {
    setServerFormData({
      name: '',
      command: '',
      args: '[]',
      env: '{}',
      type: 'stdio',
      url: '',
      is_active: true,
    })
  }

  const handleImportServers = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    try {
      const result = await mcpServersApi.import(file)
      alert(`Imported ${result.data.total_created} server(s) successfully`)
      loadServers()
      loadTools()
      setShowImportModal(false)
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Error importing MCP servers')
    }
    
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const handleExportServers = async () => {
    try {
      const response = await mcpServersApi.export()
      const blob = new Blob([response.data], { type: 'application/json' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'mcp_servers.json'
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (error) {
      alert('Error exporting MCP servers')
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    )
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">MCP Tools & Servers</h1>
        <div className="flex space-x-2">
          <button onClick={handleExportServers} className="btn-secondary flex items-center">
            <Download className="w-5 h-5 mr-2" />
            Export Servers
          </button>
          <button onClick={() => setShowImportModal(true)} className="btn-secondary flex items-center">
            <Upload className="w-5 h-5 mr-2" />
            Import Servers
          </button>
          <button onClick={openCreateServerModal} className="btn-primary flex items-center">
            <Plus className="w-5 h-5 mr-2" />
            Add Server
          </button>
          <button onClick={() => { loadTools(); loadServers(); }} className="btn-secondary flex items-center">
            <RefreshCw className="w-5 h-5 mr-2" />
            Refresh
          </button>
        </div>
      </div>

      {/* MCP Servers Section */}
      <div className="mb-8">
        <h2 className="text-2xl font-semibold mb-4">MCP Servers</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {servers.map((server) => (
            <div key={server.id} className="card">
              <div className="flex justify-between items-start mb-3">
                <div className="flex items-center">
                  <Server className="w-5 h-5 mr-2 text-blue-400" />
                  <h3 className="text-lg font-semibold">{server.name}</h3>
                </div>
                <div className="flex space-x-2">
                  <button
                    onClick={() => openEditServerModal(server)}
                    className="btn-secondary p-1"
                    title="Edit"
                  >
                    <Edit className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleDeleteServer(server.id)}
                    className="btn-danger p-1"
                    title="Delete"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
              <div className="text-sm space-y-1">
                <p className="text-gray-400">
                  <span className="font-semibold">Command:</span> {server.command}
                </p>
                <p className="text-gray-400">
                  <span className="font-semibold">Type:</span> {server.type}
                </p>
                <p className="text-gray-400">
                  <span className="font-semibold">Status:</span>{' '}
                  <span className={server.is_active ? 'text-green-400' : 'text-red-400'}>
                    {server.is_active ? 'Active' : 'Inactive'}
                  </span>
                </p>
              </div>
            </div>
          ))}
        </div>
        {servers.length === 0 && (
          <div className="card text-center text-gray-400">
            No MCP servers configured. Add a server to start using MCP tools.
          </div>
        )}
      </div>

      {/* Search Section */}
      <div className="mb-6">
        <h2 className="text-2xl font-semibold mb-4">Available Tools</h2>
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search tools..."
            className="input pl-10"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filteredTools.map((tool, index) => (
          <div key={index} className="card">
            <div className="flex justify-between items-start mb-2">
              <h3 className="text-lg font-semibold">{tool.name}</h3>
              <span className="text-xs bg-blue-600 px-2 py-1 rounded">{tool.server}</span>
            </div>
            <p className="text-gray-400 mb-4">{tool.description}</p>
            {tool.parameters && Object.keys(tool.parameters).length > 0 && (
              <div>
                <p className="text-sm font-semibold text-gray-300 mb-2">Parameters:</p>
                <div className="space-y-2">
                  {Object.entries(tool.parameters).map(([key, value]: [string, any]) => (
                    <div key={key} className="text-sm">
                      <span className="font-mono text-blue-400">{key}</span>
                      <span className="text-gray-500 ml-2">
                        ({value.type})
                      </span>
                      {value.description && (
                        <p className="text-gray-400 ml-4 mt-1">{value.description}</p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {filteredTools.length === 0 && (
        <div className="card text-center text-gray-400">
          {searchTerm ? 'No tools found matching your search.' : 'No MCP tools available. Configure MCP servers to see available tools.'}
        </div>
      )}

      {/* Server Modal */}
      {showServerModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <h2 className="text-2xl font-bold mb-4">
              {editingServer ? 'Edit MCP Server' : 'Add MCP Server'}
            </h2>
            <div className="space-y-4">
              <div>
                <label className="label">Server Name</label>
                <input
                  type="text"
                  className="input"
                  value={serverFormData.name}
                  onChange={(e) => setServerFormData({ ...serverFormData, name: e.target.value })}
                  placeholder="sequential-thinking"
                />
              </div>
              <div>
                <label className="label">Command</label>
                <input
                  type="text"
                  className="input"
                  value={serverFormData.command}
                  onChange={(e) => setServerFormData({ ...serverFormData, command: e.target.value })}
                  placeholder="npx"
                />
              </div>
              <div>
                <label className="label">Arguments (JSON Array)</label>
                <textarea
                  className="input"
                  rows={3}
                  value={serverFormData.args}
                  onChange={(e) => setServerFormData({ ...serverFormData, args: e.target.value })}
                  placeholder='["-y", "@modelcontextprotocol/server-sequential-thinking"]'
                />
              </div>
              <div>
                <label className="label">Environment Variables (JSON Object)</label>
                <textarea
                  className="input"
                  rows={3}
                  value={serverFormData.env}
                  onChange={(e) => setServerFormData({ ...serverFormData, env: e.target.value })}
                  placeholder='{"API_KEY": "your-key"}'
                />
              </div>
              <div>
                <label className="label">Type</label>
                <select
                  className="input"
                  value={serverFormData.type}
                  onChange={(e) => setServerFormData({ ...serverFormData, type: e.target.value })}
                >
                  <option value="stdio">stdio</option>
                  <option value="http">http</option>
                </select>
              </div>
              {serverFormData.type === 'http' && (
                <div>
                  <label className="label">URL</label>
                  <input
                    type="text"
                    className="input"
                    value={serverFormData.url}
                    onChange={(e) => setServerFormData({ ...serverFormData, url: e.target.value })}
                    placeholder="http://localhost:8080/mcp"
                  />
                </div>
              )}
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="is_active"
                  checked={serverFormData.is_active}
                  onChange={(e) => setServerFormData({ ...serverFormData, is_active: e.target.checked })}
                  className="mr-2"
                />
                <label htmlFor="is_active" className="text-gray-300">Active</label>
              </div>
            </div>
            <div className="flex justify-end space-x-2 mt-6">
              <button
                onClick={() => {
                  setShowServerModal(false)
                  setEditingServer(null)
                }}
                className="btn-secondary"
              >
                Cancel
              </button>
              <button
                onClick={editingServer ? handleUpdateServer : handleCreateServer}
                className="btn-primary"
              >
                {editingServer ? 'Update' : 'Create'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Import Modal */}
      {showImportModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg p-6 w-full max-w-md">
            <h2 className="text-2xl font-bold mb-4">Import MCP Servers</h2>
            <p className="text-gray-400 mb-4">
              Upload an MCP configuration JSON file (mcp.json format)
            </p>
            <input
              ref={fileInputRef}
              type="file"
              accept=".json"
              onChange={handleImportServers}
              className="input mb-4"
            />
            <div className="flex justify-end">
              <button
                onClick={() => setShowImportModal(false)}
                className="btn-secondary"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default MCPToolsPage
