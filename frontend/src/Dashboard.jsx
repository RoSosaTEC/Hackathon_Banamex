import React from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import './Dashboard.css';

export default function Dashboard() {
  return (
    <div className="dashboard-container h-screen w-screen flex flex-col select-none p-0 overflow-hidden bg-black text-white">
      
      {/* HEADER GLOBAL */}
      <header className="flex justify-between items-center pt-6 px-6 mb-4 w-full">
        
        {/* BOTONES DE ROUTEO */}
        <div className="flex border-2 border-brand-line text-xl bg-black shrink-0">
          <NavLink
            to="/dashboard/data"
            className={({ isActive }) =>
              `px-8 py-3 font-medium transition-colors ${
                isActive ? 'bg-brand-line text-black' : 'text-white hover:bg-white/10'
              }`
            }
          >
            Data
          </NavLink>
          
          <NavLink
            to="/dashboard/graficas"
            className={({ isActive }) =>
              `px-8 py-3 font-medium border-l-2 border-brand-line transition-colors ${
                isActive ? 'bg-brand-line text-black' : 'text-white hover:bg-white/10'
              }`
            }
          >
            Gráficas
          </NavLink>

          <NavLink
            to="/dashboard/otro"
            className={({ isActive }) =>
              `px-8 py-3 font-medium border-l-2 border-brand-line transition-colors ${
                isActive ? 'bg-brand-line text-black' : 'text-white hover:bg-white/10'
              }`
            }
          >
            Otro
          </NavLink>
        </div>

        {/* LOGO BANAMEX */}
        <div className="border-brand-line px-4 py-3 bg-black shrink-0">
          <img src="/img/Banamex-Logo.png" alt="Banamex Logo" className="h-25 w-auto object-contain" />
        </div>
      </header>

      {/* CONTENIDO DINÁMICO */}
      <main className="flex-1 flex flex-col min-h-0 w-full">
        {/* Aquí React Router renderizará DataView, GraficasView o OtroView dependiendo de la URL */}
        <Outlet />
      </main>
    </div>
  );
}