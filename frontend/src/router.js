import { createRouter, createWebHistory } from 'vue-router'
import Editor from './views/Editor.vue'
import NotFound from './views/NotFound.vue'
import PoemList from './views/PoemList.vue'
import PoemView from './views/PoemView.vue'
import Download from './views/Download.vue'
import Auth from './views/Auth.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: PoemList
  },
  {
    path: '/p/:id',
    name: 'poem',
    component: Editor,
    meta: { requiresAuth: true }
  },
  {
    path: '/v',
    name: 'poems',
    component: PoemList
  },
  {
    path: '/v/:id',
    name: 'poem-view',
    component: PoemView
  },
  {
    path: '/download',
    name: 'download',
    component: Download
  },
  {
    path: '/auth',
    name: 'auth',
    component: Auth
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: NotFound
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const isAuthenticated = !!localStorage.getItem('auth_token')
  
  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/v')
  } else {
    next()
  }
})

export default router 