import React, { useState } from 'react';
import {
  Typography,
  Card,
  CardContent,
  Button,
  Snackbar,
  Alert,
} from '@mui/material';
import { PortfolioItem, useStockPortfolio } from '@/api/getStockPortfolio';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import { Stock, useStockPrices } from '@/api/getStockPrices';
import { SlideTransition } from '@/components/SlideTransition';
import { PortfolioGrid } from '@/components/PortfolioGrid';
import { DashboardCard } from '@/components/DashboardCard/DashboardCard.tsx';
import { TransactionsGrid } from '@/components/TransactionsGrid';
import './TradePage.scss';

export function TradePage() {
  const stocks = useStockPrices();

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

  const stockColumns: GridColDef<Stock>[] = [
    { field: 'stock_id', headerName: 'id' },
    { field: 'stock_name', headerName: 'Name', flex: 60 },
    { field: 'price', headerName: 'Price' },
    {
      field: 'actions',
      headerName: 'Actions',
      flex: 25,
      renderCell: (params) => (
        <Button
          onClick={() => console.log(params.row.stock_id)}
          variant="contained"
        >
          View Stock
        </Button>
      ),
    },
  ];

  return (
    <div className="trade-page">
      <Typography variant="h2">My Stocks</Typography>
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
        <PortfolioGrid />
        <TransactionsGrid />


    </div>
  );
}
