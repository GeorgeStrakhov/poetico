import { createRouter, createWebHistory } from 'vue-router'
import Editor from './views/Editor.vue'
import NotFound from './views/NotFound.vue'
import PoemList from './views/PoemList.vue'
import PoemView from './views/PoemView.vue'
import Download from './views/Download.vue'

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