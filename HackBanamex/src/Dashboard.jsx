import React, { useState, useEffect } from 'react';
import Papa from 'papaparse';
import './Dashboard.css';

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState('data');
  const [csvHeaders, setCsvHeaders] = useState([]);
  const [csvRows, setCsvRows] = useState([]);
  const [visibleCount, setVisibleCount] = useState(50);
  const [loading, setLoading] = useState(true);

  // ESTADOS DE FILTRADO
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedBranch, setSelectedBranch] = useState('');
  const [uniqueBranches, setUniqueBranches] = useState([]);
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  useEffect(() => {
    Papa.parse('/Data/raw-data-all-clean.csv', { 
      download: true,
      header: true,
      skipEmptyLines: true,
      complete: (results) => {
        if (results.data.length > 0) {
          const keys = Object.keys(results.data[0]).slice(0, 6);
          setCsvHeaders(keys);
          setCsvRows(results.data);

          // EXTRAER SUCURSALES ÚNICAS: Busca la columna que contenga "branch" o "Id" de sucursal
          // Ajusta el string 'Id_Branch' si en tu CSV se escribe diferente (ej. 'id_branch', 'Branch')
          const branchKey = Object.keys(results.data[0]).find(k => k.toLowerCase().includes('branch') || k.toLowerCase().includes('sucursal'));
          
          if (branchKey) {
            const branches = [...new Set(results.data.map(row => row[branchKey]).filter(Boolean))];
            setUniqueBranches(branches.sort());
          }
        }
        setLoading(false);
      },
      error: (error) => {
        console.error("Error al leer el archivo CSV:", error);
        setLoading(false);
      }
    });
  }, []);

  const handleScrollGeneral = (e) => {
    const { scrollTop, scrollHeight, clientHeight } = e.currentTarget;
    if (scrollHeight - scrollTop <= clientHeight + 100) {
      if (visibleCount < filteredRows.length) {
        setVisibleCount((prev) => Math.min(prev + 50, filteredRows.length));
      }
    }
  };

  // MOTOR DE FILTRADO MULTI-VARIABLE (Alto Rendimiento)
  const filteredRows = csvRows.filter((row) => {
    // 1. Filtro por Sucursal / Branch
    const branchKey = csvHeaders.find(k => k.toLowerCase().includes('branch') || k.toLowerCase().includes('sucursal'));
    if (selectedBranch && branchKey && row[branchKey] !== selectedBranch) {
      return false;
    }

    // 2. Filtro por Rango de Fechas
    const dateKey = csvHeaders.find(k => k.toLowerCase().includes('fecha') || k.toLowerCase().includes('date'));
    if (dateKey && (startDate || endDate)) {
      const rowDateStr = row[dateKey];
      if (rowDateStr) {
        // Convierte la fecha del registro (adapta el substring si tu formato varía)
        const rowDate = new Date(rowDateStr.split(' ')[0]); 
        
        if (startDate && rowDate < new Date(startDate)) return false;
        if (endDate && rowDate > new Date(endDate)) return false;
      } else {
        return false; // Si no tiene fecha y hay rango activo, se descarta
      }
    }

    // 3. Filtro de Texto Global (Buscador previo)
    if (!searchTerm) return true;
    const term = searchTerm.toLowerCase();
    return csvHeaders.some((header) => {
      const cellValue = String(row[header] || '').toLowerCase();
      return cellValue.includes(term);
    });
  });

  // Funciones controladoras para reiniciar el scroll infinito al cambiar filtros
  const handleSearchChange = (e) => {
    setSearchTerm(e.target.value);
    setVisibleCount(50); 
  };

  const handleBranchChange = (e) => {
    setSelectedBranch(e.target.value);
    setVisibleCount(50);
  };

  const handleStartDateChange = (e) => {
    setStartDate(e.target.value);
    setVisibleCount(50);
  };

  const handleEndDateChange = (e) => {
    setEndDate(e.target.value);
    setVisibleCount(50);
  };

  return (
    <div className="dashboard-container h-screen w-screen flex flex-col select-none p-0 overflow-hidden bg-black text-white">
      
      {/* HEADER */}
      <header className="flex justify-between items-center pt-6 px-6 mb-4 w-full">
        <div className="flex border-2 border-brand-line text-xl bg-black shrink-0">
          <button
            onClick={() => setActiveTab('data')}
            className={`px-8 py-3 font-medium transition-colors ${
              activeTab === 'data' ? 'bg-brand-line text-black' : 'text-white hover:bg-white/10'
            }`}
          >
            Data
          </button>
          <button
            onClick={() => setActiveTab('graficas')}
            className={`px-8 py-3 font-medium border-l-2 border-brand-line transition-colors ${
              activeTab === 'graficas' ? 'bg-brand-line text-black' : 'text-white hover:bg-white/10'
            }`}
          >
            Graficas
          </button>
        </div>

        {/* ÁREA DE CONTROLES Y FILTROS INTEGRADOS (Estilo pizarra) */}
        <div className="flex flex-1 mx-6 gap-3 max-w-4xl items-center">
          
          {/* Buscador de Texto */}
          <input
            type="text"
            placeholder="Buscar texto..."
            value={searchTerm}
            onChange={handleSearchChange}
            className="flex-1 min-w-[150px] bg-black border-2 border-brand-line px-3 py-2 text-xs text-white focus:outline-none placeholder-white/40 tracking-wide font-light"
          />

          {/* Selector de Branch */}
          <select
            value={selectedBranch}
            onChange={handleBranchChange}
            className="bg-black border-2 border-brand-line px-3 py-2 text-xs text-white focus:outline-none tracking-wide font-light cursor-pointer min-w-[140px]"
          >
            <option value="">Todas las sucursales</option>
            {uniqueBranches.map((branch, i) => (
              <option key={i} value={branch}>{branch}</option>
            ))}
          </select>

          {/* Rango de Fechas */}
          <div className="flex items-center gap-1 border-2 border-brand-line px-2 py-1 bg-black text-xs font-light">
            <span className="opacity-40 text-[10px] uppercase mr-1">Desde:</span>
            <input 
              type="date" 
              value={startDate} 
              onChange={handleStartDateChange}
              className="bg-black text-white outline-none cursor-pointer inverted-colors-scheme"
            />
            <span className="opacity-40 text-[10px] uppercase mx-1">Hasta:</span>
            <input 
              type="date" 
              value={endDate} 
              onChange={handleEndDateChange}
              className="bg-black text-white outline-none cursor-pointer"
            />
          </div>

        </div>

        <div className="border-2 border-brand-line px-12 py-3 text-2xl tracking-widest bg-black shrink-0">
          <img src="/img/Banamex-Logo.png" alt="/img/Banamex-Logo.png" />
        </div>
      </header>

      {/* CUERPO PRINCIPAL */}
      <main className="flex-1 flex flex-col min-h-0 w-full">
        {loading ? (
          <div className="text-center py-20 text-xl font-light opacity-50 animate-pulse">
            Procesando registros del CSV...
          </div>
        ) : activeTab === 'data' ? (
          <div className="flex-1 flex flex-col min-h-0 w-full relative">
            
            {/* Indicadores superiores */}
            <div className="flex justify-between items-end mb-2 px-6">
              <p className="text-xs font-mono opacity-40">
                Mostrando {Math.min(visibleCount, filteredRows.length)} de {filteredRows.length} filas encontradas
              </p>
              <p className="text-2xl font-light">
                NPS General: <span className="font-normal border-b border-brand-line/50 pb-1">94</span>
              </p>
            </div>

            {/* TABLA GRID GENERAL */}
            <div className="flex-1 border-t-2 border-brand-line flex flex-col min-h-0 bg-black w-full">
              
              <div className="grid grid-cols-6 w-full pt-4 px-4 border-b border-white/20 bg-black">
                {csvHeaders.map((headerName, index) => (
                  <div key={index} className="pb-3 relative pr-4">
                    <h3 className="text-base font-medium tracking-wide text-ellipsis overflow-hidden whitespace-nowrap opacity-90">
                      {headerName}
                    </h3>
                    {index !== csvHeaders.length - 1 && (
                      <div className="absolute top-0 right-0 h-6 w-[2px] bg-brand-line opacity-40" />
                    )}
                  </div>
                ))}
              </div>

              <div 
                onScroll={handleScrollGeneral}
                className="flex-1 overflow-y-auto w-full scrollbar-none pb-8"
              >
                {filteredRows.length === 0 ? (
                  <div className="text-center py-20 opacity-40 font-light tracking-wide">
                    Ningún registro coincide con los filtros aplicados.
                  </div>
                ) : (
                  filteredRows.slice(0, visibleCount).map((row, rowIndex) => (
                    <div 
                      key={rowIndex} 
                      className="grid grid-cols-6 px-4 border-b border-white/5 hover:bg-white/5 transition-colors"
                    >
                      {csvHeaders.map((headerName, colIndex) => (
                        <div 
                          key={colIndex} 
                          className="py-3 pr-4 relative min-h-[44px] flex items-center min-w-0"
                        >
                          <p className="text-xs font-light break-words leading-relaxed opacity-75 w-full">
                            {row[headerName] || '---'}
                          </p>
                          {colIndex !== csvHeaders.length - 1 && (
                            <div className="absolute top-0 right-0 h-full w-[2px] bg-brand-line opacity-20" />
                          )}
                        </div>
                      ))}
                    </div>
                  ))
                )}
              </div>

            </div>

          </div>
        ) : (
          <div className="flex-1 border-2 border-dashed border-brand-line/30 m-6 text-center text-xl font-light opacity-60 flex items-center justify-center">
            [ Área de Gráficas para NPS e Historial ]
          </div>
        )}
      </main>
    </div>
  );
}
