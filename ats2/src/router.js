import { userResource } from "@/data/user"
import { createRouter, createWebHistory } from "vue-router"
import { session } from "./data/session"

const routes = [
	{
		path: "/",
		name: "Home",
		redirect: "/jobs-pipeline",
		component: () => import("@/pages/Home.vue"),
	},
	{
		path: "/jobs-pipeline",
		name: "JobsPipeline",
		component: () => import("@/pages/jobs/JobsList.vue"),
	},
	{
		path: "/jobs/:jobId",
		name: "JobDetails",
		component: () => import("@/pages/jobs/JobDetails.vue"),
	},
	{
		name: "Login",
		path: "/account/login",
		component: () => import("@/pages/Login.vue"),
	},
]

const router = createRouter({
	history: createWebHistory("/ats2"),
	routes,
})

router.beforeEach(async (to, from, next) => {
	let isLoggedIn = session.isLoggedIn
	try {
		await userResource.promise
	} catch (error) {
		isLoggedIn = false
	}

	if (to.name === "Login" && isLoggedIn) {
		next({ name: "Home" })
	} else if (to.name !== "Login" && !isLoggedIn) {
		next({ name: "Login" })
	} else {
		next()
	}
})

export default router
