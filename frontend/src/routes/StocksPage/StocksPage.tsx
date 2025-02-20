import React, { useState } from 'react';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import { useStockPrices, Stock } from '@/api/getStockPrices.ts';
import { Button, Typography, Snackbar, Alert, Slide } from '@mui/material';
import { SlideTransition } from '@/components/SlideTransition';
import { PurchaseStockDialog } from '@/features/transactions/stock/PurchaseStockDialog';
import './StocksPage.scss';
import { DashboardCard } from '@/components/DashboardCard/DashboardCard';

export const StocksPage = () => {
  const stocks = useStockPrices();

  const [error, setError] = useState<string | null>(null);
  const [open, setOpen] = useState(false);
  const [currentStockName, setCurrentStockName] = useState<string | undefined>(
    undefined,
  );
  const [currentStockId, setCurrentStockId] = useState<number | undefined>(
    undefined,
  );
  const [currentPrice, setCurrentPrice] = useState<number | undefined>(
    undefined,
  );
  const [dialogOpen, setDialogOpen] = useState(false);

  const handleClose = () => {
    setOpen(false);
    setError(null);
  };

  const handleOpenDialog = (
    stockId: number,
    stockName: string,
    price: number,
  ) => {
    setCurrentStockName(stockName);
    setCurrentStockId(stockId);
    setCurrentPrice(price);
    setDialogOpen(true);
  };

  const columns: GridColDef<Stock>[] = [
    { field: 'stock_id', headerName: 'id' },
    { field: 'stock_name', headerName: 'Name', flex: 60 },
    { field: 'current_price', headerName: 'Current Price' },
    {
      field: 'actions',
      headerName: 'Actions',
      flex: 15,
      renderCell: (params) => (
        <Button
          onClick={() =>
            handleOpenDialog(
              params.row.stock_id,
              params.row.stock_name,
              params.row.current_price,
            )
          }
          variant="contained"
        >
          Purchase
        </Button>
      ),
    },
  ];

  return (
    <div className="stocks-page">
      <Typography variant="h2">Stocks</Typography>
      <DashboardCard>
      <Snackbar
        open={open}
        autoHideDuration={6000}
        onClose={handleClose}
        TransitionComponent={SlideTransition}
      >
        <Alert onClose={handleClose} variant="filled" severity="error">
          {error}
        </Alert>
      </Snackbar>
      <PurchaseStockDialog
        isOpen={dialogOpen}
        setIsOpen={setDialogOpen}
        stockId={currentStockId}
        stockName={currentStockName ?? ''}
        price={currentPrice}
      />
      <DataGrid
        sx={{ width: 800 }}
        rows={stocks.data ?? []}
        columns={columns}
        getRowId={(row) => row.stock_id}
        disableRowSelectionOnClick
      />
      </DashboardCard>
    </div>
    
  );
};
