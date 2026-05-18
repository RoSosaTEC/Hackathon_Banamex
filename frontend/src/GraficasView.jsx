import React, { useState, useEffect, useMemo } from 'react';
import Papa from 'papaparse';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer
} from 'recharts';

const PALETTE = [
  '#00bdf2', '#ee3124', '#68cce7', '#004785',
  '#f5a623', '#7ed321', '#9b59b6', '#e67e22',
  '#1abc9c', '#e74c3c', '#3498db', '#2ecc71',
];

function parseDate(str) {
  if (!str) return null;
  // DD/MM/YYYY or DD/MM/YY
  const parts = str.trim().split('/');
  if (parts.length === 3) {
    const [d, m, y] = parts;
    const year = y.length === 2 ? `20${y}` : y;
    return new Date(`${year}-${m.padStart(2, '0')}-${d.padStart(2, '0')}`);
  }
  // fallback ISO
  return new Date(str.split(' ')[0]);
}

function monthKey(date) {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, '0');
  return `${y}-${m}`;
}

function monthLabel(key) {
  const [y, m] = key.split('-');
  const monthNames = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic'];
  return `${monthNames[parseInt(m, 10) - 1]} ${y}`;
}

export default function GraficasView() {
  const [allRows, setAllRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dateKey, setDateKey] = useState('');
  const [npsKey, setNpsKey] = useState('');
  const [branchKey, setBranchKey] = useState('');
  const [allBranches, setAllBranches] = useState([]);
  const [selectedBranches, setSelectedBranches] = useState([]);

  useEffect(() => {
    Papa.parse('/Data/raw-data-all-clean.csv', {
      download: true,
      header: true,
      skipEmptyLines: true,
      complete: (results) => {
        if (!results.data.length) { setLoading(false); return; }

        const keys = Object.keys(results.data[0]);
        const dKey = keys.find(k => /fecha|date/i.test(k)) || keys[0];
        const nKey = keys.find(k => /nps_rate/i.test(k)) || keys.find(k => /^nps$/i.test(k)) || keys.find(k => /nps/i.test(k)) || keys[1];
        const bKey = keys.find(k => /branch|sucursal/i.test(k)) || keys[2];

        setDateKey(dKey);
        setNpsKey(nKey);
        setBranchKey(bKey);

        const branches = [...new Set(results.data.map(r => r[bKey]).filter(Boolean))].sort();
        setAllBranches(branches);
        setSelectedBranches(branches.slice(0, 3));
        setAllRows(results.data);
        setLoading(false);
      },
      error: () => setLoading(false),
    });
  }, []);

  // Agrupa: { monthKey -> { branchId -> { sum, count } } }
  const chartData = useMemo(() => {
    if (!allRows.length || !dateKey || !npsKey || !branchKey) return [];

    const map = {};
    for (const row of allRows) {
      const date = parseDate(row[dateKey]);
      if (!date || isNaN(date)) continue;
      const nps = parseFloat(row[npsKey]);
      if (isNaN(nps)) continue;
      const branch = row[branchKey];
      if (!branch) continue;

      const mk = monthKey(date);
      if (!map[mk]) map[mk] = {};
      if (!map[mk][branch]) map[mk][branch] = { sum: 0, count: 0 };
      map[mk][branch].sum += nps;
      map[mk][branch].count += 1;
    }

    return Object.keys(map)
      .sort()
      .map(mk => {
        const entry = { month: mk, label: monthLabel(mk) };
        for (const b of selectedBranches) {
          if (map[mk][b]) {
            entry[b] = parseFloat((map[mk][b].sum / map[mk][b].count).toFixed(2));
          } else {
            entry[b] = null;
          }
        }
        return entry;
      });
  }, [allRows, dateKey, npsKey, branchKey, selectedBranches]);

  const toggleBranch = (branch) => {
    setSelectedBranches(prev =>
      prev.includes(branch)
        ? prev.filter(b => b !== branch)
        : [...prev, branch]
    );
  };

  const CustomTooltip = ({ active, payload, label }) => {
    if (!active || !payload?.length) return null;
    return (
      <div className="bg-black border border-brand-line p-3 text-xs font-mono">
        <p className="text-brand-blue mb-2 font-medium">{label}</p>
        {payload.map((p) => (
          <p key={p.dataKey} style={{ color: p.color }}>
            {p.dataKey}: <span className="font-bold">{p.value}</span>
          </p>
        ))}
      </div>
    );
  };

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center text-xl font-light opacity-50 animate-pulse">
        Calculando promedios mensuales...
      </div>
    );
  }

  if (!allRows.length) {
    return (
      <div className="flex-1 flex items-center justify-center text-xl font-light opacity-50">
        No se encontraron datos en el CSV.
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col min-h-0 px-6 pb-6 gap-4">

      {/* HEADER */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-light">
          NPS Promedio Mensual —{' '}
          <span className="font-normal border-b border-brand-line/50 pb-1">
            por Sucursal
          </span>
        </h2>
        <p className="text-xs font-mono opacity-40">
          {selectedBranches.length} / {allBranches.length} sucursales
        </p>
      </div>

      {/* CONTENIDO: sidebar + gráfica */}
      <div className="flex-1 flex flex-row min-h-0 gap-4">

        {/* PANEL LATERAL */}
        <div className="w-44 flex flex-col border border-brand-line shrink-0">
          <div className="flex justify-between items-center px-3 py-2 border-b border-brand-line">
            <span className="text-xs font-mono opacity-60 uppercase tracking-widest">Sucursales</span>
          </div>
          <div className="flex gap-2 px-3 py-2 border-b border-brand-line">
            <button
              onClick={() => setSelectedBranches(allBranches)}
              className="flex-1 text-xs font-mono py-1 border border-brand-line hover:bg-white/10 transition-colors cursor-pointer"
            >
              Todas
            </button>
            <button
              onClick={() => setSelectedBranches([])}
              className="flex-1 text-xs font-mono py-1 border border-brand-line hover:bg-white/10 transition-colors cursor-pointer"
            >
              Ninguna
            </button>
          </div>
          <div className="flex-1 overflow-y-auto">
            {allBranches.map((branch) => {
              const isActive = selectedBranches.includes(branch);
              const color = PALETTE[allBranches.indexOf(branch) % PALETTE.length];
              return (
                <label
                  key={branch}
                  className="flex items-center gap-2 px-3 py-2 cursor-pointer hover:bg-white/5 transition-colors border-b border-brand-line/20"
                >
                  <span
                    className="w-3 h-3 shrink-0 border-2 flex items-center justify-center"
                    style={{ borderColor: color, backgroundColor: isActive ? color : 'transparent' }}
                  >
                    {isActive && <span className="w-1.5 h-1.5 bg-black" />}
                  </span>
                  <input
                    type="checkbox"
                    className="hidden"
                    checked={isActive}
                    onChange={() => toggleBranch(branch)}
                  />
                  <span className="text-xs font-mono truncate" style={{ color: isActive ? color : '#ffffff99' }}>
                    {branch}
                  </span>
                </label>
              );
            })}
          </div>
        </div>

        {/* GRÁFICA */}
        <div className="flex-1 border border-brand-line min-h-0 p-4">
          {selectedBranches.length === 0 ? (
            <div className="h-full flex items-center justify-center opacity-40 font-light">
              Selecciona al menos una sucursal.
            </div>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#004785" strokeOpacity={0.2} />
                <XAxis
                  dataKey="label"
                  tick={{ fill: '#ffffff', fontSize: 11, fontFamily: 'monospace' }}
                  axisLine={{ stroke: '#004785' }}
                  tickLine={false}
                />
                <YAxis
                  tick={{ fill: '#ffffff', fontSize: 11, fontFamily: 'monospace' }}
                  axisLine={{ stroke: '#004785' }}
                  tickLine={false}
                  domain={['auto', 'auto']}
                  width={45}
                />
                <Tooltip content={<CustomTooltip />} />
                <Legend
                  wrapperStyle={{ fontSize: '11px', fontFamily: 'monospace', color: '#fff' }}
                />
                {selectedBranches.map((branch) => (
                  <Line
                    key={branch}
                    type="monotone"
                    dataKey={branch}
                    stroke={PALETTE[allBranches.indexOf(branch) % PALETTE.length]}
                    strokeWidth={2}
                    dot={{ r: 3, strokeWidth: 0 }}
                    activeDot={{ r: 5 }}
                    connectNulls={false}
                  />
                ))}
              </LineChart>
            </ResponsiveContainer>
          )}
        </div>

      </div>
    </div>
  );
}
