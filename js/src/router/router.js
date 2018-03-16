import Vue from 'vue'
import Router from 'vue-router'
import DataSelectionPage from '../components/page/data_selection/page.vue'

Vue.use(Router)

const router = new Router({
  routes: [
    { path: '/', name: 'DataSelectionPage', component: DataSelectionPage },
  ]
})

export default router
