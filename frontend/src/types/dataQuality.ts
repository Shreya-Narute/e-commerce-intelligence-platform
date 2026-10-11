export interface ColumnQuality {
  name: string;
  data_type: string;
  nullable: boolean;
  null_count: number;
  null_percentage: number;
}

export interface TableQualityMetric {
  table_name: string;
  row_count: number;
  column_count: number;
  columns: ColumnQuality[];
  completeness_score: number;
  status: 'populated' | 'empty' | 'table_missing';
}

export interface DatasetFileStatus {
  filename: string;
  exists: boolean;
  size_bytes: number;
  size_readable: string;
}

export interface DataQualityReport {
  status: 'operational' | 'pending_ingestion' | 'degraded';
  generated_at: string;
  total_tables: number;
  populated_tables: number;
  total_records: number;
  raw_files_found: number;
  raw_files_total: number;
  raw_files: DatasetFileStatus[];
  tables: TableQualityMetric[];
  pipeline_stage: string;
  warnings: string[];
}
