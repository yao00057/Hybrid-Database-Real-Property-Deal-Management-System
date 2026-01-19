import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/login'
    },
    {
      path: '/login',
      name: 'Login',
      component: () => import('../views/Login.vue'),
      meta: { requiresGuest: true }
    },
    {
      path: '/register',
      name: 'Register',
      component: () => import('../views/Register.vue'),
      meta: { requiresGuest: true }
    },
    {
      path: '/dashboard',
      name: 'Dashboard',
      component: () => import('../views/Dashboard.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/users',
      name: 'Users',
      component: () => import('../views/Users.vue'),
      meta: {
        requiresAuth: true,
        allowedRoles: ['buyer_agent', 'seller_agent', 'buyer_lawyer', 'seller_lawyer']
      }
    },
    {
      path: '/properties',
      name: 'Properties',
      component: () => import('../views/Properties.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/deals',
      name: 'Deals',
      component: () => import('../views/Deals.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/transactions',
      name: 'Transactions',
      component: () => import('../views/Transactions.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: '/dashboard'
    }
  ]
})

// Navigation guards
router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('token')
  const isAuthenticated = !!token

  // Redirect to login if auth required but not authenticated
  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login')
    return
  }

  // Redirect to dashboard if guest route but already authenticated
  if (to.meta.requiresGuest && isAuthenticated) {
    next('/dashboard')
    return
  }

  // Check role-based access
  if (to.meta.allowedRoles && token) {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]))
      const userRole = payload.role
      const allowedRoles = to.meta.allowedRoles as string[]

      if (!allowedRoles.includes(userRole)) {
        next('/dashboard')
        return
      }
    } catch {
      next('/login')
      return
    }
  }

  next()
})

export default router
