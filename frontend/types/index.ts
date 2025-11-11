// types/index.ts

export interface User {
  username: string;
  email: string;
  full_name: string;
  is_admin: boolean;
}

export interface Dataset {
  id: string;
  dataset_name: string;
  row_count: number;
  column_count: number;
  file_size: number;
  created_at: string;
}

export interface AIProvider {
  name: string;
  value: string;
  models: string[];
}

export interface QueryResult {
  success: boolean;
  sql: string;
  results: any[];
  interpretation: string;
  rows: number;
  columns: number;
}

export interface StatTestResult {
  test: string;
  statistic: number;
  p_value: number;
  significant: boolean;
  interpretation: string;
}