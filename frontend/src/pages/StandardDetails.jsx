import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import StandardDetailsContent from '../components/standards/StandardDetailsContent';
import { getStandard, toUiStandard } from '../services/api';

export default function StandardDetails() {
  const { id } = useParams();

  const [detailData, setDetailData] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    getStandard(id).then((standard) => setDetailData(toUiStandard(standard))).catch((err) => setError(err.message));
  }, [id]);

  if (error) return <p className="text-sm text-red-600">{error}</p>;
  if (!detailData) return <p className="text-sm text-gray-500">Loading standard…</p>;

  return <StandardDetailsContent detail={detailData} />;
}
