import { Container, Typography, Card, CardContent } from '@mui/material';
import './HistoryPage.scss';

export function HistoryPage() {
  return (
    <Container maxWidth="sm" sx={{ mt: 4 }} className="history-page">
      <Typography variant="h4" component="h1" gutterBottom>
        History
      </Typography>
      <Card sx={{ mt: 2 }}>
        <CardContent>
          <Typography variant="h5" component="h2">
            Wallet Transactions
          </Typography>
          {/* Add wallet transactions content here */}
        </CardContent>
      </Card>
      <Card sx={{ mt: 2 }}>
        <CardContent>
          <Typography variant="h5" component="h2">
            Stock Transactions
          </Typography>
          {/* Add stock transactions content here */}
        </CardContent>
      </Card>
    </Container>
  );
}
