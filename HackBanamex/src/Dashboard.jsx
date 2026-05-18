import React, { useState, useEffect, useRef } from 'react';
import Papa from 'papaparse';
import './Dashboard.css';

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState('data');
  const [csvHeaders, setCsvHeaders] = useState([]);
  const [allRows, setAllRows] = useState([]); // Mantiene las 600k filas en memoria externa
  const [visibleCount, setVisibleCount] = useState(50); // Cuántas filas se muestran inicialmente
  const [loading, setLoading] = useState(true);

  // Carga e indexación inicial del CSV masivo
  useEffect(() => {
    Papa.parse('../Data/raw-data-all-clean.csv', {
      download: true,
      header: true,
      skipEmptyLines: true,
      complete: (results) => {
        if (results.data.length > 0) {
          const keys = Object.keys(results.data).slice(0, 6);
          setCsvHeaders(keys);
          setAllRows(results.data);
        }
        setLoading(false);
      },
      error: (error) => {
        console.error("Error al leer el archivo CSV:", error);
        setLoading(false);
      }
    });
  }, []);

  // Función para detectar si el usuario llegó al fondo de una columna y cargar más datos
  const handleScroll = (e) => {
    const { scrollTop, scrollHeight, clientHeight } = e.currentTarget;
    // Si falta poco para llegar al final (100px), incrementamos el lote de filas visibles
    if (scrollHeight - scrollTop <= clientHeight + 100) {
      if (visibleCount < allRows.length) {
        setVisibleCount((prev) => Math.min(prev + 50, allRows.length));
      }
    }
  };

  return (
    /* p-0 y w-screen quitan cualquier rastro de bordes gordos en la pantalla */
    <div className="dashboard-container h-screen w-screen flex flex-col select-none p-0 overflow-hidden bg-black text-white">
      
      {/* HEADER: Con padding interno sutil para que no pegue al borde superior */}
      <header className="flex justify-between items-start pt-6 px-6 mb-4">
        <div className="flex border-2 border-brand-line text-xl bg-black">
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

        <div className="border-2 border-brand-line px-12 py-3 text-2xl tracking-widest bg-black">
          Logo
        </div>
      </header>

      {/* CUERPO PRINCIPAL */}
      <main className="flex-1 flex flex-col min-h-0 w-full">
        {loading ? (
          <div className="text-center py-20 text-xl font-light opacity-50 animate-pulse">
            Procesando {allRows.length || 'registros'} del CSV de forma optimizada...
          </div>
        ) : activeTab === 'data' ? (
          <div className="flex-1 flex flex-col min-h-0 w-full relative">
            
            {/* NPS General ajustado a la derecha con un margen sutil */}
            <div className="text-right mb-2 pr-6">
              <p className="text-2xl font-light">
                NPS General: <span className="font-normal border-b border-brand-line/50 pb-1">94</span>
              </p>
            </div>

            {/* SECCIÓN HORIZONTAL: grid de 6 columnas ocupando el 100% de la pantalla de extremo a extremo */}
            <div className="flex-1 border-t-2 border-brand-line grid grid-cols-6 w-full min-h-0 bg-black">
              {csvHeaders.map((headerName, index) => (
                <div 
                  key={index} 
                  className="pt-4 px-4 relative flex flex-col min-h-0 h-full"
                >
                  {/* Título de tu columna */}
                  <h3 className="text-base font-medium mb-3 tracking-wide text-ellipsis overflow-hidden whitespace-nowrap opacity-90">
                    {headerName}
                  </h3>

                  {/* CONTENEDOR CON LA CARGA DINÁMICA: 
                      Escucha el evento onScroll y renderiza solo el subconjunto de filas activas */}
                  <div 
                    onScroll={handleScroll}
                    className="flex-1 overflow-y-auto h-full pr-1 scrollbar-none pb-8"
                  >
                    <table className="w-full text-left text-xs opacity-75 table-fixed">
                      <tbody>
                        {allRows.slice(0, visibleCount).map((row, rowIndex) => (
                          <tr key={rowIndex} className="border-b border-white/5 hover:bg-white/5">
                            <td className="py-2.5 text-left font-light break-words leading-relaxed">
                              {row[headerName] || '---'}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>

                  {/* Línea blanca vertical de separación del boceto que ahora cubre todo el largo disponible */}
                  {index !== csvHeaders.length - 1 && (
                    <div className="absolute top-0 right-0 h-full w-[2px] bg-brand-line opacity-40" />
                  )}
                </div>
              ))}
            </div>

          </div>
        ) : (
          /* Pestaña de Gráficas */
          <div className="flex-1 border-2 border-dashed border-brand-line/30 m-6 text-center text-xl font-light opacity-60 flex items-center justify-center">
            [ Área de Gráficas para NPS e Historial ]
          </div>
        )}
      </main>
    </div>
  );
}
