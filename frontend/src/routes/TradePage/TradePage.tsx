import React from 'react';
import { Typography, Button, Snackbar, Alert } from '@mui/material';
import { PortfolioGrid } from '@/features/portfolio/PortfolioGrid';
import { StockTransactionsGrid } from '@/features/transactions/stock/StockTransactionsGrid';
import './TradePage.scss';

export function TradePage() {
  return (
    <div className="trade-page">
      <Typography variant="h2">My Stocks</Typography>
      <PortfolioGrid />
      <StockTransactionsGrid />
    </div>
  );
}
