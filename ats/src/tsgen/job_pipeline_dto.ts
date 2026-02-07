export interface JobPipelineStep {
  step_code: string;
  step_name: string;
  step_type: string;
}

export interface JobPipelineCreateRequest {
  name: string;
  description?: string;
  steps: JobPipelineStep[];
}
