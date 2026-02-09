frappe.pages["jobs"].on_page_load = function (wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: "Jobs",
		single_column: true,
	});

	// ---- Route options ----
	const opts = frappe.route_options || {};
	frappe.route_options = null;
	const jobId = opts.job || frappe.get_route()[1] || null;

	if (!jobId) {
		frappe.msgprint(__("No job ID provided"));
		return;
	}

	// Breadcrumbs
	frappe.breadcrumbs.add("Mawhub");
	const crumbs = [
		{ label: __("Jobs"), route: "/app/jobs-candidates" },
		{ label: __("Job Details") },
	];

	if (frappe.breadcrumbs.set_custom_breadcrumbs) {
		frappe.breadcrumbs.set_custom_breadcrumbs(crumbs);
	} else if (frappe.breadcrumbs.set_list) {
		frappe.breadcrumbs.set_list(crumbs);
	}

	// ---- State ----
	let job = null;
	let steps = {};
	let allCandidates = [];
	let activeStep = null;
	let activeCandidateId = null;
	let selectedCandidates = new Set();
	let activeTab = "profile";

	// ---- API Functions ----
	async function fetchJobOpening(jobName) {
		return new Promise((resolve, reject) => {
			frappe.call({
				method: "mawhub.job_opening_find",
				args: { job: jobName },
				callback: (r) => {
					if (r.message) {
						resolve(r.message);
					} else {
						reject(new Error("Failed to fetch job opening"));
					}
				},
				error: (err) => reject(err),
			});
		});
	}

	async function bulkUpdateApplicants(payload) {
		return new Promise((resolve, reject) => {
			frappe.call({
				method: "mawhub.job_applicant_bulk_update",
				args: { payload: payload },
				callback: (r) => {
					if (r.message) {
						resolve(r.message);
					} else {
						reject(new Error("Failed to update applicants"));
					}
				},
				error: (err) => reject(err),
			});
		});
	}

	async function sendApplicantEmail(payload) {
		return new Promise((resolve, reject) => {
			frappe.call({
				method: "mawhub.send_applicant_email",
				args: { payload: payload },
				callback: (r) => {
					if (r.message) {
						resolve(r.message);
					} else {
						reject(new Error("Failed to send email"));
					}
				},
				error: (err) => reject(err),
			});
		});
	}

	async function createOrUpdateInterview(payload) {
		return new Promise((resolve, reject) => {
			frappe.call({
				method: "mawhub.interview_create_update",
				args: { payload: payload },
				callback: (r) => {
					if (r.message) {
						resolve(r.message);
					} else {
						reject(new Error("Failed to create interview"));
					}
				},
				error: (err) => reject(err),
			});
		});
	}

	// ---- Helper Functions ----
	function getStepCounts() {
		const counts = {};
		if (job && job.steps) {
			job.steps.forEach((step) => {
				counts[step.step_id] = step.candidates ? step.candidates.length : 0;
			});
		}
		return counts;
	}

	function filteredCandidates() {
		if (!activeStep || !steps[activeStep]) return [];
		
		const stepCandidates = steps[activeStep].candidates || [];
		const q = ($("#jd-search").val() || "").trim().toLowerCase();

		if (!q) return stepCandidates;

		return stepCandidates.filter((c) => {
			const searchText = `${c.applicant_name} ${c.email_id} ${c.phone_number || ""} ${c.country || ""}`.toLowerCase();
			return searchText.includes(q);
		});
	}

	function getActiveCandidateDetails() {
		if (!activeCandidateId) return null;
		const candidates = filteredCandidates();
		return candidates.find((c) => c.applicant_id === activeCandidateId) || null;
	}

	// ---- Render Function ----
	function renderPage() {
		const filtered = filteredCandidates();
		const activeCand = getActiveCandidateDetails();
		
		const context = {
			job: job,
			active_step: activeStep,
			step_counts: getStepCounts(),
			candidates: filtered,
			active_candidate_id: activeCandidateId,
			active_candidate: activeCand,
			selected_candidates: Array.from(selectedCandidates),
			has_selected_candidates: selectedCandidates.size > 0,
			active_tab: activeTab,
		};
		
		$(page.main).html(frappe.render_template("jobs", context));
		attachEventHandlers();
	}

	// ---- Event Handlers ----
	function attachEventHandlers() {
		// Pipeline step navigation
		$(page.main).off("click", ".jd-step").on("click", ".jd-step", function () {
			activeStep = $(this).attr("data-step");
			selectedCandidates.clear();
			
			const list = filteredCandidates();
			const currentExists = list.some((x) => x.applicant_id === activeCandidateId);
			if (!currentExists) {
				activeCandidateId = list[0]?.applicant_id || null;
			}
			renderPage();
		});

		// Search
		$(page.main).off("input", "#jd-search").on(
			"input",
			"#jd-search",
			frappe.utils.debounce(() => {
				const list = filteredCandidates();
				const currentExists = list.some((x) => x.applicant_id === activeCandidateId);
				if (!currentExists) {
					activeCandidateId = list[0]?.applicant_id || null;
				}
				renderPage();
			}, 300),
		);

		// Candidate selection
		$(page.main).off("click", ".jd-item").on("click", ".jd-item", function (e) {
			if ($(e.target).hasClass("jd-candidate-checkbox")) return;
			activeCandidateId = $(this).attr("data-candidate");
			renderPage();
		});

		// Checkbox selection
		$(page.main).off("change", ".jd-candidate-checkbox").on("change", ".jd-candidate-checkbox", function (e) {
			e.stopPropagation();
			const candidateId = $(this).attr("data-candidate");
			if ($(this).is(":checked")) {
				selectedCandidates.add(candidateId);
			} else {
				selectedCandidates.delete(candidateId);
			}
			renderPage();
		});

		// Tab navigation
		$(page.main).off("click", ".jd-tab-button").on("click", ".jd-tab-button", function () {
			activeTab = $(this).attr("data-tab");
			renderPage();
		});

		// Edit job
		$("#jd-edit-job").off("click").on("click", () => {
			if (!job) return;
			frappe.set_route("Form", "Job Opening", job.name);
		});

		// View job description
		$("#jd-view-description").off("click").on("click", () => {
			if (!job) return;
			showJobDescriptionDialog();
		});

		// Edit pipeline
		$("#jd-edit-pipeline").off("click").on("click", () => {
			if (!job) return;
			showEditPipelineDialog();
		});

		// Move to step
		$("#jd-move-to-step").off("change").on("change", function () {
			const targetStep = $(this).val();
			if (!targetStep || !activeCandidateId) return;
			moveCandidateToStep(activeCandidateId, targetStep);
			$(this).val("");
		});

		// Bulk actions
		$("#jd-bulk-move").off("click").on("click", () => {
			if (selectedCandidates.size === 0) return;
			showBulkMoveDialog();
		});

		$("#jd-bulk-email").off("click").on("click", () => {
			if (selectedCandidates.size === 0) return;
			showBulkEmailDialog();
		});

		$("#jd-clear-selection").off("click").on("click", () => {
			selectedCandidates.clear();
			renderPage();
		});

		// Action buttons
		$("#jd-assign-interview").off("click").on("click", () => {
			if (!activeCandidateId) return;
			showAssignInterviewDialog();
		});

		$("#jd-send-email").off("click").on("click", () => {
			if (!activeCandidateId) return;
			showSendEmailDialog();
		});

		$("#jd-share-candidate").off("click").on("click", () => {
			if (!activeCandidateId) return;
			shareCandidate();
		});

		$("#jd-edit-candidate").off("click").on("click", () => {
			if (!activeCandidateId) return;
			frappe.set_route("Form", "Job Applicant", activeCandidateId);
		});
	}

	// ---- Action Functions ----
	async function moveCandidateToStep(candidateId, targetStepId) {
		try {
			const payload = {
				names: [candidateId],
				pipeline_step: targetStepId,
				status: "Open",
			};

			await bulkUpdateApplicants(payload);
			frappe.show_alert({ message: __("Candidate moved successfully"), indicator: "green" });
			
			// Refresh data
			await loadJobData();
			activeStep = targetStepId;
			activeCandidateId = candidateId;
			renderPage();
		} catch (error) {
			frappe.msgprint({
				title: __("Error"),
				message: error.message || __("Failed to move candidate"),
				indicator: "red",
			});
		}
	}

	function showBulkMoveDialog() {
		const dialog = new frappe.ui.Dialog({
			title: __("Move Candidates"),
			fields: [
				{
					fieldtype: "Select",
					fieldname: "target_step",
					label: __("Target Step"),
					options: job.steps.map((s) => s.step_name),
					reqd: 1,
				},
			],
			primary_action_label: __("Move"),
			primary_action: async (values) => {
				const targetStep = job.steps.find((s) => s.step_name === values.target_step);
				if (!targetStep) return;

				try {
					const payload = {
						names: Array.from(selectedCandidates),
						pipeline_step: targetStep.step_id,
						status: "Open",
					};

					await bulkUpdateApplicants(payload);
					dialog.hide();
					frappe.show_alert({
						message: __("{0} candidates moved successfully", [selectedCandidates.size]),
						indicator: "green",
					});

					selectedCandidates.clear();
					await loadJobData();
					activeStep = targetStep.step_id;
					renderPage();
				} catch (error) {
					frappe.msgprint({
						title: __("Error"),
						message: error.message || __("Failed to move candidates"),
						indicator: "red",
					});
				}
			},
		});
		dialog.show();
	}

	function showBulkEmailDialog() {
		const activeCand = getActiveCandidateDetails();
		const dialog = new frappe.ui.Dialog({
			title: __("Send Email to Selected Candidates"),
			fields: [
				{
					fieldtype: "Data",
					fieldname: "subject",
					label: __("Subject"),
					reqd: 1,
				},
				{
					fieldtype: "Text Editor",
					fieldname: "message",
					label: __("Message"),
					reqd: 1,
				},
			],
			primary_action_label: __("Send"),
			primary_action: async (values) => {
				const candidates = filteredCandidates().filter((c) =>
					selectedCandidates.has(c.applicant_id)
				);

				try {
					for (const candidate of candidates) {
						const payload = {
							recipient: candidate.email_id,
							subject: values.subject,
							message: values.message,
							job_applicant: candidate.applicant_id,
							job_opening: job.name,
						};
						await sendApplicantEmail(payload);
					}

					dialog.hide();
					frappe.show_alert({
						message: __("Emails sent successfully"),
						indicator: "green",
					});
				} catch (error) {
					frappe.msgprint({
						title: __("Error"),
						message: error.message || __("Failed to send emails"),
						indicator: "red",
					});
				}
			},
		});
		dialog.show();
	}

	function showAssignInterviewDialog() {
		const activeCand = getActiveCandidateDetails();
		if (!activeCand) return;

		const dialog = new frappe.ui.Dialog({
			title: __("Assign Interview"),
			fields: [
				{
					fieldtype: "Data",
					fieldname: "interview_round",
					label: __("Interview Round"),
					reqd: 1,
				},
				{
					fieldtype: "Date",
					fieldname: "scheduled_on",
					label: __("Scheduled Date"),
					reqd: 1,
				},
				{
					fieldtype: "Time",
					fieldname: "from_time",
					label: __("From Time"),
					reqd: 1,
				},
				{
					fieldtype: "Time",
					fieldname: "to_time",
					label: __("To Time"),
					reqd: 1,
				},
				{
					fieldtype: "Small Text",
					fieldname: "interview_summary",
					label: __("Notes"),
				},
			],
			primary_action_label: __("Assign"),
			primary_action: async (values) => {
				try {
					const payload = {
						job_applicant: activeCand.applicant_id,
						interview_round: values.interview_round,
						status: "Pending",
						scheduled_on: values.scheduled_on,
						from_time: values.from_time,
						to_time: values.to_time,
						interview_summary: values.interview_summary || "",
					};

					await createOrUpdateInterview(payload);
					dialog.hide();
					frappe.show_alert({
						message: __("Interview assigned successfully"),
						indicator: "green",
					});
				} catch (error) {
					frappe.msgprint({
						title: __("Error"),
						message: error.message || __("Failed to assign interview"),
						indicator: "red",
					});
				}
			},
		});
		dialog.show();
	}

	function showSendEmailDialog() {
		const activeCand = getActiveCandidateDetails();
		if (!activeCand) return;

		const dialog = new frappe.ui.Dialog({
			title: __("Send Email"),
			fields: [
				{
					fieldtype: "Data",
					fieldname: "recipient",
					label: __("To"),
					default: activeCand.email_id,
					reqd: 1,
				},
				{
					fieldtype: "Data",
					fieldname: "subject",
					label: __("Subject"),
					reqd: 1,
				},
				{
					fieldtype: "Text Editor",
					fieldname: "message",
					label: __("Message"),
					reqd: 1,
				},
				{
					fieldtype: "Data",
					fieldname: "cc",
					label: __("CC"),
				},
			],
			primary_action_label: __("Send"),
			primary_action: async (values) => {
				try {
					const payload = {
						recipient: values.recipient,
						subject: values.subject,
						message: values.message,
						cc: values.cc || "",
						job_applicant: activeCand.applicant_id,
						job_opening: job.name,
					};

					await sendApplicantEmail(payload);
					dialog.hide();
					frappe.show_alert({
						message: __("Email sent successfully"),
						indicator: "green",
					});
				} catch (error) {
					frappe.msgprint({
						title: __("Error"),
						message: error.message || __("Failed to send email"),
						indicator: "red",
					});
				}
			},
		});
		dialog.show();
	}

	function showJobDescriptionDialog() {
		const dialog = new frappe.ui.Dialog({
			title: __("Job Description"),
			fields: [
				{
					fieldtype: "HTML",
					fieldname: "description",
				},
			],
		});

		const description = job.description || "<p>No description available</p>";
		dialog.fields_dict.description.$wrapper.html(description);
		dialog.show();
	}

	function showEditPipelineDialog() {
		frappe.msgprint(__("Pipeline editing will open the Job Opening form"));
		frappe.set_route("Form", "Job Opening", job.name);
	}

	function shareCandidate() {
		const activeCand = getActiveCandidateDetails();
		if (!activeCand) return;

		const url = `${window.location.origin}/app/job-applicant/${activeCand.applicant_id}`;
		
		if (navigator.clipboard) {
			navigator.clipboard.writeText(url).then(() => {
				frappe.show_alert({
					message: __("Link copied to clipboard"),
					indicator: "green",
				});
			});
		} else {
			frappe.msgprint({
				title: __("Share Candidate"),
				message: `<p>Copy this link:</p><input type="text" class="form-control" value="${url}" readonly onclick="this.select()">`,
			});
		}
	}

	// ---- Load Data ----
	async function loadJobData() {
		try {
			page.set_indicator(__("Loading..."), "blue");
			
			const data = await fetchJobOpening(jobId);
			job = data;
			
			// Build steps lookup
			steps = {};
			if (job.steps) {
				job.steps.forEach((step) => {
					steps[step.step_id] = step;
				});
			}

			// Set initial active step
			if (!activeStep && job.steps && job.steps.length > 0) {
				activeStep = job.steps[0].step_id;
			}

			// Set initial active candidate
			const candidates = filteredCandidates();
			if (!activeCandidateId && candidates.length > 0) {
				activeCandidateId = candidates[0].applicant_id;
			}

			page.set_title(job.job_title || "Job Details");
			page.clear_indicator();
			
			renderPage();
		} catch (error) {
			page.clear_indicator();
			frappe.msgprint({
				title: __("Error"),
				message: error.message || __("Failed to load job data"),
				indicator: "red",
			});
		}
	}

	// ---- Initialize ----
	loadJobData();
};