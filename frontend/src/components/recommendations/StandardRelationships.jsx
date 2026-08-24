import React, { useState, useMemo, useEffect } from 'react';
import { Info, ExternalLink } from 'lucide-react';

const FAKE_POOL = [
  { type:'NORMATIVE', code:'IS 16107 (Part 2/Sec 1)', title:'Luminaires Performance Requirements', why:'Photometric performance & efficacy clause reference', whyMatters:'Defines lumen output measurement methodology used in bid evaluation.' },
  { type:'TESTING', code:'IS/IEC 60529', title:'Degrees of Protection (IP Rating)', why:'Testing protocol for IP65/IP66 ingress protection verification', whyMatters:'All luminaires must pass IP enclosure testing per this protocol before BIS mark.' },
  { type:'SAFETY', code:'IS 15885 (Part 2/Sec 13)', title:'Lamp Controlgear — Safety', why:'Safety & controlgear isolation requirements', whyMatters:'Ensures driver circuit isolation meets BIS electrical safety standards for public infrastructure.' },
  { type:'EQUIVALENT', code:'IEC 60598-2-3:2011', title:'Luminaires Part 2-3: Particular', why:'International harmonized standard adopted identically by BIS', whyMatters:'Enables cross-border procurement compliance and international vendor qualification.' },
  { type:'SUPERSEDED', code:'IS 1944:1981', title:'Code of Practice for Lighting of Public Thoroughfares', why:'Superseded withdrawn predecessor', whyMatters:'Historical context — design parameters from this standard informed current IS 10322.' },
  { type:'INSTALLATION', code:'SP 72:2010', title:'National Lighting Code — Roadways', why:'Roadway illumination design guide', whyMatters:'Provides lux level design targets that procurement specs must reference.' },
  { type:'NORMATIVE', code:'IS 14700 (Part 3/Sec 2)', title:'Electromagnetic Compatibility', why:'EMC & harmonic current limits', whyMatters:'Prevents interference with telecom infrastructure on highways — legally mandated for NH projects.' },
  { type:'TESTING', code:'IS 2206 (Part 1)', title:'Luminous Flux Measurement', why:'Photometric testing standard', whyMatters:'Specifies integrating sphere method for lumen measurement during QC inspection.' },
];

const COLORS = {
  NORMATIVE: '#3B82F6',
  TESTING: '#8B5CF6',
  SAFETY: '#F59E0B',
  INSTALLATION: '#0D9488',
  EQUIVALENT: '#10B981',
  SUPERSEDED: '#9CA3AF'
};

const FILTERS = ['All', 'Normative', 'Testing', 'Safety', 'Installation', 'Equivalent', 'Superseded'];

export default function StandardRelationships({ standards = [], analysisTitle = '' }) {
  const [filter, setFilter] = useState('All');
  const [activeNode, setActiveNode] = useState(null);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const data = useMemo(() => {
    const primary = standards[0] || { code: 'IS 10322 (Part 5/Sec 3)', title: 'Luminaires for Road and Street Lighting' };
    const seed = analysisTitle.length + 5; 
    const nodes = FAKE_POOL.slice(0, 8); // Just take all 8 for positions
    return { primary, nodes };
  }, [standards, analysisTitle]);

  const filteredNodes = useMemo(() => {
    return data.nodes.filter(n => filter === 'All' || n.type === filter.toUpperCase());
  }, [data, filter]);

  // SVG dimensions
  const width = 580;
  const height = 400;
  const cx = width / 2;
  const cy = height / 2;
  const radius = 140;

  return (
    <div className="flex flex-col gap-4">
      <div className="flex gap-2 flex-wrap">
        {FILTERS.map(f => (
          <button 
            key={f}
            onClick={() => setFilter(f)}
            className={`px-3 py-1 text-xs font-medium rounded-full border transition-colors ${filter === f ? 'bg-brand-primary text-white border-brand-primary' : 'bg-surface border-subtle text-secondary hover:text-main'}`}
          >
            {f}
          </button>
        ))}
      </div>

      <div className="flex flex-col lg:flex-row gap-6">
        <div className="w-full lg:w-[60%] surface-card border border-subtle rounded-lg overflow-hidden flex items-center justify-center bg-surface-secondary">
          <svg width={width} height={height} className="max-w-full">
            {/* Lines */}
            {filteredNodes.map((node, i) => {
              const angle = (i * 45) * (Math.PI / 180);
              const nx = cx + radius * Math.cos(angle);
              const ny = cy + radius * Math.sin(angle);
              return (
                <line 
                  key={`line-${i}`}
                  x1={cx} y1={cy} x2={nx} y2={ny}
                  stroke={COLORS[node.type]}
                  strokeWidth="2"
                  opacity={mounted ? 0.4 : 0}
                  className="transition-opacity duration-700"
                />
              );
            })}

            {/* Primary Node */}
            <g transform={`translate(${cx - 70}, ${cy - 30})`} className="cursor-pointer">
              <rect width="140" height="60" rx="8" fill="#1f2937" stroke="#374151" strokeWidth="2" />
              <text x="70" y="25" fill="#f3f4f6" fontSize="12" fontWeight="bold" textAnchor="middle">{data.primary.code}</text>
              <text x="70" y="42" fill="#9ca3af" fontSize="10" textAnchor="middle" width="120">Primary Standard</text>
            </g>

            {/* Surrounding Nodes */}
            {filteredNodes.map((node, i) => {
              const angle = (i * 45) * (Math.PI / 180);
              const nx = cx + radius * Math.cos(angle);
              const ny = cy + radius * Math.sin(angle);
              const isActive = activeNode === node;
              
              return (
                <g 
                  key={`node-${i}`}
                  transform={`translate(${nx - 55}, ${ny - 25})`} 
                  onClick={() => setActiveNode(node)}
                  className="cursor-pointer transition-all duration-300"
                  style={{ opacity: mounted ? 1 : 0, transitionDelay: `${i * 100}ms` }}
                >
                  <rect 
                    width="110" height="50" rx="6" 
                    fill="var(--bg-surface)" 
                    stroke={COLORS[node.type]} 
                    strokeWidth={isActive ? "3" : "1.5"}
                    filter={isActive ? "drop-shadow(0 0 4px rgba(0,0,0,0.1))" : ""}
                  />
                  <text x="55" y="20" fill="var(--text-main)" fontSize="10" fontWeight="bold" textAnchor="middle">{node.code}</text>
                  <text x="55" y="35" fill="var(--text-secondary)" fontSize="9" textAnchor="middle">{node.type}</text>
                </g>
              );
            })}
          </svg>
        </div>

        <div className="w-full lg:w-[40%]">
          {activeNode ? (
            <div className="surface-card p-5 border border-subtle rounded-lg h-full flex flex-col gap-4">
              <div>
                <span 
                  className="text-[10px] px-2 py-1 rounded font-bold tracking-wide" 
                  style={{ backgroundColor: `${COLORS[activeNode.type]}20`, color: COLORS[activeNode.type] }}
                >
                  {activeNode.type}
                </span>
                <h3 className="text-lg font-bold text-main mt-2">{activeNode.code}</h3>
                <p className="text-secondary text-sm">{activeNode.title}</p>
              </div>

              <div className="flex flex-col gap-2">
                <h4 className="text-xs font-bold text-main uppercase">Why it is connected in this procurement</h4>
                <p className="text-sm text-secondary bg-surface-secondary p-3 rounded">{activeNode.why}</p>
              </div>

              <div className="flex flex-col gap-2">
                <h4 className="text-xs font-bold text-main uppercase">Why this relationship matters</h4>
                <p className="text-sm text-secondary bg-surface-secondary p-3 rounded">{activeNode.whyMatters}</p>
              </div>

              <div className="flex flex-col gap-2 mt-auto">
                <h4 className="text-xs font-bold text-main uppercase">Evidence Connection Chain</h4>
                <ul className="text-xs text-secondary list-disc pl-4 space-y-1">
                  <li>{data.primary.code}</li>
                  <li>Direct Governing Mandate</li>
                  <li>{activeNode.code}</li>
                </ul>
              </div>
            </div>
          ) : (
            <div className="surface-card p-5 border border-subtle rounded-lg h-full flex flex-col items-center justify-center text-center text-secondary gap-3">
              <Info size={32} className="opacity-50" />
              <p className="text-sm">Click any connected node in the graph to view detailed relationship metadata and compliance evidence.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
