import { Container, Typography } from '@mui/material';

export function HomePage() {
  return (
    <Container maxWidth="sm" sx={{ mt: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Welcome to the home page!
      </Typography>
    </Container>
  );
}

