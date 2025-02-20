import React from 'react';
import { DashboardCard } from '@/components/DashboardCard/DashboardCard.tsx';
import { Typography } from '@mui/material';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import {
  useWalletTransactions,
  WalletTransaction,
} from '@/api/getWalletTransactions.ts';

export const WalletTransactionsGrid = () => {
  const transactions = useWalletTransactions();

  const columns: GridColDef<WalletTransaction>[] = [
    { field: 'stock_tx_id', headerName: 'Stock Tx Id', flex: 10 },
    { field: 'wallet_tx_id', headerName: 'Wallet Tx Id', flex: 10 },
    { field: 'is_debit', headerName: 'Is Debit', flex: 5 },
    { field: 'amount', headerName: 'Amount', flex: 5 },
    { field: 'time_stamp', headerName: 'Timestamp', flex: 30 },
  ];

  return (
    <DashboardCard>
      <Typography variant="h5">Wallet Transactions</Typography>
      <DataGrid
        columns={columns}
        rows={transactions.data ?? []}
        getRowId={(row) => row.wallet_tx_id}
        disableRowSelectionOnClick
      />
    </DashboardCard>
  );
};
