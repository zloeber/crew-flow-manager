import { useEffect, useState, useRef } from 'react'
import { Plus, Edit, Trash2, Eye, Play, CheckCircle, XCircle, Upload, Download, FileText, CheckSquare, Square } from 'lucide-react'
import Editor from '@monaco-editor/react'
import { flowsApi, executionsApi } from '../services/api'
import { Flow } from '../types'

interface FlowTask {
  index: number
  description: string
  agent: string
  expected_output: string
}

function FlowsPage() {
  const [flows, setFlows] = useState<Flow[]>([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [showViewModal, setShowViewModal] = useState(false)
  const [showExecuteModal, setShowExecuteModal] = useState(false)
  const [showImportModal, setShowImportModal] = useState(false)
  const [editingFlow, setEditingFlow] = useState<Flow | null>(null)
  const [viewingFlow, setViewingFlow] = useState<Flow | null>(null)
  const [executingFlow, setExecutingFlow] = useState<Flow | null>(null)
  const [availableTasks, setAvailableTasks] = useState<FlowTask[]>([])
  const [selectedTasks, setSelectedTasks] = useState<string[]>([])
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    yaml_content: 'name: My Flow\ndescription: A sample CrewAI flow\n',
  })
  const [executeFormData, setExecuteFormData] = useState({
    model_override: '',
    llm_provider: '',
    llm_base_url: '',
    inputs: '{}',
  })

  useEffect(() => {
    loadFlows()
  }, [])

  const loadFlows = async () => {
    try {
      const response = await flowsApi.getAll()
      setFlows(response.data)
    } catch (error) {
      console.error('Error loading flows:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = async () => {
    try {
      await flowsApi.create(formData)
      setShowModal(false)
      resetForm()
      loadFlows()
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Error creating flow')
    }
  }

  const handleUpdate = async () => {
    if (!editingFlow) return
    try {
      await flowsApi.update(editingFlow.id, formData)
      setShowModal(false)
      setEditingFlow(null)
      resetForm()
      loadFlows()
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Error updating flow')
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this flow?')) return
    try {
      await flowsApi.delete(id)
      loadFlows()
    } catch (error) {
      alert('Error deleting flow')
    }
  }

  const handleExecute = async () => {
    if (!executingFlow) return
    try {
      const data = {
        flow_id: executingFlow.id,
        model_override: executeFormData.model_override || null,
        llm_provider: executeFormData.llm_provider || null,
        llm_base_url: executeFormData.llm_base_url || null,
        inputs: executeFormData.inputs ? JSON.parse(executeFormData.inputs) : null,
        selected_tasks: selectedTasks.length > 0 ? selectedTasks : null,
      }
      await executionsApi.create(data)
      setShowExecuteModal(false)
      setExecutingFlow(null)
      resetExecuteForm()
      alert('Execution started successfully')
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Error starting execution')
    }
  }

  const openExecuteModal = async (flow: Flow) => {
    setExecutingFlow(flow)
    resetExecuteForm()
    setSelectedTasks([])
    
    // Load available tasks
    try {
      const response = await flowsApi.getTasks(flow.id)
      setAvailableTasks(response.data.tasks || [])
    } catch (error) {
      console.error('Error loading tasks:', error)
      setAvailableTasks([])
    }
    
    setShowExecuteModal(true)
  }

  const toggleTaskSelection = (taskDescription: string) => {
    setSelectedTasks(prev => 
      prev.includes(taskDescription)
        ? prev.filter(t => t !== taskDescription)
        : [...prev, taskDescription]
    )
  }

  const toggleAllTasks = () => {
    if (selectedTasks.length === availableTasks.length) {
      setSelectedTasks([])
    } else {
      setSelectedTasks(availableTasks.map(t => t.description))
    }
  }
    resetExecuteForm()
    setShowExecuteModal(true)
  }

  const resetExecuteForm = () => {
    setExecuteFormData({
      model_override: '',
      llm_provider: '',
      llm_base_url: '',
      inputs: '{}',
    })
  }

  const openCreateModal = () => {
    resetForm()
    setEditingFlow(null)
    setShowModal(true)
  }

  const openEditModal = (flow: Flow) => {
    setFormData({
      name: flow.name,
      description: flow.description || '',
      yaml_content: flow.yaml_content,
    })
    setEditingFlow(flow)
    setShowModal(true)
  }

  const openViewModal = (flow: Flow) => {
    setViewingFlow(flow)
    setShowViewModal(true)
  }

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      yaml_content: 'name: My Flow\ndescription: A sample CrewAI flow\n',
    })
  }

  const handleImportFile = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    try {
      await flowsApi.import(file)
      alert('Flow imported successfully')
      loadFlows()
      setShowImportModal(false)
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Error importing flow')
    }
    
    // Reset file input
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const handleExportFlow = async (flowId: number, flowName: string) => {
    try {
      const response = await flowsApi.export(flowId)
      const blob = new Blob([response.data], { type: 'application/x-yaml' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${flowName.replace(/\s+/g, '_')}.yaml`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (error) {
      alert('Error exporting flow')
    }
  }

  const openImportModal = () => {
    setShowImportModal(true)
  }

  const exampleFlows = [
    { name: 'simple_flow.yaml', path: '/examples/simple_flow.yaml' },
    { name: 'sample_flow.yaml', path: '/examples/sample_flow.yaml' },
    { name: 'ollama-flow-example.yaml', path: '/examples/ollama-flow-example.yaml' },
    { name: 'multi-agent-content-pipeline.yaml', path: '/examples/multi-agent-content-pipeline.yaml' },
    { name: 'multi-agent-software-dev.yaml', path: '/examples/multi-agent-software-dev.yaml' },
  ]

  const handleImportExample = async (examplePath: string) => {
    try {
      const response = await fetch(examplePath)
      if (!response.ok) throw new Error('Failed to fetch example')
      
      const blob = await response.blob()
      const file = new File([blob], examplePath.split('/').pop() || 'example.yaml', { type: 'application/x-yaml' })
      
      await flowsApi.import(file)
      alert('Example flow imported successfully')
      loadFlows()
      setShowImportModal(false)
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Error importing example flow')
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
        <h1 className="text-3xl font-bold">Flows</h1>
        <div className="flex space-x-2">
          <button onClick={openImportModal} className="btn-secondary flex items-center">
            <Upload className="w-5 h-5 mr-2" />
            Import
          </button>
          <button onClick={openCreateModal} className="btn-primary flex items-center">
            <Plus className="w-5 h-5 mr-2" />
            New Flow
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4">
        {flows.map((flow) => (
          <div key={flow.id} className="card flex justify-between items-start">
            <div className="flex-1">
              <div className="flex items-center mb-2">
                <h3 className="text-xl font-semibold">{flow.name}</h3>
                {flow.is_valid ? (
                  <CheckCircle className="w-5 h-5 text-green-500 ml-2" />
                ) : (
                  <XCircle className="w-5 h-5 text-red-500 ml-2" />
                )}
              </div>
              {flow.description && (
                <p className="text-gray-400 mb-2">{flow.description}</p>
              )}
              <p className="text-sm text-gray-500">
                Created: {new Date(flow.created_at).toLocaleString()}
              </p>
              {!flow.is_valid && flow.validation_errors && (
                <div className="mt-2 text-sm text-red-400">
                  Validation errors: {flow.validation_errors.errors.join(', ')}
                </div>
              )}
            </div>
            <div className="flex space-x-2">
              <button
                onClick={() => openViewModal(flow)}
                className="btn-secondary p-2"
                title="View"
              >
                <Eye className="w-5 h-5" />
              </button>
              <button
                onClick={() => handleExportFlow(flow.id, flow.name)}
                className="btn-secondary p-2"
                title="Export"
              >
                <Download className="w-5 h-5" />
              </button>
              <button
                onClick={() => openEditModal(flow)}
                className="btn-secondary p-2"
                title="Edit"
              >
                <Edit className="w-5 h-5" />
              </button>
              <button
                onClick={() => openExecuteModal(flow)}
                className="btn-success p-2"
                title="Execute"
                disabled={!flow.is_valid}
              >
                <Play className="w-5 h-5" />
              </button>
              <button
                onClick={() => handleDelete(flow.id)}
                className="btn-danger p-2"
                title="Delete"
              >
                <Trash2 className="w-5 h-5" />
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Create/Edit Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
            <h2 className="text-2xl font-bold mb-4">
              {editingFlow ? 'Edit Flow' : 'Create Flow'}
            </h2>
            <div className="space-y-4">
              <div>
                <label className="label">Name</label>
                <input
                  type="text"
                  className="input"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                />
              </div>
              <div>
                <label className="label">Description</label>
                <input
                  type="text"
                  className="input"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                />
              </div>
              <div>
                <label className="label">YAML Content</label>
                <div className="border border-gray-600 rounded-lg overflow-hidden">
                  <Editor
                    height="400px"
                    defaultLanguage="yaml"
                    theme="vs-dark"
                    value={formData.yaml_content}
                    onChange={(value) => setFormData({ ...formData, yaml_content: value || '' })}
                  />
                </div>
              </div>
            </div>
            <div className="flex justify-end space-x-2 mt-6">
              <button
                onClick={() => {
                  setShowModal(false)
                  setEditingFlow(null)
                }}
                className="btn-secondary"
              >
                Cancel
              </button>
              <button
                onClick={editingFlow ? handleUpdate : handleCreate}
                className="btn-primary"
              >
                {editingFlow ? 'Update' : 'Create'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* View Modal */}
      {showViewModal && viewingFlow && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
            <h2 className="text-2xl font-bold mb-4">View Flow: {viewingFlow.name}</h2>
            <div className="space-y-4">
              <div>
                <p className="text-gray-400">Description:</p>
                <p className="text-white">{viewingFlow.description || 'N/A'}</p>
              </div>
              <div>
                <p className="text-gray-400 mb-2">YAML Content:</p>
                <div className="border border-gray-600 rounded-lg overflow-hidden">
                  <Editor
                    height="400px"
                    defaultLanguage="yaml"
                    theme="vs-dark"
                    value={viewingFlow.yaml_content}
                    options={{ readOnly: true }}
                  />
                </div>
              </div>
            </div>
            <div className="flex justify-end mt-6">
              <button onClick={() => setShowViewModal(false)} className="btn-secondary">
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Execute Modal */}
      {showExecuteModal && executingFlow && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <h2 className="text-2xl font-bold mb-4">Execute Flow: {executingFlow.name}</h2>
            <div className="space-y-4">
              <div>
                <label className="label">Model Override (optional)</label>
                <input
                  type="text"
                  className="input"
                  value={executeFormData.model_override}
                  onChange={(e) => setExecuteFormData({ ...executeFormData, model_override: e.target.value })}
                  placeholder="gpt-4, llama2, etc."
                />
              </div>
              <div>
                <label className="label">LLM Provider (optional)</label>
                <select
                  className="input"
                  value={executeFormData.llm_provider}
                  onChange={(e) => setExecuteFormData({ ...executeFormData, llm_provider: e.target.value })}
                >
                  <option value="">Default (OpenAI)</option>
                  <option value="openai">OpenAI</option>
                  <option value="ollama">Ollama (Local)</option>
                  <option value="custom">Custom Endpoint</option>
                </select>
              </div>
              <div>
                <label className="label">LLM Base URL (optional)</label>
                <input
                  type="text"
                  className="input"
                  value={executeFormData.llm_base_url}
                  onChange={(e) => setExecuteFormData({ ...executeFormData, llm_base_url: e.target.value })}
                  placeholder="http://localhost:11434 for Ollama"
                />
                <p className="text-xs text-gray-500 mt-1">
                  For Ollama: http://localhost:11434, or custom OpenAI-compatible endpoint
                </p>
              </div>
              <div>
                <label className="label">Inputs (JSON, optional)</label>
                <textarea
                  className="input"
                  rows={4}
                  value={executeFormData.inputs}
                  onChange={(e) => setExecuteFormData({ ...executeFormData, inputs: e.target.value })}
                />
              </div>
              
              {/* Task Selection */}
              {availableTasks.length > 0 && (
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <label className="label">Select Tasks to Execute</label>
                    <button
                      onClick={toggleAllTasks}
                      className="text-sm text-blue-400 hover:text-blue-300"
                    >
                      {selectedTasks.length === availableTasks.length ? 'Deselect All' : 'Select All'}
                    </button>
                  </div>
                  <div className="space-y-2 max-h-60 overflow-y-auto border border-gray-700 rounded-lg p-3">
                    {availableTasks.map((task) => (
                      <div
                        key={task.index}
                        className="flex items-start space-x-3 p-2 hover:bg-gray-700 rounded cursor-pointer"
                        onClick={() => toggleTaskSelection(task.description)}
                      >
                        {selectedTasks.includes(task.description) ? (
                          <CheckSquare className="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" />
                        ) : (
                          <Square className="w-5 h-5 text-gray-500 flex-shrink-0 mt-0.5" />
                        )}
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-white truncate">{task.description}</p>
                          <p className="text-xs text-gray-400">Agent: {task.agent}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                  {selectedTasks.length === 0 && (
                    <p className="text-xs text-yellow-400 mt-2">
                      No tasks selected - all tasks will be executed
                    </p>
                  )}
                  {selectedTasks.length > 0 && (
                    <p className="text-xs text-green-400 mt-2">
                      {selectedTasks.length} of {availableTasks.length} task(s) selected
                    </p>
                  )}
                </div>
              )}
            </div>
            <div className="flex justify-end space-x-2 mt-6">
              <button
                onClick={() => {
                  setShowExecuteModal(false)
                  setExecutingFlow(null)
                  resetExecuteForm()
                }}
                className="btn-secondary"
              >
                Cancel
              </button>
              <button onClick={handleExecute} className="btn-success">
                Execute
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Import Modal */}
      {showImportModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <h2 className="text-2xl font-bold mb-4">Import Flow</h2>
            
            <div className="space-y-6">
              {/* File Upload Section */}
              <div>
                <h3 className="text-lg font-semibold mb-2">Import from File</h3>
                <p className="text-gray-400 text-sm mb-3">
                  Upload a YAML file to import a flow
                </p>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".yaml,.yml"
                  onChange={handleImportFile}
                  className="input"
                />
              </div>

              {/* Example Flows Section */}
              <div>
                <h3 className="text-lg font-semibold mb-2">Import Example Flows</h3>
                <p className="text-gray-400 text-sm mb-3">
                  Click on an example to import it
                </p>
                <div className="space-y-2">
                  {exampleFlows.map((example) => (
                    <button
                      key={example.path}
                      onClick={() => handleImportExample(example.path)}
                      className="w-full text-left px-4 py-3 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors flex items-center"
                    >
                      <FileText className="w-5 h-5 mr-3 text-blue-400" />
                      <span>{example.name}</span>
                    </button>
                  ))}
                </div>
              </div>
            </div>

            <div className="flex justify-end mt-6">
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

export default FlowsPage
