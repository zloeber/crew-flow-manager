import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: `${API_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Flows
export const flowsApi = {
  getAll: () => api.get('/flows'),
  getById: (id: number) => api.get(`/flows/${id}`),
  create: (data: any) => api.post('/flows', data),
  update: (id: number, data: any) => api.put(`/flows/${id}`, data),
  delete: (id: number) => api.delete(`/flows/${id}`),
  validate: (yaml_content: string) => api.post('/flows/validate', yaml_content, {
    headers: { 'Content-Type': 'text/plain' }
  }),
}

// Executions
export const executionsApi = {
  getAll: (flowId?: number) => api.get('/executions', { params: { flow_id: flowId } }),
  getById: (id: number) => api.get(`/executions/${id}`),
  create: (data: any) => api.post('/executions', data),
  delete: (id: number) => api.delete(`/executions/${id}`),
}

// Schedules
export const schedulesApi = {
  getAll: (flowId?: number) => api.get('/schedules', { params: { flow_id: flowId } }),
  getById: (id: number) => api.get(`/schedules/${id}`),
  create: (data: any) => api.post('/schedules', data),
  update: (id: number, data: any) => api.put(`/schedules/${id}`, data),
  delete: (id: number) => api.delete(`/schedules/${id}`),
}

// MCP Tools
export const mcpToolsApi = {
  getAll: () => api.get('/mcp-tools'),
}
