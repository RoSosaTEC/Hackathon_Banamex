import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { createBrowserRouter, RouterProvider, Navigate } from 'react-router-dom'
import './index.css'

// Importamos todos tus componentes independientes
import Dashboard from './Dashboard.jsx'
import DataView from './DataView.jsx'
import GraficasView from './GraficasView.jsx'
import OtroView from './OtroView.jsx'
import Encuesta from './Encuesta.jsx'

const router = createBrowserRouter([
  {
    path: "/",
    element: <Navigate to="/dashboard/data" replace />, 
  },
  {
    path: "/dashboard",
    element: <Dashboard />, // El padre (contiene el Header y el Outlet)
    children: [
      {
        path: "data", // URL: /dashboard/data
        element: <DataView />,
      },
      {
        path: "graficas", // URL: /dashboard/graficas
        element: <GraficasView />,
      },
      {
        path: "otro", // URL: /dashboard/otro
        element: <OtroView />,
      },
      {
        path: "", // Si entran a /dashboard a secas, redirige a data
        element: <Navigate to="data" replace />,
      }
    ]
  },
  {
    path: "/encuesta",
    element: <Encuesta />,
  },
  {
    path: "*",
    element: <Navigate to="/dashboard/data" replace />,
  }
]);

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>,
)