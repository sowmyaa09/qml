/** Plain-language help for paste-a-record columns (matches src/feature_labels.py). */

export type FieldHelp = {
  key: string;
  label: string;
  description: string;
};

export const WISCONSIN_REDUCED_FIELDS: FieldHelp[] = [
  {
    key: 'mean perimeter',
    label: 'Mean perimeter of cell nuclei',
    description:
      'Average length around the edge of breast cell nuclei in the fine-needle aspirate (FNA) sample.',
  },
  {
    key: 'mean concave points',
    label: 'Mean concave points (indent severity)',
    description:
      'Average severity of inward curves on the nuclear boundary — a shape measure from FNA image analysis.',
  },
  {
    key: 'worst radius',
    label: 'Worst (largest) radius of cell nuclei',
    description:
      'Largest half-width among the most abnormal-looking nuclei (radius = center to edge).',
  },
  {
    key: 'worst perimeter',
    label: 'Worst (largest) perimeter of cell nuclei',
    description:
      'Longest edge-length around the most abnormal nuclei — related to cell size and shape.',
  },
  {
    key: 'worst area',
    label: 'Worst (largest) area of cell nuclei',
    description: 'Largest nuclear footprint among the most abnormal cells in the sample.',
  },
  {
    key: 'worst concave points',
    label: 'Worst concave points (max indent severity)',
    description:
      'Strongest inward curve on the most abnormal nuclei — a shape feature, not a symptom.',
  },
];

export const HEART_CP_FIELD: FieldHelp = {
  key: 'cp',
  label: 'Chest Pain type (CP)',
  description:
    '0 = typical angina, 1 = atypical angina, 2 = non-anginal pain, 3 = asymptomatic. Not a 1–10 pain score.',
};

export const DDD_FIELDS: FieldHelp[] = [
  {
    key: 'pelvic_incidence',
    label: 'Pelvic incidence',
    description: 'Angle relating the sacrum to the femoral heads on this orthopedic table (not an MRI).',
  },
  {
    key: 'pelvic_tilt',
    label: 'Pelvic tilt',
    description: 'Orientation of the pelvis on this public biomechanical table.',
  },
  {
    key: 'lumbar_lordosis_angle',
    label: 'Lumbar lordosis angle',
    description: 'Lower-back curve angle on this table — not a symptom score.',
  },
  {
    key: 'sacral_slope',
    label: 'Sacral slope',
    description: 'Sacrum orientation relative to the horizontal on this table.',
  },
  {
    key: 'pelvic_radius',
    label: 'Pelvic radius',
    description: 'Distance measure of pelvic geometry on this table.',
  },
  {
    key: 'degree_spondylolisthesis',
    label: 'Degree of spondylolisthesis',
    description: 'Slip-grade number on this UCI table. Not a radiology DDD grade.',
  },
];

export const FIELD_GUIDES: Record<string, FieldHelp[]> = {
  wisconsin_reduced: WISCONSIN_REDUCED_FIELDS,
  ddd: DDD_FIELDS,
};

