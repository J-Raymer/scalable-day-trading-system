import { Container, Typography } from '@mui/material';
import './HistoryPage.scss';

export function HistoryPage() {
  return (
    <Container maxWidth="sm" sx={{ mt: 4 }} className="history-page">
      <Typography variant="h4" component="h1" gutterBottom>
        History Page
      </Typography>
    </Container>
  );
}
