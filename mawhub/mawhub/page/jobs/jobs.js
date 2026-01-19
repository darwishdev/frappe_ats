frappe.pages["jobs"].on_page_load = function (wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: "jobs",
		single_column: true,
	});

	$(page.main).html(frappe.render_template("jobs", {}));

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
	const esc = frappe.utils.escape_html;

	function getCountsByStep() {
		const counts = {};
		for (const c of candidates) counts[c.stage] = (counts[c.stage] || 0) + 1;
		counts.all = candidates.length;
		return counts;
	}

	function renderHeader() {
		$("#jd-job-title").text(job.title);
		$("#jd-job-subtitle").text(`${job.department} · ${job.work_mode} · ${job.location}`);

		$("#jd-edit-job")
			.off("click")
			.on("click", () => {
				// later: route to actual Job Opening doc
				frappe.msgprint(`Mock: edit ${job.name}`);
			});

		$("#jd-add-candidate")
			.off("click")
			.on("click", () => {
				frappe.msgprint("Mock: Add candidates");
			});
	}

	function renderPipeline() {
		const counts = getCountsByStep();

		$("#jd-pipeline").html(
			job.pipeline_steps
				.map((s) => {
					const cnt = counts[s.key] || 0;
					const active = s.key === activeStep ? "active" : "";
					return `
          <div class="jd-step ${active}" data-step="${esc(s.key)}">
            ${esc(s.label)} <span class="count">${cnt ? cnt : "–"}</span>
          </div>
        `;
				})
				.join(""),
		);
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

	function renderCandidateList() {
		const list = filteredCandidates();

		$("#jd-candidate-list").html(
			list
				.map(
					(c) => `
        <div class="jd-item ${c.id === activeCandidateId ? "active" : ""}" data-candidate="${esc(c.id)}">
          <div class="jd-avatar">${esc(c.name.split(" ").slice(0, 1)[0].slice(0, 1))}</div>
          <div>
            <div class="jd-item-name">${esc(c.name)}</div>
            <div class="jd-item-sub">via <b>${esc(c.source)}</b> · ${esc(c.applied_ago)}</div>
          </div>
        </div>
      `,
				)
				.join("") || `<div class="text-muted" style="padding:10px;">No candidates</div>`,
		);
	}

	function renderCandidateDetails() {
		const c = candidates.find((x) => x.id === activeCandidateId);
		if (!c) {
			$("#jd-detail-card").html(
				`<div class="text-muted">Select a candidate from the list.</div>`,
			);
			return;
		}

		$("#jd-detail-card").html(`
      <div class="jd-detail-head">
        <div>
          <h3 class="jd-detail-name">${esc(c.name)}</h3>
          <div class="jd-detail-meta">${esc(c.headline || "")}</div>
          <div class="jd-badges">
            <span class="jd-badge">📍 ${esc(c.location)}</span>
            <span class="jd-badge">☎ ${esc(c.phone)}</span>
            <span class="jd-badge">Score: ${esc(String(c.score))}</span>
          </div>
          <div class="jd-badges" style="margin-top:10px;">
            ${(c.tags || []).map((t) => `<span class="jd-badge">${esc(t)}</span>`).join("")}
          </div>
        </div>

        <div>
          <button class="btn btn-default btn-sm" id="jd-move-next">Move to next step</button>
        </div>
      </div>
    `);

		$("#jd-move-next")
			.off("click")
			.on("click", () => {
				frappe.msgprint("Mock: move candidate to next step");
			});
	}

	function renderAll() {
		renderHeader();
		renderPipeline();
		renderCandidateList();
		renderCandidateDetails();
	}

	// ---- Events ----
	$(page.main).on("click", ".jd-step", function () {
		activeStep = $(this).attr("data-step");
		// reset selection if it disappears from filter
		const list = filteredCandidates();
		if (!list.some((x) => x.id === activeCandidateId)) activeCandidateId = list[0]?.id || null;
		renderAll();
	});

	$(page.main).on(
		"input",
		"#jd-search",
		frappe.utils.debounce(() => {
			const list = filteredCandidates();
			if (!list.some((x) => x.id === activeCandidateId))
				activeCandidateId = list[0]?.id || null;
			renderCandidateList();
			renderCandidateDetails();
		}, 200),
	);

	$(page.main).on("click", ".jd-item", function () {
		activeCandidateId = $(this).attr("data-candidate");
		renderCandidateList();
		renderCandidateDetails();
	});

	// ---- Init ----
	(async function init() {
		page.set_indicator(__("Loading..."), "blue");

		job = await mockFetchJob(jobId);
		candidates = await mockFetchCandidates(jobId);

		activeStep = "all";
		activeCandidateId = candidates[0]?.id || null;

		renderAll();
		page.clear_indicator();
	})();
};
