import { Container, Typography } from '@mui/material';
import './TradePage.scss';

export function TradePage() {
  return (
    <Container maxWidth="sm" sx={{ mt: 4 }} className="trade-page">
      <Typography variant="h4" component="h1" gutterBottom>
        Trade Page
      </Typography>
    </Container>
  );
}
