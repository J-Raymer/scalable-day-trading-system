import React, { useState, useEffect } from 'react';
import React, { useState } from 'react';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import { useStockPrices, Stock } from '@/api/getStockPrices.ts';
import { Button, Typography, Snackbar, Alert, Slide } from '@mui/material';
import { Button, Typography } from '@mui/material';
import { PurchaseStockDialog } from '@/components/PurchaseStockDialog';
import './StocksPage.scss';

interface SlideTransitionProps {
  children: React.ReactElement;
  in: boolean;
  onEnter?: () => void;
  onExited?: () => void;
}

function SlideTransition(props: SlideTransitionProps) {
  return <Slide {...props} direction="up" />;
}

export const StocksPage = () => {
  const [error, setError] = useState<string | null>(null);
  const [open, setOpen] = useState(false);

  const handleError = (message: string) => {
    setError(message);
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
    setError(null);
  };

  const stocks = useStockPrices({
    queryConfig: {
      onError: (error) => {
        handleError(error.message);
      },
    },
  });
  const [currentStockName, setCurrentStockName] = useState<string | undefined>(
    undefined,
  );
  const [stockId, setStockId] = useState<number | undefined>(undefined);
  const [dialogOpen, setDialogOpen] = useState(false);

  const handleOpenDialog = (stockId: number, stockName: string) => {
    setCurrentStockName(stockName);
    setStockId(stockId);
    setDialogOpen(true);
  };

  const columns: GridColDef<Stock>[] = [
    { field: 'stock_id', headerName: 'id' },
    { field: 'stock_name', headerName: 'Name', flex: 60 },
    { field: 'price', headerName: 'Price' },
    {
      field: 'actions',
      headerName: 'Actions',
      flex: 15,
      renderCell: (params) => (
        <Button
          onClick={() =>
            handleOpenDialog(params.row.stock_id, params.row.stock_name)
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
      <Snackbar open={open} autoHideDuration={6000} onClose={handleClose} TransitionComponent={SlideTransition}>
        <Alert onClose={handleClose} variant="filled" severity="error">
          {error}
        </Alert>
      </Snackbar>
      <PurchaseStockDialog
        isOpen={dialogOpen}
        setIsOpen={setDialogOpen}
        stockId={stockId}
        stockName={currentStockName}
      />
      <DataGrid
        sx={{ width: 800 }}
        rows={stocks.data ?? []}
        columns={columns}
        getRowId={(row) => row.stock_id}
        disableRowSelectionOnClick
      />
    </div>
  );
};
