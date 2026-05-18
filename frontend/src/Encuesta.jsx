import React, { useState } from 'react';
import './Encuesta.css'; // <--- Importas tu archivo CSS aquí

export default function Encuesta() {
  const [satisfaction, setSatisfaction] = useState(null);
  const [comment, setComment] = useState('');
  const scaleOptions = Array.from({ length: 11 }, (_, i) => i);

  return (
    <div className="encuesta-container flex flex-col justify-between p-6 md:p-12 select-none">
      
      {/* HEADER */}
      <header className="flex justify-end items-center">
        <div className="border border-brand-line/30 rounded-lg px-6 py-2 bg-white/5 font-bold tracking-widest text-xs uppercase opacity-70">
          Logo
        </div>
      </header>

      {/* CUERPO DEL FORMULARIO */}
      <main className="flex-1 flex flex-col items-center justify-center max-w-2xl mx-auto w-full my-auto">
        <form className="w-full space-y-12">
          
          <h1 className="text-3xl md:text-4xl font-light tracking-wide text-center text-white/95">
            Encuesta de satisfacción
          </h1>

          {/* ESCALA 0-10 */}
          <div className="space-y-6">
            <p className="text-lg md:text-xl font-light text-center text-white/80">
              ¿Cuál fue tu nivel de satisfacción en tu visita?
            </p>

            <div className="flex flex-col items-center space-y-3">
              {/* Aquí aplicas la clase .scrollbar-none que definiste en el CSS */}
              <div className="flex justify-between w-full gap-1 md:gap-2 overflow-x-auto py-2 scrollbar-none">
                {scaleOptions.map((num) => (
                  <button
                    type="button"
                    key={num}
                    onClick={() => setSatisfaction(num)}
                    className={`w-10 h-10 md:w-12 md:h-12 rounded-full border text-sm font-medium flex items-center justify-center transition-all duration-200 shrink-0 ${
                      satisfaction === num
                        ? 'bg-brand-line text-black border-brand-line scale-110 shadow-md'
                        : 'border-white/20 text-white/40 hover:border-brand-line hover:text-white'
                    }`}
                  >
                    {num}
                  </button>
                ))}
              </div>

              <div className="flex justify-between w-full px-1 text-xs md:text-sm text-white/40 font-light">
                <span>Nada</span>
                <span>Mucho</span>
              </div>
            </div>
          </div>

          {/* TEXTAREA COMENTARIOS */}
          <div className="space-y-3">
            <label htmlFor="comments" className="block text-base md:text-lg font-light text-white/80 pl-1">
              Comentarios
            </label>
            <textarea
              id="comments"
              rows={4}
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              placeholder="Agrega tu comentario aquí..."
              className="w-full bg-white/5 border border-white/20 rounded-xl p-4 text-white placeholder-white/20 font-light resize-none transition-colors duration-200 focus:outline-none focus:border-brand-line focus:bg-transparent"
            />
          </div>

          {/* BOTÓN ENVIAR */}
          <div className="flex justify-center">
            <button
              type="submit"
              disabled={satisfaction === null}
              className={`px-8 py-3 rounded-lg border text-xs md:text-sm font-semibold tracking-wider uppercase transition-all duration-200 ${
                satisfaction !== null
                  ? 'border-brand-line bg-brand-line text-black hover:bg-transparent hover:text-white cursor-pointer'
                  : 'border-white/10 text-white/20 cursor-not-allowed'
              }`}
            >
              Enviar respuestas
            </button>
          </div>

        </form>
      </main>

      {/* FOOTER */}
      <footer className="text-center text-[10px] text-white/20 tracking-widest uppercase">
        © {new Date().getFullYear()} Sistema de Feedback
      </footer>

    </div>
  );
}