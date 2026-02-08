import type { JobOpeningDTO } from "../tsgen/job_opening";

let _createResource : any = null;

export const NewJobDetailsAPI = {
    /**
     * Initialize the API client with frappe-ui createResource function
     * Call this in onMounted of your Vue component
     * @param {Function} createResource - createResource function from frappe-ui
     */
    init: function (createResource : any) {
        _createResource = createResource;
    },

        /**
     * Find job opening details
     * @param {string} jobName - Job opening name/ID
     * @returns {Promise<Object>} Job opening details
     */
    findJobOpening: function (jobName : string) : Promise<JobOpeningDTO> {
        if (!_createResource) {
            throw new Error(
                "JobDetailsAPI not initialized. Call JobDetailsAPI.init(createResource) first.",
            );
        }

        const resource = _createResource({
            url: "mawhub.job_opening_find",
            method: "GET",
            params: {
                job: jobName,
            },
            auto: true,
        });

        return resource.promise;
    },
}