export type TabType =
  | 'story'
  | 'data'
  | 'classical'
  | 'qml-studio'
  | 'cost-latency'
  | 'simulator-demo'
  | 'paste-a-record';

export interface DatasetMeta {
  id: string;
  name: string;
  code: string;
  ref: string;
  targetDescription: string;
  sampleCount: number;
  totalPopulation?: string;
  split: string;
  dimensionality: string;
  features: string[];
  qubits: number;
  scikitBaselineName: string;
  scikitBaselineF1: number;
  scikitBaselineAccuracy: number;
  qmlModelName: string;
  qmlModelF1: number;
  qmlModelAccuracy: number;
  qmlF1Delta: string;
  preprocessing: string;
  license: string;
  experimentTag: string;
  experimentType: string;
}

export interface FeatureSliderConfig {
  id: string;
  name: string;
  dimLabel: string;
  min: number;
  max: number;
  step: number;
  defaultVal: number;
  unit: string;
  formatRaw: (z: number) => string;
  weight: number; // Beta coefficient in LR
}

export interface ModelPrediction {
  linearLR: {
    margin: number;
    score: number;
    band: 'Lower' | 'Middle' | 'Higher';
  };
  treeEnsemble: {
    vote: number;
    score: number;
  };
  quantumKernel: {
    overlap: number;
    score: number;
  };
  hyperplaneDelta: number;
}
