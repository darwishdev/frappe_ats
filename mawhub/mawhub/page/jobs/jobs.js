frappe.pages["jobs"].on_page_load = function (wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: "jobs",
		single_column: true,
	});

	// ---- route options ----
	const opts = frappe.route_options || {};
	frappe.route_options = null;
	const jobId = opts.job || "JOB-0001";

	// 1) set the module crumb (left-most)
	frappe.breadcrumbs.add("Addicta");

	// 2) If your Frappe has a custom breadcrumb setter, use it
	const crumbs = [
		{ label: __("Jobs"), route: "/app/jobs-candidates" },
		{ label: __("Job Details") },
	];

	if (frappe.breadcrumbs.set_custom_breadcrumbs) {
		frappe.breadcrumbs.set_custom_breadcrumbs(crumbs);
	} else if (frappe.breadcrumbs.set_list) {
		frappe.breadcrumbs.set_list(crumbs);
	} else {
		// fallback: only module crumb will show
	}

	// ---- Mock API ----
	function mockFetchJob(job) {
		return Promise.resolve({
			name: job,
			title: "Director of Sales - MAWHUB",
			department: "Corporate Sales",
			work_mode: "Hybrid",
			location: "New Cairo City, Cairo Governorate, Egypt",
			pipeline_steps: [
				{ key: "all", label: "All" },
				{ key: "sourced", label: "Sourced" },
				{ key: "applied", label: "Applied" },
				{ key: "profiles", label: "Profiles to Review" },
				{ key: "screening", label: "Screening" },
				{ key: "ta", label: "TA Interview" },
				{ key: "tech", label: "Technical Interview" },
				{ key: "final", label: "Final Interview" },
				{ key: "offer", label: "Offer Proposal" },
				{ key: "sent", label: "Offer Sent" },
				{ key: "accepted", label: "Offer Accepted" },
			],
		});
	}

	function mockFetchCandidates(job) {
		return Promise.resolve([
			{
				id: "CAND-0001",
				name: "Moataz Farid Elkholy",
				source: "profile upload",
				applied_ago: "4 months ago",
				stage: "ta",
				location: "Cairo, Egypt",
				phone: "+201010001400",
				headline: "eNovate (2024 - now) · Alexandria University",
				tags: ["Qualified"],
				score: 92,
			},
			{
				id: "CAND-0002",
				name: "Candidate Two",
				source: "referral",
				applied_ago: "2 weeks ago",
				stage: "applied",
				location: "Giza, Egypt",
				phone: "+201234567890",
				headline: "Backend Engineer · 3 yrs",
				tags: ["Disqualified"],
				score: 41,
			},
		]);
	}

	// ---- State ----
	let job = null;
	let candidates = [];
	let activeStep = "all";
	let activeCandidateId = null;

	// ---- Render helpers ----
	function getCountsByStep() {
		const counts = {};
		for (const c of candidates) counts[c.stage] = (counts[c.stage] || 0) + 1;
		counts.all = candidates.length;
		return counts;
	}

	function filteredCandidates() {
		const q = ($("#jd-search").val() || "").trim().toLowerCase();

		return candidates.filter((c) => {
			if (activeStep !== "all" && c.stage !== activeStep) return false;
			if (q) {
				const hay =
					`${c.name} ${c.location} ${c.headline} ${(c.tags || []).join(" ")}`.toLowerCase();
				if (!hay.includes(q)) return false;
			}
			return true;
		});
	}

	function renderPage() {
		const filtered = filteredCandidates();
		const activeCand = filtered.find((c) => c.id === activeCandidateId) || null;
		
		// Render the entire template with Jinja
		const context = {
			job: job,
			active_step: activeStep,
			step_counts: getCountsByStep(),
			candidates: filtered,
			active_candidate_id: activeCandidateId,
			active_candidate: activeCand,
		};
		
		$(page.main).html(frappe.render_template("jobs", context));
		
		// Re-attach event handlers after re-render
		attachEventHandlers();
	}

	function attachEventHandlers() {
		$("#jd-edit-job")
			.off("click")
			.on("click", () => {
				frappe.msgprint(`Mock: edit ${job.name}`);
			});

		$("#jd-add-candidate")
			.off("click")
			.on("click", () => {
				frappe.msgprint("Mock: Add candidates");
			});

		$("#jd-move-next")
			.off("click")
			.on("click", () => {
				frappe.msgprint("Mock: move candidate to next step");
			});

		$(page.main).off("click", ".jd-step").on("click", ".jd-step", function () {
			activeStep = $(this).attr("data-step");
			const list = filteredCandidates();
			if (!list.some((x) => x.id === activeCandidateId)) {
				activeCandidateId = list[0]?.id || null;
			}
			renderPage();
		});

		$(page.main).off("input", "#jd-search").on(
			"input",
			"#jd-search",
			frappe.utils.debounce(() => {
				const list = filteredCandidates();
				if (!list.some((x) => x.id === activeCandidateId)) {
					activeCandidateId = list[0]?.id || null;
				}
				renderPage();
			}, 200),
		);

		$(page.main).off("click", ".jd-item").on("click", ".jd-item", function () {
			activeCandidateId = $(this).attr("data-candidate");
			renderPage();
		});
	}

	// ---- Init ----
	(async function init() {
		page.set_indicator(__("Loading..."), "blue");

		job = await mockFetchJob(jobId);
		candidates = await mockFetchCandidates(jobId);

		activeStep = "all";
		activeCandidateId = candidates[0]?.id || null;

		renderPage();
		page.clear_indicator();
	})();
};
