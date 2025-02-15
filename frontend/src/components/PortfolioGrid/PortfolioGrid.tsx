import { DashboardCard } from '@/components/DashboardCard/DashboardCard.tsx';
import { Typography } from '@mui/material';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import React from 'react';
import { PortfolioItem, useStockPortfolio } from '@/api/getStockPortfolio.ts';

export const PortfolioGrid = () => {
  const portolio = useStockPortfolio();

  const columns: GridColDef<PortfolioItem>[] = [
    { field: 'stock_id', headerName: 'id' },
    { field: 'stock_name', headerName: 'Name', flex: 60 },
    { field: 'quantity_owned', headerName: 'Quantity Owned', flex: 30 },
  ];

  // TODO: Need to update this when real data is available
  const placeholderData: PortfolioItem[] = [
    { stock_id: 1, stock_name: 'AAPL', quantity_owned: 150 },
    { stock_id: 2, stock_name: 'GOOGL', quantity_owned: 2800 },
    { stock_id: 3, stock_name: 'AMZN', quantity_owned: 3400 },
  ];

  return (
    <DashboardCard className="portfolio-grid">
      <Typography variant="h5">Stock Portfolio</Typography>
      <DataGrid
        columns={columns}
        rows={placeholderData}
        getRowId={(row) => row.stock_id}
      />
    </DashboardCard>
  );
};
