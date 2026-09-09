import React from 'react';

interface FooterProps {
  seed?: string;
  ansatz?: string;
  layers?: number;
}

export const Footer: React.FC<FooterProps> = ({
  seed = '0x4B3A8F',
  ansatz = 'RealAmplitudes',
  layers = 4,
}) => {
  return (
    <aside className="fixed bottom-0 left-0 right-0 h-9 z-50 bg-[#070b13]/95 backdrop-blur-md border-t border-[#31353f]/50 flex items-center justify-between px-4 shadow-[0_-1px_8px_rgba(0,0,0,0.6)]">
      <div className="flex items-center gap-2 overflow-hidden text-ellipsis whitespace-nowrap">
        <span className="w-1.5 h-1.5 rounded-full bg-[#d0bcff] shrink-0"></span>
        <span className="font-mono text-[11px] text-[#b9cacb] truncate">
          [RESEARCH ENVIRONMENT: NON-DIAGNOSTIC] Exploratory hybrid variational quantum algorithms evaluated on anonymized biomedical tables.
        </span>
      </div>
      <div className="flex items-center gap-4 shrink-0 font-mono text-[11px]">
        <span className="hidden sm:inline-block text-[#849495]">
          Ansatz: {ansatz} · Layers: {layers}
        </span>
        <span className="text-[#00dbe9]">Seed: {seed}</span>
      </div>
    </aside>
  );
};
