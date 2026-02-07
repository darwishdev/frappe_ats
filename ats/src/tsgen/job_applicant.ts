export interface JobApplicantCreateWithResume {
  applicant_resume: ApplicantResumeDTO;
  pipeline_step_id: string;
  job_opening_id: string;
}

export interface JobApplicantUpdateRequest {
  name: string;
  status: string;
  pipeline_step: string;
}

export interface JobApplicantBulkUpdateRequest {
  names: string[];
  status: string;
  pipeline_step: string;
}
