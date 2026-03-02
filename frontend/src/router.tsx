import { createBrowserRouter } from 'react-router-dom'
import App from './App'

const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
    children: [
      {
        path: '/login',
        lazy: () => import('./pages/Login'),
      },
      {
        path: '/register',
        lazy: () => import('./pages/Register'),
      },
      {
        path: '/projects',
        lazy: () => import('./pages/ProjectList'),
      },
      {
        path: '/projects/:id',
        lazy: () => import('./pages/ProjectDetail'),
      },
    ],
  },
])

export default router
