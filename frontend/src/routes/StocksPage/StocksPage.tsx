import React, { useState } from 'react';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import { useStockPrices, Stock } from '@/api/getStockPrices.ts';
import { Button, Typography } from '@mui/material';
import { PurchaseStockDialog } from '@/components/PurchaseStockDialog';
import './StocksPage.scss';

export const StocksPage = () => {
  const stocks = useStockPrices();
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
