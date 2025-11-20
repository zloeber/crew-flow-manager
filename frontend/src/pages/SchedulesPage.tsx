import { useEffect, useState } from 'react'
import { Plus, Edit, Trash2, ToggleLeft, ToggleRight } from 'lucide-react'
import { schedulesApi, flowsApi } from '../services/api'
import { Schedule, Flow } from '../types'

function SchedulesPage() {
  const [schedules, setSchedules] = useState<Schedule[]>([])
  const [flows, setFlows] = useState<Flow[]>([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [editingSchedule, setEditingSchedule] = useState<Schedule | null>(null)
  const [formData, setFormData] = useState({
    flow_id: 0,
    name: '',
    cron_expression: '0 0 * * *',
    model_override: '',
    llm_provider: '',
    llm_base_url: '',
    inputs: '{}',
    is_active: true,
  })

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    await Promise.all([loadSchedules(), loadFlows()])
    setLoading(false)
  }

  const loadSchedules = async () => {
    try {
      const response = await schedulesApi.getAll()
      setSchedules(response.data)
    } catch (error) {
      console.error('Error loading schedules:', error)
    }
  }

  const loadFlows = async () => {
    try {
      const response = await flowsApi.getAll()
      setFlows(response.data.filter((f: Flow) => f.is_valid))
    } catch (error) {
      console.error('Error loading flows:', error)
    }
  }

  const handleCreate = async () => {
    try {
      const data = {
        ...formData,
        inputs: formData.inputs ? JSON.parse(formData.inputs) : null,
        model_override: formData.model_override || null,
        llm_provider: formData.llm_provider || null,
        llm_base_url: formData.llm_base_url || null,
      }
      await schedulesApi.create(data)
      setShowModal(false)
      resetForm()
      loadSchedules()
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Error creating schedule')
    }
  }

  const handleUpdate = async () => {
    if (!editingSchedule) return
    try {
      const data = {
        ...formData,
        inputs: formData.inputs ? JSON.parse(formData.inputs) : null,
        model_override: formData.model_override || null,
        llm_provider: formData.llm_provider || null,
        llm_base_url: formData.llm_base_url || null,
      }
      await schedulesApi.update(editingSchedule.id, data)
      setShowModal(false)
      setEditingSchedule(null)
      resetForm()
      loadSchedules()
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Error updating schedule')
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this schedule?')) return
    try {
      await schedulesApi.delete(id)
      loadSchedules()
    } catch (error) {
      alert('Error deleting schedule')
    }
  }

  const handleToggleActive = async (schedule: Schedule) => {
    try {
      await schedulesApi.update(schedule.id, { is_active: !schedule.is_active })
      loadSchedules()
    } catch (error) {
      alert('Error toggling schedule')
    }
  }

  const openCreateModal = () => {
    resetForm()
    setEditingSchedule(null)
    setShowModal(true)
  }

  const openEditModal = (schedule: Schedule) => {
    setFormData({
      flow_id: schedule.flow_id,
      name: schedule.name,
      cron_expression: schedule.cron_expression,
      model_override: schedule.model_override || '',
      llm_provider: schedule.llm_provider || '',
      llm_base_url: schedule.llm_base_url || '',
      inputs: schedule.inputs ? JSON.stringify(schedule.inputs, null, 2) : '{}',
      is_active: schedule.is_active,
    })
    setEditingSchedule(schedule)
    setShowModal(true)
  }

  const resetForm = () => {
    setFormData({
      flow_id: flows[0]?.id || 0,
      name: '',
      cron_expression: '0 0 * * *',
      model_override: '',
      llm_provider: '',
      llm_base_url: '',
      inputs: '{}',
      is_active: true,
    })
  }

  const getFlowName = (flowId: number) => {
    const flow = flows.find(f => f.id === flowId)
    return flow?.name || `Flow ${flowId}`
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
        <h1 className="text-3xl font-bold">Schedules</h1>
        <button onClick={openCreateModal} className="btn-primary flex items-center">
          <Plus className="w-5 h-5 mr-2" />
          New Schedule
        </button>
      </div>

      <div className="space-y-4">
        {schedules.map((schedule) => (
          <div key={schedule.id} className="card">
            <div className="flex justify-between items-start">
              <div className="flex-1">
                <div className="flex items-center mb-2">
                  <h3 className="text-lg font-semibold mr-3">{schedule.name}</h3>
                  {schedule.is_active ? (
                    <span className="px-3 py-1 rounded-full text-sm font-medium bg-green-900 text-green-300">
                      Active
                    </span>
                  ) : (
                    <span className="px-3 py-1 rounded-full text-sm font-medium bg-gray-900 text-gray-300">
                      Inactive
                    </span>
                  )}
                </div>
                <div className="text-sm text-gray-400 space-y-1">
                  <p>Flow: {getFlowName(schedule.flow_id)}</p>
                  <p>Cron: {schedule.cron_expression}</p>
                  {schedule.model_override && <p>Model: {schedule.model_override}</p>}
                  {schedule.last_run_at && (
                    <p>Last Run: {new Date(schedule.last_run_at).toLocaleString()}</p>
                  )}
                  {schedule.next_run_at && (
                    <p>Next Run: {new Date(schedule.next_run_at).toLocaleString()}</p>
                  )}
                </div>
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={() => handleToggleActive(schedule)}
                  className="btn-secondary p-2"
                  title={schedule.is_active ? 'Deactivate' : 'Activate'}
                >
                  {schedule.is_active ? (
                    <ToggleRight className="w-5 h-5" />
                  ) : (
                    <ToggleLeft className="w-5 h-5" />
                  )}
                </button>
                <button
                  onClick={() => openEditModal(schedule)}
                  className="btn-secondary p-2"
                  title="Edit"
                >
                  <Edit className="w-5 h-5" />
                </button>
                <button
                  onClick={() => handleDelete(schedule.id)}
                  className="btn-danger p-2"
                  title="Delete"
                >
                  <Trash2 className="w-5 h-5" />
                </button>
              </div>
            </div>
          </div>
        ))}

        {schedules.length === 0 && (
          <div className="card text-center text-gray-400">
            No schedules found. Create a schedule to automatically execute flows.
          </div>
        )}
      </div>

      {/* Create/Edit Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <h2 className="text-2xl font-bold mb-4">
              {editingSchedule ? 'Edit Schedule' : 'Create Schedule'}
            </h2>
            <div className="space-y-4">
              <div>
                <label className="label">Flow</label>
                <select
                  className="input"
                  value={formData.flow_id}
                  onChange={(e) => setFormData({ ...formData, flow_id: parseInt(e.target.value) })}
                >
                  <option value={0}>Select a flow</option>
                  {flows.map((flow) => (
                    <option key={flow.id} value={flow.id}>
                      {flow.name}
                    </option>
                  ))}
                </select>
              </div>
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
                <label className="label">Cron Expression</label>
                <input
                  type="text"
                  className="input"
                  value={formData.cron_expression}
                  onChange={(e) => setFormData({ ...formData, cron_expression: e.target.value })}
                  placeholder="0 0 * * *"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Format: minute hour day month day_of_week (e.g., "0 0 * * *" for daily at midnight)
                </p>
              </div>
              <div>
                <label className="label">Model Override (optional)</label>
                <input
                  type="text"
                  className="input"
                  value={formData.model_override}
                  onChange={(e) => setFormData({ ...formData, model_override: e.target.value })}
                  placeholder="gpt-4, llama2, etc."
                />
              </div>
              <div>
                <label className="label">LLM Provider (optional)</label>
                <select
                  className="input"
                  value={formData.llm_provider}
                  onChange={(e) => setFormData({ ...formData, llm_provider: e.target.value })}
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
                  value={formData.llm_base_url}
                  onChange={(e) => setFormData({ ...formData, llm_base_url: e.target.value })}
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
                  value={formData.inputs}
                  onChange={(e) => setFormData({ ...formData, inputs: e.target.value })}
                />
              </div>
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="is_active"
                  checked={formData.is_active}
                  onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                  className="mr-2"
                />
                <label htmlFor="is_active" className="text-sm text-gray-300">
                  Active
                </label>
              </div>
            </div>
            <div className="flex justify-end space-x-2 mt-6">
              <button
                onClick={() => {
                  setShowModal(false)
                  setEditingSchedule(null)
                }}
                className="btn-secondary"
              >
                Cancel
              </button>
              <button
                onClick={editingSchedule ? handleUpdate : handleCreate}
                className="btn-primary"
              >
                {editingSchedule ? 'Update' : 'Create'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default SchedulesPage
