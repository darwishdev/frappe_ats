<template>
  <div class="flex h-screen w-full">
    <Sidebar
      :header="{
        title: 'ATS System',
        subtitle: session.user || 'User',
        menuItems: [
          {
            label: 'Help',
            icon: 'lucide-help-circle',
            onClick: () => showHelp(),
          },
          {
            label: 'Logout',
            icon: 'lucide-log-out',
            onClick: () => session.logout.submit(),
          },
        ],
      }"
      :sections="[
        {
          label: 'Recruitment',
          items: [
            {
              label: 'Job Openings',
              icon: {
                name: 'lucide-users',
              },
              to: '/jobs-pipeline',
            },
            {
              label: 'Candidates',
              // icon: 'lucide-users',
              to: '/candidates',
            },
            {
              label: 'Interviews',
              // icon: 'lucide-calendar',
              to: '/interviews',
            },
          ],
        },
        {
          label: 'Management',
          items: [
            {
              label: 'Dashboard',
              // icon: 'lucide-layout-dashboard',
              to: '/',
            },
          ],
        },
      ]"
    />
    <div class="flex-1 overflow-auto">
      <div class="p-4">
        <Breadcrumbs :items="breadcrumbItems" />
      </div>
      <router-view />
    </div>
  </div>
</template>

<script setup>
import { Sidebar, Breadcrumbs } from "frappe-ui";
import { session } from "./data/session";
import { useRoute } from "vue-router";
import { computed } from "vue";

const route = useRoute();

// Route metadata mapping for breadcrumbs
const routeMetadata = {
  "/": {
    label: "Dashboard",
    icon: "lucide-home",
  },
  "/jobs-pipeline": {
    label: "Job Openings",
    icon: "lucide-briefcase",
  },
  "/candidates": {
    label: "Candidates",
    icon: "lucide-users",
  },
  "/interviews": {
    label: "Interviews",
    icon: "lucide-calendar",
  },
};

// Dynamically generate breadcrumb items based on current route
const breadcrumbItems = computed(() => {
  const items = [
    {
      label: "Home",
      icon: "lucide-home",
      route: "/",
    },
  ];

  const currentPath = route.path;
  
  // Handle job details page
  if (currentPath.startsWith("/jobs/") || currentPath === "/job-details") {
    items.push({
      label: "Job Openings",
      icon: "lucide-briefcase",
      route: "/jobs-pipeline",
    });
    items.push({
      label: "Job Details",
      icon: "lucide-file-text",
      route: currentPath,
    });
    return items;
  }
  
  // If we're not on home page, add the current page
  if (currentPath !== "/" && routeMetadata[currentPath]) {
    items.push({
      label: routeMetadata[currentPath].label,
      icon: routeMetadata[currentPath].icon,
      route: currentPath,
    });
  }

  return items;
});

function showHelp() {
  alert("Help documentation coming soon!");
}
</script>
