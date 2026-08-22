import { createRouter, createWebHistory } from "vue-router"

import HomeView from "../views/HomeView.vue"
import ProductHomeView from "../views/ProductHomeView.vue"
import AuditPage from "../views/AuditPage.vue"
import ReportPage from "../views/ReportPage.vue"
import TokenPage from "../views/TokenPage.vue"
import HistoryPage from "../views/HistoryPage.vue"
import GuideView from "../views/GuideView.vue"

const routes = [
  { path: "/", component: HomeView },
  { path: "/home", component: ProductHomeView, meta: { title: "项目主页", section: "HOME" } },
  { path: "/audit", component: AuditPage },
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

