export interface PipelineStepOption {
    label: string;
    value: string;
}

export interface JobApplicantCreateUpdateRequest {
    name: string;
    email: string;
    lower_range?: string;
    upper_range?: string;
    applicant_id?: string;
}

export interface InterviewAssignmentRequest {
    interview_round: string;
    status: string;
    scheduled_on: string;
    from_time: string;
    to_time: string;
    expected_average_rating?: number;
    interview_summary?: string;
}

export interface BulkMoveRequest {
    target_step: string;
    status?: string;
}

export interface EmailRequest {
    to: string;
    subject: string;
    message: string;
    cc?: string;
    bcc?: string;
    send_me_a_copy?: boolean;
}

export interface ResumeParseProgressData {
    data?: {
        name?: string;
        content?: string;
        [key: string]: any;
    };
}

export interface ApplicantParsedProfile {
    job_applicant: string;
    summary: string | null;
    skills: string | null;
    experience: any[];
    education: any[];
    projects: any[];
    links: any[];
    personal: Record<string, any>;
}
