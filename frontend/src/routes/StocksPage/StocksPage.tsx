import React from 'react';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import { useGetStocks, Stock } from '@/api/getStocks.ts';
import { Button, Typography } from '@mui/material';
import './StocksPage.scss';

export const StocksPage = () => {
  const stocks = useGetStocks();

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
          onClick={() => console.log(params.row.stock_id)}
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
      <DataGrid
        sx={{ width: 800 }}
        rows={stocks.data?.data ?? []}
        columns={columns}
        getRowId={(row) => row.stock_id}
        disableRowSelectionOnClick
      />
    </div>
  );
};
