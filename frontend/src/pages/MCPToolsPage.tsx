import { useEffect, useState } from 'react'
import { RefreshCw, Search } from 'lucide-react'
import { mcpToolsApi } from '../services/api'
import { MCPTool } from '../types'

function MCPToolsPage() {
  const [tools, setTools] = useState<MCPTool[]>([])
  const [filteredTools, setFilteredTools] = useState<MCPTool[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')

  useEffect(() => {
    loadTools()
  }, [])

  useEffect(() => {
    if (searchTerm) {
      setFilteredTools(
        tools.filter(
          (tool) =>
            tool.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
            tool.description.toLowerCase().includes(searchTerm.toLowerCase())
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
        <h1 className="text-3xl font-bold">MCP Tools</h1>
        <button onClick={loadTools} className="btn-secondary flex items-center">
          <RefreshCw className="w-5 h-5 mr-2" />
          Refresh
        </button>
      </div>

      <div className="mb-6">
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
            <h3 className="text-lg font-semibold mb-2">{tool.name}</h3>
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
          {searchTerm ? 'No tools found matching your search.' : 'No MCP tools available.'}
        </div>
      )}
    </div>
  )
}

export default MCPToolsPage
