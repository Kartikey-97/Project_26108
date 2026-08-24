import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import CompareStandardsTable from '../components/standards/CompareStandardsTable';
import { getStandard, toUiStandard } from '../services/api';

export default function Compare() {
  const [searchParams] = useSearchParams();
  const [standards, setStandards] = useState([]);
  useEffect(() => {
    const ids = searchParams.get('ids')?.split(',').filter(Boolean) || [];
    Promise.all(ids.map(getStandard)).then((items) => setStandards(items.map(toUiStandard))).catch(() => setStandards([]));
  }, [searchParams]);
  return <CompareStandardsTable initialStandards={standards} />;
}
