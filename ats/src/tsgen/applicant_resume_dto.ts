export interface PersonalInfo {
  name: string
  email: string
  phone: string
  location: string
  links: string[]
}

export interface ApplicantExperience {
  company: string
  role: string
  from_date: string
  to_date: string
  description: string
}

export interface ApplicantEducation {
  institution: string
  degree: string
  from_date: string
  to_date: string
}

export interface ApplicantProject {
  title: string
  description: string
  link: string
}

export interface ApplicantLink {
  label: string
  url: string
}

export interface ApplicantResumeDTO {
  job_applicant: string
  personal: PersonalInfo
  skills?: string
  summary?: string
  raw_resume_text?: string
  resume_hash?: string
  experience?: ApplicantExperience[]
  education?: ApplicantEducation[]
  projects?: ApplicantProject[]
  links?: ApplicantLink[]
}
