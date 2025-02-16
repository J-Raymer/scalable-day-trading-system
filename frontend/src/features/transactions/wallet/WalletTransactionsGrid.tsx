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
  console.log(transactions.data);

  const columns: GridColDef<WalletTransaction>[] = [
    { field: 'stock_tx_id', headerName: 'Stock Tx Id', flex: 10 },
    { field: 'wallet_tx_id', headerName: 'Wallet Tx Id', flex: 10 },
    { field: 'is_debit', headerName: 'Is Debit', flex: 5 },
    { field: 'amount', headerName: 'Amount', flex: 5 },
    { field: 'time_stamp', headerName: 'Timestamp', flex: 30 },
  ];

  const placeHolderData: WalletTransaction[] = [
    // TODO: Replace this with real data when engine complete
    // TODO: How should we format the timestamp?
    {
      stock_tx_id: 1,
      wallet_tx_id: 1,
      is_debit: true,
      amount: 100,
      time_stamp: new Date('2023-10-01T10:00:00Z'),
    },
    {
      stock_tx_id: 2,
      wallet_tx_id: 2,
      is_debit: false,
      amount: 200,
      time_stamp: new Date('2023-10-01T10:00:00Z'),
    },
  ];

  return (
    <DashboardCard>
      <Typography variant="h5">Wallet Transactions</Typography>
      <DataGrid
        columns={columns}
        rows={placeHolderData}
        getRowId={(row) => row.wallet_tx_id}
        disableRowSelectionOnClick
      />
    </DashboardCard>
  );
};
