import React from 'react';
import { useParams } from 'react-router-dom';
import StandardDetailsContent from '../components/standards/StandardDetailsContent';
import { MOCK_STANDARD_DETAIL_SINGLE } from '../data/mockData';

export default function StandardDetails() {
  const { id } = useParams();

  const detailData = {
    ...MOCK_STANDARD_DETAIL_SINGLE,
    standardCode: id ? decodeURIComponent(id) : MOCK_STANDARD_DETAIL_SINGLE.standardCode
  };

  return <StandardDetailsContent detail={detailData} />;
}
