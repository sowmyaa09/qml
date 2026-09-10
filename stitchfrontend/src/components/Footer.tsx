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
    <aside className="fixed bottom-0 left-0 right-0 h-9 z-20 bg-[#02110c]/92 backdrop-blur-md border-t-2 border-[#5cffb5]/40 flex items-center justify-between px-4 pointer-events-none">
      <div className="flex items-center gap-2 overflow-hidden text-ellipsis whitespace-nowrap">
        <span className="w-1.5 h-1.5 rounded-full bg-[#5cffb5] shrink-0 shadow-[0_0_8px_#5cffb5]"></span>
        <span className="font-mono text-[11px] text-[#b8ffd9] truncate">
          [RESEARCH ENVIRONMENT: NON-DIAGNOSTIC] Exploratory hybrid variational quantum algorithms evaluated on anonymized biomedical tables.
        </span>
      </div>
      <div className="flex items-center gap-4 shrink-0 font-mono text-[11px]">
        <span className="hidden sm:inline-block text-[#7dffc4]">
          Ansatz: {ansatz} · Layers: {layers}
        </span>
        <span className="text-[#5cffb5] drop-shadow-[0_0_6px_rgba(94,255,181,0.8)]">Seed: {seed}</span>
      </div>
    </aside>
  );
};
