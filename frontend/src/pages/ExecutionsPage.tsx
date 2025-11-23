import { useEffect, useState } from 'react'
import { RefreshCw, Eye, Trash2 } from 'lucide-react'
import { executionsApi, flowsApi } from '../services/api'
import { Execution, Flow } from '../types'
import { wsService } from '../services/websocket'

function ExecutionsPage() {
  const [executions, setExecutions] = useState<Execution[]>([])
  const [flows, setFlows] = useState<Flow[]>([])
  const [loading, setLoading] = useState(true)
  const [viewingExecution, setViewingExecution] = useState<Execution | null>(null)

  useEffect(() => {
    loadData()
    
    // Connect to WebSocket for real-time updates
    wsService.connect()
    const unsubscribe = wsService.subscribe('execution_update', (data) => {
      console.log('Execution update:', data)
      loadExecutions()
    })

    return () => {
      unsubscribe()
    }
  }, [])

  const loadData = async () => {
    await Promise.all([loadExecutions(), loadFlows()])
    setLoading(false)
  }

  const loadExecutions = async () => {
    try {
      const response = await executionsApi.getAll()
      setExecutions(response.data)
    } catch (error) {
      console.error('Error loading executions:', error)
    }
  }

  const loadFlows = async () => {
    try {
      const response = await flowsApi.getAll()
      setFlows(response.data)
    } catch (error) {
      console.error('Error loading flows:', error)
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this execution?')) return
    try {
      await executionsApi.delete(id)
      loadExecutions()
    } catch (error) {
      alert('Error deleting execution')
    }
  }

  const getFlowName = (flowId: number) => {
    const flow = flows.find(f => f.id === flowId)
    return flow?.name || `Flow ${flowId}`
  }

  const getStatusBadge = (status: string) => {
    const baseClass = 'px-3 py-1 rounded-full text-sm font-medium'
    switch (status) {
      case 'success': return `${baseClass} bg-green-900 text-green-300`
      case 'failed': return `${baseClass} bg-red-900 text-red-300`
      case 'running': return `${baseClass} bg-blue-900 text-blue-300`
      case 'pending': return `${baseClass} bg-yellow-900 text-yellow-300`
      default: return `${baseClass} bg-gray-900 text-gray-300`
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
        <h1 className="text-3xl font-bold">Executions</h1>
        <button onClick={loadExecutions} className="btn-secondary flex items-center">
          <RefreshCw className="w-5 h-5 mr-2" />
          Refresh
        </button>
      </div>

      <div className="space-y-4">
        {executions.map((execution) => (
          <div key={execution.id} className="card">
            <div className="flex justify-between items-start">
              <div className="flex-1">
                <div className="flex items-center mb-2">
                  <h3 className="text-lg font-semibold mr-3">
                    {getFlowName(execution.flow_id)}
                  </h3>
                  <span className={getStatusBadge(execution.status)}>
                    {execution.status}
                  </span>
                </div>
                <div className="text-sm text-gray-400 space-y-1">
                  <p>Execution ID: {execution.id}</p>
                  {execution.model_override && (
                    <p>Model: {execution.model_override}</p>
                  )}
                  <p>Created: {new Date(execution.created_at).toLocaleString()}</p>
                  {execution.started_at && (
                    <p>Started: {new Date(execution.started_at).toLocaleString()}</p>
                  )}
                  {execution.completed_at && (
                    <p>Completed: {new Date(execution.completed_at).toLocaleString()}</p>
                  )}
                  {execution.error_message && (
                    <p className="text-red-400">Error: {execution.error_message}</p>
                  )}
                </div>
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={() => setViewingExecution(execution)}
                  className="btn-secondary p-2"
                  title="View Details"
                >
                  <Eye className="w-5 h-5" />
                </button>
                <button
                  onClick={() => handleDelete(execution.id)}
                  className="btn-danger p-2"
                  title="Delete"
                >
                  <Trash2 className="w-5 h-5" />
                </button>
              </div>
            </div>
          </div>
        ))}

        {executions.length === 0 && (
          <div className="card text-center text-gray-400">
            No executions found. Execute a flow to see results here.
          </div>
        )}
      </div>

      {/* View Details Modal */}
      {viewingExecution && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
            <h2 className="text-2xl font-bold mb-4">
              Execution Details: {viewingExecution.id}
            </h2>
            <div className="space-y-4">
              <div>
                <p className="text-gray-400">Flow:</p>
                <p className="text-white">{getFlowName(viewingExecution.flow_id)}</p>
              </div>
              <div>
                <p className="text-gray-400">Status:</p>
                <span className={getStatusBadge(viewingExecution.status)}>
                  {viewingExecution.status}
                </span>
              </div>
              {viewingExecution.inputs && (
                <div>
                  <p className="text-gray-400 mb-2">Inputs:</p>
                  <pre className="bg-gray-900 p-4 rounded-lg text-sm overflow-x-auto">
                    {JSON.stringify(viewingExecution.inputs, null, 2)}
                  </pre>
                </div>
              )}
              {viewingExecution.outputs && (
                <div>
                  <p className="text-gray-400 mb-2">Outputs:</p>
                  <pre className="bg-gray-900 p-4 rounded-lg text-sm overflow-x-auto">
                    {JSON.stringify(viewingExecution.outputs, null, 2)}
                  </pre>
                </div>
              )}
              {viewingExecution.logs && (
                <div>
                  <p className="text-gray-400 mb-2">Logs:</p>
                  <pre className="bg-gray-900 p-4 rounded-lg text-sm overflow-x-auto whitespace-pre-wrap">
                    {viewingExecution.logs}
                  </pre>
                </div>
              )}
              {viewingExecution.error_message && (
                <div>
                  <p className="text-gray-400 mb-2">Error:</p>
                  <pre className="bg-red-900 p-4 rounded-lg text-sm overflow-x-auto text-red-300">
                    {viewingExecution.error_message}
                  </pre>
                </div>
              )}
            </div>
            <div className="flex justify-end mt-6">
              <button onClick={() => setViewingExecution(null)} className="btn-secondary">
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default ExecutionsPage
