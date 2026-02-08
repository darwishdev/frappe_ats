export interface InterviewFeedbackDTO {
  feedback_id: string;
  feedback_interviewer: string;
  feedback_result: string;
  feedback_average_rating: number;
  feedback_text?: string;
  feedback_docstatus: number;
  feedback_created_at: string;
  feedback_modified_at: string;
}

export interface InterviewDTO {
  interview_id: string;
  interview_round: string;
  interview_status: string;
  interview_scheduled_on: string;
  interview_from_time: string;
  interview_to_time: string;
  interview_expected_avg_rating: number;
  interview_average_rating: number;
  interview_job_opening: string;
  interview_designation: string;
  interview_docstatus: number;
  interview_created_at: string;
  interview_modified_at: string;
  feedbacks: InterviewFeedbackDTO[];
}

export interface AppointmentLetterDTO {
  appointment_letter_id: string;
  appointment_company: string;
  appointment_date: string;
  appointment_template: string;
  appointment_docstatus: number;
  appointment_created_at: string;
  appointment_modified_at: string;
}

export interface JobOfferDTO {
  job_offer_id: string;
  job_offer_status: string;
  job_offer_date: string;
  job_offer_company: string;
  job_offer_designation: string;
  job_offer_applicant_email: string;
  job_offer_docstatus: number;
  job_offer_created_at: string;
  job_offer_modified_at: string;
}

export interface CandidateDTO {
  job_opening_id?: string;
  pipeline_id?: string;
  pipeline_description?: string;
  pipeline_is_primary?: number;
  pipeline_docstatus?: number;
  pipeline_created_at?: string;
  pipeline_modified_at?: string;
  pipeline_step_id?: number;
  pipeline_step_idx?: number;
  pipeline_step_name?: string;
  pipeline_step_type?: string;
  pipeline_parent_id?: string;
  applicant_id?: string;
  applicant_name?: string;
  applicant_email?: string;
  applicant_phone?: string;
  applicant_country?: string;
  applicant_job_title?: string;
  applicant_designation?: string;
  applicant_status?: string;
  applicant_source?: string;
  applicant_source_name?: string;
  applicant_employee_referral?: string;
  applicant_rating?: number;
  applicant_resume_link?: string;
  applicant_resume_attachment?: string;
  applicant_cover_letter?: string;
  applicant_pipeline_step_ref?: string;
  applicant_docstatus?: number;
  applicant_created_at?: string;
  applicant_modified_at?: string;
  appointment_letters?: AppointmentLetterDTO[];
  job_offers?: JobOfferDTO[];
  interviews?: InterviewDTO[];
}

export interface JobPipelineStepCandidateDTO {
  "applicant_id": string,
  "applicant_name": string,
  "applicant_email": string,
  "applicant_status": string,
  "applicant_rating": number,
  "applicant_source"?: string,
  "applicant_phone"?: string,
  "applicant_country": string,
  "applicant_designation": string
}

export interface JobPipelineStepDTO {
  step_id: string;
  step_name: string;
  step_type: string;
  step_idx: number;
  candidates: JobPipelineStepCandidateDTO[];
  candidate_count: number;
}

export interface JobOpeningDTO {
  name: string;
  designation: string;
  department?: string;
  pipeline?: string;
  parsed_documents: any[];
  employment_type: string;
  location: string;
  customer: string;
  docstatus: number;
  publish: number;
  publish_salary_range: number;
  publish_applications_received: number;
  route: string;
  job_application_route?: string;
  currency: string;
  salary_per: string;
  lower_range: string;
  upper_range: string;
  posted_on: string;
  closes_on: string;
  step_count: number;
  candidate_count: number;
  steps: JobPipelineStepDTO[];
}

export interface JobOpeningCreateRequest {
  job_title: string;
  designation?: string;
  company?: string;
  location?: string;
  planned_vacancies: number;
  vacancies: number;
  lower_range: number;
  upper_range: number;
  publish: number;
  publish_salary_range: number;
  publish_applications_received: number;
  customer: number;
}
