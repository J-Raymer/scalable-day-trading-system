import { DashboardCard } from '@/components/DashboardCard/DashboardCard.tsx';
import { Typography, Button } from '@mui/material';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import React, { useState } from 'react';
import { PortfolioItem, useStockPortfolio } from '@/api/getStockPortfolio.ts';
import { SellStockDialog } from '@/features/transactions/stock/SellStockDialog';

export const PortfolioGrid = () => {
  const portolio = useStockPortfolio();
  const [currentStockId, setCurrentStockId] = useState<number | undefined>(
    undefined,
  );
  const [isDialogOpen, setIsDialogOpen] = useState(false);

  const handleOpenDialog = (stockId: number) => {
    setCurrentStockId(stockId);
    setIsDialogOpen(true);
  };

  const columns: GridColDef<PortfolioItem>[] = [
    { field: 'stock_id', headerName: 'Stock ID' },
    { field: 'stock_name', headerName: 'Name', flex: 60 },
    { field: 'quantity_owned', headerName: 'Quantity Owned', flex: 30 },
    {
      field: 'actions',
      headerName: 'Actions',
      flex: 20,
      renderCell: (params) => {
        return (
          <Button
            variant="contained"
            onClick={() => handleOpenDialog(params.row.stock_id)}
          >
            Sell Stock
          </Button>
        );
      },
    },
  ];

  return (
    <>
      <SellStockDialog
        isOpen={isDialogOpen}
        setIsOpen={setIsDialogOpen}
        stockId={currentStockId}
        setCurrentId={setCurrentStockId}
      />
      <DashboardCard className="portfolio-grid">
        <Typography variant="h5">Stock Portfolio</Typography>
        <DataGrid
          columns={columns}
          rows={portolio.data?? []}
          getRowId={(row) => row.stock_id}
          disableRowSelectionOnClick
        />
      </DashboardCard>
    </>
  );
};
