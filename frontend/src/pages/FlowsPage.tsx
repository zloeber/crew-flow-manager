import { useEffect, useState } from 'react'
import { Plus, Edit, Trash2, Eye, Play, CheckCircle, XCircle } from 'lucide-react'
import Editor from '@monaco-editor/react'
import { flowsApi, executionsApi } from '../services/api'
import { Flow } from '../types'

function FlowsPage() {
  const [flows, setFlows] = useState<Flow[]>([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [showViewModal, setShowViewModal] = useState(false)
  const [editingFlow, setEditingFlow] = useState<Flow | null>(null)
  const [viewingFlow, setViewingFlow] = useState<Flow | null>(null)
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    yaml_content: 'name: My Flow\ndescription: A sample CrewAI flow\n',
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

  const handleExecute = async (flowId: number) => {
    try {
      await executionsApi.create({ flow_id: flowId })
      alert('Execution started successfully')
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Error starting execution')
    }
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
        <button onClick={openCreateModal} className="btn-primary flex items-center">
          <Plus className="w-5 h-5 mr-2" />
          New Flow
        </button>
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
                onClick={() => openEditModal(flow)}
                className="btn-secondary p-2"
                title="Edit"
              >
                <Edit className="w-5 h-5" />
              </button>
              <button
                onClick={() => handleExecute(flow.id)}
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
    </div>
  )
}

export default FlowsPage
