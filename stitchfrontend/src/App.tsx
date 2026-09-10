/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useEffect, useState } from 'react';
import { TabType, DatasetMeta } from './types';
import { Navbar } from './components/Navbar';
import { Footer } from './components/Footer';
import { StoryView } from './components/StoryView';
import { DataLibraryView } from './components/DataLibraryView';
import { ClassicalBaselinesView } from './components/ClassicalBaselinesView';
import { QMLStudioView } from './components/QMLStudioView';
import { CostLatencyDashboardView } from './components/CostLatencyDashboardView';
import { SimulatorDemoView } from './components/SimulatorDemoView';
import { ScoreSheetView } from './components/ScoreSheetView';
import { MetricsGuideModal } from './components/MetricsGuideModal';
import { AboutModal } from './components/AboutModal';
import { FeatureDistributionModal } from './components/FeatureDistributionModal';

export default function App() {
  const [currentTab, setCurrentTab] = useState<TabType>('story');
  const [selectedDatasetId, setSelectedDatasetId] = useState<string>('wisconsin');

  // Modals state
  const [metricsModalOpen, setMetricsModalOpen] = useState(false);
  const [aboutModalOpen, setAboutModalOpen] = useState(false);
  const [inspectingDataset, setInspectingDataset] = useState<DatasetMeta | null>(null);

  const handleSelectDatasetForClassical = (datasetId: string) => {
    setSelectedDatasetId(datasetId);
    setCurrentTab('classical');
  };

  const handleNavigateToScoreSheet = () => {
    setCurrentTab('paste-a-record');
  };

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [currentTab]);

  return (
    <div className="min-h-screen bg-transparent text-[#e6fff4] flex flex-col font-sans selection:bg-[#5cffb5] selection:text-[#032016]">
      {/* Fixed Top Advisory & Navigation Header */}
      <Navbar
        currentTab={currentTab}
        onSelectTab={(tab) => setCurrentTab(tab)}
        onOpenModal={(modal) => {
          if (modal === 'metrics-guide') setMetricsModalOpen(true);
          if (modal === 'about-and-boundaries') setAboutModalOpen(true);
        }}
      />

      {/* Main View Container */}
      <main className="flex-1 w-full pt-40 md:pt-32 pb-20 overflow-x-hidden relative z-10">
        {currentTab === 'story' && (
          <StoryView onNavigate={(tab) => setCurrentTab(tab)} />
        )}

        {currentTab === 'data' && (
          <DataLibraryView
            onSelectDatasetForClassical={handleSelectDatasetForClassical}
            onInspectFeatures={(ds) => setInspectingDataset(ds)}
          />
        )}

        {currentTab === 'classical' && (
          <ClassicalBaselinesView
            selectedDatasetId={selectedDatasetId}
            onSelectDatasetId={setSelectedDatasetId}
            onNavigate={(tab) => setCurrentTab(tab)}
          />
        )}

        {currentTab === 'qml-studio' && <QMLStudioView />}

        {currentTab === 'cost-latency' && <CostLatencyDashboardView />}

        {currentTab === 'simulator-demo' && (
          <SimulatorDemoView
            onNavigateToScoreSheet={handleNavigateToScoreSheet}
          />
        )}

        {currentTab === 'paste-a-record' && <ScoreSheetView />}
      </main>

      {/* Fixed Bottom Safety Ribbon */}
      <Footer
        seed="0x4B3A8F"
        ansatz="RealAmplitudes"
        layers={4}
      />

      {/* Modals */}
      <MetricsGuideModal
        isOpen={metricsModalOpen}
        onClose={() => setMetricsModalOpen(false)}
      />

      <AboutModal
        isOpen={aboutModalOpen}
        onClose={() => setAboutModalOpen(false)}
      />

      <FeatureDistributionModal
        dataset={inspectingDataset}
        onClose={() => setInspectingDataset(null)}
        onLoadInClassical={(dsId) => {
          setSelectedDatasetId(dsId);
          setCurrentTab('classical');
        }}
      />
    </div>
  );
}
