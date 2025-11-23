import { useEffect, useState } from 'react'
import { Activity, CheckCircle, Clock } from 'lucide-react'
import { flowsApi, executionsApi, schedulesApi } from '../services/api'

function HomePage() {
  const [stats, setStats] = useState({
    totalFlows: 0,
    validFlows: 0,
    totalExecutions: 0,
    successfulExecutions: 0,
    activeSchedules: 0,
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadStats()
  }, [])

  const loadStats = async () => {
    try {
      const [flowsRes, executionsRes, schedulesRes] = await Promise.all([
        flowsApi.getAll(),
        executionsApi.getAll(),
        schedulesApi.getAll(),
      ])

      const flows = flowsRes.data
      const executions = executionsRes.data
      const schedules = schedulesRes.data

      setStats({
        totalFlows: flows.length,
        validFlows: flows.filter((f: any) => f.is_valid).length,
        totalExecutions: executions.length,
        successfulExecutions: executions.filter((e: any) => e.status === 'success').length,
        activeSchedules: schedules.filter((s: any) => s.is_active).length,
      })
    } catch (error) {
      console.error('Error loading stats:', error)
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
      <h1 className="text-3xl font-bold mb-8">Dashboard</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Total Flows</p>
              <p className="text-3xl font-bold">{stats.totalFlows}</p>
              <p className="text-sm text-gray-500 mt-1">
                {stats.validFlows} valid
              </p>
            </div>
            <Activity className="w-12 h-12 text-blue-500" />
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Total Executions</p>
              <p className="text-3xl font-bold">{stats.totalExecutions}</p>
              <p className="text-sm text-gray-500 mt-1">
                {stats.successfulExecutions} successful
              </p>
            </div>
            <CheckCircle className="w-12 h-12 text-green-500" />
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Active Schedules</p>
              <p className="text-3xl font-bold">{stats.activeSchedules}</p>
            </div>
            <Clock className="w-12 h-12 text-purple-500" />
          </div>
        </div>
      </div>

      <div className="card">
        <h2 className="text-xl font-bold mb-4">About CrewAI Flow Manager</h2>
        <p className="text-gray-300 mb-4">
          CrewAI Flow Manager is a comprehensive platform for managing, executing, and monitoring CrewAI Flows.
        </p>
        <div className="space-y-2 text-sm text-gray-400">
          <div className="flex items-center">
            <CheckCircle className="w-4 h-4 mr-2 text-green-500" />
            Create and edit Flow YAML with Monaco editor
          </div>
          <div className="flex items-center">
            <CheckCircle className="w-4 h-4 mr-2 text-green-500" />
            Real-time flow validation
          </div>
          <div className="flex items-center">
            <CheckCircle className="w-4 h-4 mr-2 text-green-500" />
            On-demand and scheduled execution
          </div>
          <div className="flex items-center">
            <CheckCircle className="w-4 h-4 mr-2 text-green-500" />
            Per-run model override support
          </div>
          <div className="flex items-center">
            <CheckCircle className="w-4 h-4 mr-2 text-green-500" />
            Real-time monitoring via WebSockets
          </div>
          <div className="flex items-center">
            <CheckCircle className="w-4 h-4 mr-2 text-green-500" />
            MCP server tools discovery
          </div>
        </div>
      </div>
    </div>
  )
}

export default HomePage
