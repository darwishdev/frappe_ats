import { createResource } from '@/utils/resource';
// Import your DTOs here - you might want to automate this path
import { JobOpeningDTO } from './tal_models';

export function use_job_opening_list(initialParams?: { customer: string, owner: string }) {
  return createResource<JobOpeningDTO[]>({
    url: 'mawhub.mawhub_job_opening_api.job_opening_list',
    params: initialParams,
  });
}

export function use_job_opening_find(initialParams?: { job: string }) {
  return createResource<JobOpeningDTO>({
    url: 'mawhub.mawhub_job_opening_api.job_opening_find',
    params: initialParams,
  });
}

export function use_job_opening_create_update(initialParams?: { payload: Record<string, any> }) {
  return createResource<any>({
    url: 'mawhub.mawhub_job_opening_api.job_opening_create_update',
    params: initialParams,
  });
}

export function use_generate_applicant_email(initialParams?: { applicant: Record<string, any>, job: Record<string, any>, pipeline_step: string, user_instructions: string }) {
  return createResource<string>({
    url: 'mawhub.mawhub_job_opening_api.generate_applicant_email',
    params: initialParams,
  });
}
