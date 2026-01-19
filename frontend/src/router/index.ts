import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue')
  },
  {
    path: '/users',
    name: 'Users',
    component: () => import('../views/Users.vue')
  },
  {
    path: '/properties',
    name: 'Properties',
    component: () => import('../views/Properties.vue')
  },
  {
    path: '/deals',
    name: 'Deals',
    component: () => import('../views/Deals.vue')
  },
  {
    path: '/transactions',
    name: 'Transactions',
    component: () => import('../views/Transactions.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
