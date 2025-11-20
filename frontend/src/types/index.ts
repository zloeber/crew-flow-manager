export interface Flow {
  id: number
  name: string
  description?: string
  yaml_content: string
  is_valid: boolean
  validation_errors?: { errors: string[] }
  created_at: string
  updated_at: string
}

export interface Execution {
  id: number
  flow_id: number
  status: 'pending' | 'running' | 'success' | 'failed' | 'cancelled'
  model_override?: string
  llm_provider?: string
  llm_base_url?: string
  inputs?: Record<string, any>
  outputs?: Record<string, any>
  error_message?: string
  logs?: string
  started_at?: string
  completed_at?: string
  created_at: string
}

export interface Schedule {
  id: number
  flow_id: number
  name: string
  cron_expression: string
  model_override?: string
  llm_provider?: string
  llm_base_url?: string
  inputs?: Record<string, any>
  is_active: boolean
  last_run_at?: string
  next_run_at?: string
  created_at: string
  updated_at: string
}

export interface MCPTool {
  name: string
  description: string
  parameters?: Record<string, any>
}

export interface WSMessage {
  type: string
  data: Record<string, any>
}
