import { createApp } from "vue"
import ElementPlus from "element-plus"
import "element-plus/dist/index.css"
import "./styles/theme.css"
import App from "./App.vue"
import router from "./router"
import reveal from "./directives/reveal"

createApp(App).use(router).use(ElementPlus).directive("reveal", reveal).mount("#app")
