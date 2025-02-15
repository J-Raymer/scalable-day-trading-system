import React, { useState } from 'react';
import { DashboardCard } from '@/components/DashboardCard/DashboardCard.tsx';
import { Button, Typography } from '@mui/material';
import {
  StockTransactions,
  useStockTransactions,
} from '@/api/getStockTransactions.ts';
import { ButtonColor, OrderStatus, OrderType } from '@/lib/enums.ts';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import { CancelOrderDialog } from '@/components/CancelOrderDialog';

export const TransactionsGrid = () => {
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

  // TODO: Replace this with real data when engine complete
  const placeHolderData: StockTransactions[] = [
    {
      stock_tx_id: 123,
      stock_id: 1,
      wallet_tx_id: 456,
      order_status: OrderStatus.PARTIALLY_COMPLETE,
      is_buy: true,
      order_type: OrderType.LIMIT,
      stock_price: 150,
      quantity: 10,
      parent_tx_id: 789,
      time_stamp: new Date('2023-10-01T10:00:00Z'),
      user_id: 'U001',
    },
    {
      stock_tx_id: 124,
      stock_id: 2,
      wallet_tx_id: 457,
      order_status: OrderStatus.IN_PROGRESS,
      is_buy: false,
      order_type: OrderType.LIMIT,
      stock_price: 250,
      quantity: 20,
      parent_tx_id: 790,
      time_stamp: new Date('2023-10-02T11:00:00Z'),
      user_id: 'U002',
    },
    {
      stock_tx_id: 125,
      stock_id: 3,
      wallet_tx_id: 458,
      order_status: OrderStatus.COMPLETED,
      is_buy: true,
      order_type: OrderType.MARKET,
      stock_price: 350,
      quantity: 30,
      parent_tx_id: 791,
      time_stamp: new Date('2023-10-03T12:00:00Z'),
      user_id: 'U003',
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
        <Typography variant="h5">Transactions</Typography>
        <DataGrid
          columns={columns}
          rows={placeHolderData}
          getRowId={(row) => row.stock_id}
          disableRowSelectionOnClick
        />
      </DashboardCard>
    </>
  );
};
