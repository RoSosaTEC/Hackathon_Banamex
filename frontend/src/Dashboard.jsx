import React from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import './Dashboard.css';

export default function Dashboard() {
  return (
    <div className="dashboard-container h-screen w-screen flex flex-col select-none p-0 overflow-hidden text-white">

      {/* BARRA DE ACENTO SUPERIOR */}
      <div className="h-1 w-full bg-brand-red shrink-0" />

      {/* HEADER GLOBAL */}
      <header className="flex justify-between items-center pt-5 px-6 pb-5 w-full bg-surface-raised border-b border-brand-line/20">

        {/* BOTONES DE ROUTEO */}
        <div className="flex gap-1 bg-surface-elevated p-1 rounded-xl shrink-0">
          <NavLink
            to="/dashboard/data"
            className={({ isActive }) =>
              `px-6 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                isActive ? 'bg-white text-surface-base shadow' : 'text-white/50 hover:text-white hover:bg-white/10'
              }`
            }
          >
            Data
          </NavLink>

          <NavLink
            to="/dashboard/graficas"
            className={({ isActive }) =>
              `px-6 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                isActive ? 'bg-white text-surface-base shadow' : 'text-white/50 hover:text-white hover:bg-white/10'
              }`
            }
          >
            Gráficas
          </NavLink>

          <NavLink
            to="/dashboard/otro"
            className={({ isActive }) =>
              `px-6 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                isActive ? 'bg-white text-surface-base shadow' : 'text-white/50 hover:text-white hover:bg-white/10'
              }`
            }
          >
            Otro
          </NavLink>
        </div>

        {/* LOGO BANAMEX */}
        <div className="shrink-0">
          <img src="/img/Banamex-Logo.png" alt="Banamex Logo" className="h-20 w-auto object-contain" />
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