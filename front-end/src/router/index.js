import { createRouter, createWebHistory } from "vue-router"

import HomeView from "../views/HomeView.vue"
import AuditPage from "../views/AuditPage.vue"
import ReportPage from "../views/ReportPage.vue"
import TokenPage from "../views/TokenPage.vue"
import HistoryPage from "../views/HistoryPage.vue"

const routes = [
  { path: "/", component: HomeView },
  { path: "/audit", component: AuditPage },
  { path: "/report/:id", component: ReportPage, props: true },
  { path: "/tokens", component: TokenPage },
  { path: "/history", component: HistoryPage }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router

