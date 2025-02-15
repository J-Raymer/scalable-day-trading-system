import { useState } from 'react';
import { Typography, Card, CardContent, Button, Snackbar, Alert } from '@mui/material';
import { useStockPortfolio } from '@/api/getStockPortfolio';
import './TradePage.scss';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import { Stock, useStockPrices } from '@/api/getStockPrices';
import { SlideTransition } from '@/components/SlideTransition';




export function TradePage() {
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


  const stocks = useStockPrices();
  // uncomment this after user has been setup to have stocks
  // const stocks = useStockPortfolio();
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
          View Stock
        </Button>
      ),
    },
  ];

  return (
    <div className="trade-page">
      <Typography variant="h2">My Stocks</Typography>
      <Snackbar open={open} autoHideDuration={6000} onClose={handleClose} TransitionComponent={SlideTransition}>
        <Alert onClose={handleClose} variant="filled" severity="error">
          {error}
        </Alert>
      </Snackbar>
      <DataGrid
        sx={{ width: 800 }}
        rows={stocks.data ?? []}
        columns={columns}
        getRowId={(row) => row.stock_id}
        disableRowSelectionOnClick
      />
      <Card sx={{ mt: 2 }}>
        <CardContent>
          {/* placeholder for pending transactions, we will need to be able to see the status of sell limit orders and cancell them here */}
          <Typography variant="h5" component="h2">
            Pending Transactions
          </Typography>
          <DataGrid
            sx={{ width: 800 }}
            rows={stocks.data ?? []}
            columns={columns}
            getRowId={(row) => row.stock_id}
            disableRowSelectionOnClick
          />
        </CardContent>
      </Card>
    </div>
  );
};
