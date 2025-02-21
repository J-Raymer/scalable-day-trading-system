import { useState } from 'react';
import { Typography, Snackbar, Alert } from '@mui/material';
import { SlideTransition } from '@/components/SlideTransition';
import { WalletTransactionsGrid } from '@/features/transactions/wallet';
import { StockTransactionsGrid } from '@/features/transactions/stock/StockTransactionsGrid';
import './HistoryPage.scss';

export function HistoryPage() {
  const [error, setError] = useState<string | null>(null);
  const [open, setOpen] = useState(false);

  const handleClose = () => {
    setOpen(false);
    setError(null);
  };

  return (
    <div className="history-page">
      <Typography variant="h4" component="h1" gutterBottom>
        History
      </Typography>
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
      <WalletTransactionsGrid />
      <StockTransactionsGrid />
    </div>
  );
}
