import React, { useState, useEffect } from 'react';

const tableHeaders = ["Frase Clave", "Frecuencia", "Segmento"];

export default function OtroView() {
  // ESTADOS DE DATOS
  const [jsonData, setJsonData] = useState(null);
  const [loading, setLoading] = useState(true);

  // ESTADOS DE FILTRADO Y SCROLL
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedSegment, setSelectedSegment] = useState('');
  const [visibleCount, setVisibleCount] = useState(50);

  // EFECTO PARA CARGAR EL ARCHIVO JSON EXTERNO
  useEffect(() => {
    fetch('/Data/data.json') // <-- Ruta del archivo en la carpeta public
      .then((response) => {
        if (!response.ok) {
          throw new Error('Error al cargar el archivo de insights');
        }
        return response.json();
      })
      .then((data) => {
        setJsonData(data);
        setLoading(false);
      })
      .catch((error) => {
        console.error("Error leyendo el archivo JSON:", error);
        setLoading(false);
      });
  }, []);

  // Manejador del scroll infinito
  const handleScrollGeneral = (e) => {
    const { scrollTop, scrollHeight, clientHeight } = e.currentTarget;
    if (scrollHeight - scrollTop <= clientHeight + 100) {
      if (jsonData && visibleCount < filteredRows.length) {
        setVisibleCount((prev) => Math.min(prev + 50, filteredRows.length));
      }
    }
  };

  // Si está cargando el archivo, mostramos un indicador estilizado
  if (loading) {
    return (
      <div className="text-center py-20 text-xl font-light opacity-50 animate-pulse">
        Cargando insights desde el archivo JSON...
      </div>
    );
  }

  // Si terminó de cargar pero no hay datos, evitamos errores de renderizado
  if (!jsonData || !jsonData.insights) {
    return (
      <div className="text-center py-20 opacity-40 font-light tracking-wide">
        No se pudieron procesar los datos del archivo JSON.
      </div>
    );
  }

  // CÁLCULO DE TOP 3 (Una vez que el JSON ya existe)
  const topDetractores = jsonData.insights.filter(r => r.Segmento === 'Detractores').slice(0, 3);
  const topPromotores = jsonData.insights.filter(r => r.Segmento === 'Promotores').slice(0, 3);
  const topPasivos = jsonData.insights.filter(r => r.Segmento === 'Pasivos').slice(0, 3);

  // FILTRADO DINÁMICO DE LA TABLA
  const filteredRows = jsonData.insights.filter((row) => {
    if (selectedSegment && row.Segmento !== selectedSegment) return false;
    if (!searchTerm) return true;
    const term = searchTerm.toLowerCase();
    return (
      row.Frase_Clave.toLowerCase().includes(term) ||
      String(row.Frecuencia).includes(term) ||
      row.Segmento.toLowerCase().includes(term)
    );
  });

  return (
    <div className="flex-1 flex flex-col min-h-0 w-full relative overflow-hidden">

      {/* 1. SECCIÓN DESTACADA: TOP 3 POR SEGMENTO */}
      <div className="px-6 mb-6 grid grid-cols-3 gap-6 shrink-0">

        {/* PANEL DETRACTORES */}
        <div className="border-2 border-red-500/30 bg-red-950/10 p-4 flex flex-col">
          <h4 className="text-red-400 font-medium tracking-wide uppercase text-xs mb-3 border-b border-red-500/20 pb-1">
            Top 3 Detractores
          </h4>
          <div className="flex flex-col gap-2 flex-1 justify-center">
            {topDetractores.map((item, idx) => (
              <div key={idx} className="flex justify-between items-center text-xs">
                <span className="font-light text-white/80 truncate max-w-[70%]">
                  {idx + 1}. {item.Frase_Clave}
                </span>
                <span className="font-mono text-red-400/90 bg-red-400/10 px-1.5 py-0.5 border border-red-400/20">
                  {item.Frecuencia.toLocaleString()}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* PANEL PROMOTORES */}
        <div className="border-2 border-green-500/30 bg-green-950/10 p-4 flex flex-col">
          <h4 className="text-green-400 font-medium tracking-wide uppercase text-xs mb-3 border-b border-green-500/20 pb-1">
            Top 3 Promotores
          </h4>
          <div className="flex flex-col gap-2 flex-1 justify-center">
            {topPromotores.map((item, idx) => (
              <div key={idx} className="flex justify-between items-center text-xs">
                <span className="font-light text-white/80 truncate max-w-[70%]">
                  {idx + 1}. {item.Frase_Clave}
                </span>
                <span className="font-mono text-green-400/90 bg-green-400/10 px-1.5 py-0.5 border border-green-400/20">
                  {item.Frecuencia.toLocaleString()}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* PANEL PASIVOS */}
        <div className="border-2 border-yellow-500/30 bg-yellow-950/10 p-4 flex flex-col">
          <h4 className="text-yellow-400 font-medium tracking-wide uppercase text-xs mb-3 border-b border-yellow-500/20 pb-1">
            Top 3 Pasivos
          </h4>
          <div className="flex flex-col gap-2 flex-1 justify-center">
            {topPasivos.length > 0 ? topPasivos.map((item, idx) => (
              <div key={idx} className="flex justify-between items-center text-xs">
                <span className="font-light text-white/80 truncate max-w-[70%]">
                  {idx + 1}. {item.Frase_Clave}
                </span>
                <span className="font-mono text-yellow-400/90 bg-yellow-400/10 px-1.5 py-0.5 border border-yellow-400/20">
                  {item.Frecuencia.toLocaleString()}
                </span>
              </div>
            )) : (
              <span className="text-xs text-white/30 font-light italic">Sin registros</span>
            )}
          </div>
        </div>

      </div>

      {/* 2. BARRA DE FILTROS */}
      <div className="flex px-6 mb-4 gap-3 max-w-4xl items-center shrink-0">
        <input
          type="text"
          placeholder="Buscar frase clave..."
          value={searchTerm}
          onChange={(e) => { setSearchTerm(e.target.value); setVisibleCount(50); }}
          className="flex-1 min-w-[150px] bg-black border-2 border-brand-line px-3 py-2 text-xs text-white focus:outline-none placeholder-white/40 tracking-wide font-light"
        />

        <select
          value={selectedSegment}
          onChange={(e) => { setSelectedSegment(e.target.value); setVisibleCount(50); }}
          className="bg-black border-2 border-brand-line px-3 py-2 text-xs text-white focus:outline-none tracking-wide font-light cursor-pointer min-w-[160px]"
        >
          <option value="">Todos los segmentos</option>
          {jsonData.summary.segments.map((segment, i) => (
            <option key={i} value={segment}>{segment}</option>
          ))}
        </select>
      </div>

      {/* INDICADORES DE TABLA */}
      <div className="flex justify-between items-end mb-2 px-6 shrink-0">
        <p className="text-xs font-mono opacity-40">
          Mostrando {Math.min(visibleCount, filteredRows.length)} de {filteredRows.length} N-grams analizados
        </p>
        <p className="text-2xl font-light">
          Total Insights: <span className="font-normal border-b border-brand-line/50 pb-1">{jsonData.summary.total_insights}</span>
        </p>
      </div>

      {/* 3. TABLA COMPLETA CON SCROLL */}
      <div className="flex-1 border-t-2 border-brand-line flex flex-col min-h-0 bg-black w-full">
        <div className="grid grid-cols-3 w-full pt-4 px-4 border-b border-white/20 bg-black shrink-0">
          {tableHeaders.map((headerName, index) => (
            <div key={index} className="pb-3 relative pr-4">
              <h3 className="text-base font-medium tracking-wide opacity-90">{headerName}</h3>
              {index !== tableHeaders.length - 1 && (
                <div className="absolute top-0 right-0 h-6 w-[2px] bg-brand-line opacity-40" />
              )}
            </div>
          ))}
        </div>

        <div onScroll={handleScrollGeneral} className="flex-1 overflow-y-auto w-full scrollbar-none pb-8">
          {filteredRows.length === 0 ? (
            <div className="text-center py-20 opacity-40 font-light tracking-wide">
              Ningún N-gram coincide con los filtros aplicados.
            </div>
          ) : (
            filteredRows.slice(0, visibleCount).map((row, rowIndex) => (
              <div key={rowIndex} className="grid grid-cols-3 px-4 border-b border-white/5 hover:bg-white/5 transition-colors">
                <div className="py-3 pr-4 relative min-h-[44px] flex items-center min-w-0">
                  <p className="text-xs font-light break-words opacity-75 w-full">{row.Frase_Clave}</p>
                  <div className="absolute top-0 right-0 h-full w-[2px] bg-brand-line opacity-20" />
                </div>
                <div className="py-3 pr-4 relative min-h-[44px] flex items-center min-w-0">
                  <p className="text-xs font-mono opacity-75 w-full">{row.Frecuencia.toLocaleString()}</p>
                  <div className="absolute top-0 right-0 h-full w-[2px] bg-brand-line opacity-20" />
                </div>
                <div className="py-3 pr-4 relative min-h-[44px] flex items-center min-w-0">
                  <span className={`text-xs font-medium px-2 py-0.5 rounded border ${row.Segmento === 'Promotores' ? 'text-green-400 border-green-400/20 bg-green-400/5' :
                      row.Segmento === 'Detractores' ? 'text-red-400 border-red-400/20 bg-red-400/5' :
                        'text-yellow-400 border-yellow-400/20 bg-yellow-400/5'
                    }`}>
                    {row.Segmento}
                  </span>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

    </div>
  );
}