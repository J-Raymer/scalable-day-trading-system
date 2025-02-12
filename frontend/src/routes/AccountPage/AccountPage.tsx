import { Container, Typography } from '@mui/material';
import './AccountPage.scss';

export function AccountPage() {
  return (
    <Container maxWidth="sm" sx={{ mt: 4 }} className="account-page">
      <Typography variant="h4" component="h1" gutterBottom>
        Account Page
      </Typography>
    </Container>
  );
}
