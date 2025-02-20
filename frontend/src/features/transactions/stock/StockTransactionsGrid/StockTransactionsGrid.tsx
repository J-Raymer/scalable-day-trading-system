import React, { useState } from 'react';
import { DashboardCard } from '@/components/DashboardCard/DashboardCard.tsx';
import { Button, Typography } from '@mui/material';
import {
  StockTransactions,
  useStockTransactions,
} from '@/api/getStockTransactions.ts';
import { ButtonColor, OrderStatus, OrderType } from '@/lib/enums.ts';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import { CancelOrderDialog } from '@/features/transactions/stock/CancelOrderDialog';

export const StockTransactionsGrid = () => {
  const transactions = useStockTransactions();
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [currentTxId, setCurrentTxId] = useState<number | undefined>();

  const handleOpenDialog = (stockTxId: number) => {
    setCurrentTxId(stockTxId);
    setIsDialogOpen(true);
  };

  const columns: GridColDef<StockTransactions>[] = [
    { field: 'stock_tx_id', headerName: 'id', width: 1 },
    { field: 'order_status', headerName: 'Order Status', flex: 15 },
    { field: 'order_type', headerName: 'Order Type', flex: 10 },
    { field: 'stock_price', headerName: 'Price', flex: 5 },
    { field: 'quantity', headerName: 'Quantity', flex: 10 },
    { field: 'is_buy', headerName: 'Is Buy Order', flex: 10 },
    {
      field: 'actions',
      headerName: 'Actions',
      flex: 10,
      renderCell: (params) => {
        return (
          params.row.order_status !== OrderStatus.COMPLETED &&
          params.row.order_type == OrderType.LIMIT && (
            <Button
              variant="contained"
              color={ButtonColor.ERROR}
              onClick={() => handleOpenDialog(params.row.stock_tx_id)}
            >
              Cancel order
            </Button>
          )
        );
      },
    },
  ];

  return (
    <>
      <CancelOrderDialog
        isOpen={isDialogOpen}
        setIsOpen={setIsDialogOpen}
        stockTxId={currentTxId}
        setCurrentId={setCurrentTxId}
      />
      <DashboardCard>
        <Typography variant="h5">Stock Transactions</Typography>
        <DataGrid
          columns={columns}
          rows={transactions.data?? []}
          getRowId={(row) => row.stock_id}
          disableRowSelectionOnClick
        />
      </DashboardCard>
    </>
  );
};
