import { Container, Typography, Card, CardContent, Button } from '@mui/material';
import { useStockPortfolio } from '@/api/getStockPortfolio';
import './TradePage.scss';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import { Stock, useStockPrices } from '@/api/getStockPrices';

export function TradePage() {
  // const stocks = useStockPrices();
  const stocks = useStockPortfolio();
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
        rows={stocks.data?? []}
        columns={columns}
        getRowId={(row) => row.stock_id}
        disableRowSelectionOnClick
      />
    </div>
  );
};
