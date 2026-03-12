import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'

const routes = [
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/auth/Login.vue')
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('../views/auth/Register.vue')
  },
  {
    path: '/users',
    name: 'users',
    component: () => import('../views/admin/Users.vue')
  },
  {
    path: '/videos',
    name: 'videos',
    component: () => import('../views/admin/Videos.vue')
  },
  {
    path: '/',
    name: 'home',
    component: Home
  },
  {
    path: '/overview',
    name: 'overview',
    component: () => import('../views/analysis/Overview.vue')
  },
  {
    path: '/sentiment-trend',
    name: 'sentiment-trend',
    component: () => import('../views/analysis/SentimentTrend.vue')
  },
  {
    path: '/sentiment-trend-analysis',
    name: 'sentiment-trend-analysis',
    component: () => import('../views/analysis/SentimentTrendAnalysis.vue')
  },
  {
    path: '/keywords',
    name: 'keywords',
    component: () => import('../views/analysis/Keywords.vue')
  },
  {
    path: '/comments',
    name: 'comments',
    component: () => import('../views/analysis/Comments.vue')
  },
  {
    path: '/region-distribution',
    name: 'region-distribution',
    component: () => import('../views/analysis/RegionDistribution.vue')
  },
  {
    path: '/export-report',
    name: 'export-report',
    component: () => import('../views/analysis/ExportReport.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const publicPages = ['/login', '/register']
  const authRequired = !publicPages.includes(to.path)
  const user = localStorage.getItem('user')

  if (authRequired && !user) {
    next('/login')
  } else {
    next()
  }
})

export default router
