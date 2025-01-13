import { createRouter, createWebHistory } from 'vue-router'
import Editor from './views/Editor.vue'
import NotFound from './views/NotFound.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: Editor
  },
  {
    path: '/p/:id',
    name: 'poem',
    component: Editor
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

export default router 