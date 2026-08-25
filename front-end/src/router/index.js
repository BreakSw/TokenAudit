import { createRouter, createWebHistory } from "vue-router"

import HomeView from "../views/HomeView.vue"
import ProductHomeView from "../views/ProductHomeView.vue"
import AuditPage from "../views/AuditPage.vue"
import DeepAuditPage from "../views/DeepAuditPage.vue"
import ReportPage from "../views/ReportPage.vue"
import TokenPage from "../views/TokenPage.vue"
import HistoryPage from "../views/HistoryPage.vue"
import GuideView from "../views/GuideView.vue"

const routes = [
  { path: "/", component: HomeView },
  { path: "/home", component: ProductHomeView, meta: { title: "项目主页", section: "HOME" } },
  { path: "/audit", component: AuditPage, meta: { title: "快速审计", section: "01" } },
  { path: "/audit/deep", component: DeepAuditPage, meta: { title: "深度审计", section: "02" } },
  { path: "/report/:id", component: ReportPage, props: true },
  { path: "/tokens", component: TokenPage },
  { path: "/history", component: HistoryPage },
  { path: "/guide", component: GuideView }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router

