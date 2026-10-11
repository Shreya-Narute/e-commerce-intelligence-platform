export interface DatabaseHealth {
  connected: boolean;
  latency_ms: number;
  message: string;
}

export interface SystemInfo {
  python_version: string;
  environment: string;
  debug: boolean;
}

export interface HealthResponse {
  status: 'healthy' | 'degraded' | 'unhealthy';
  app_name: string;
  api_version: string;
  timestamp: string;
  database: DatabaseHealth;
  system: SystemInfo;
}
