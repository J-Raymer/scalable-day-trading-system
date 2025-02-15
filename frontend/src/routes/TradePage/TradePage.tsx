import React from 'react';
import { Typography, Button, Snackbar, Alert } from '@mui/material';
import { PortfolioGrid } from '@/components/PortfolioGrid';
import { TransactionsGrid } from '@/components/TransactionsGrid';
import './TradePage.scss';

export function TradePage() {
  return (
    <div className="trade-page">
      <Typography variant="h2">My Stocks</Typography>
      <PortfolioGrid />
      <TransactionsGrid />
    </div>
  );
}
