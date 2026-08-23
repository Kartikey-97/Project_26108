import React from 'react';
import CompareStandardsTable from '../components/standards/CompareStandardsTable';
import { MOCK_COMPARISON_MATRIX } from '../data/mockData';

export default function Compare() {
  return <CompareStandardsTable initialStandards={MOCK_COMPARISON_MATRIX} />;
}
