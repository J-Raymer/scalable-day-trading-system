import { Container, Typography } from '@mui/material';
import './HomePage.scss';

export function HomePage() {
  return (
    <Container maxWidth="sm" sx={{ mt: 4 }} className="home-page">
      <Typography variant="h4" component="h1" gutterBottom>
        Welcome to the home page!
      </Typography>
    </Container>
  );
}
