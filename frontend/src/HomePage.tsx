import { Container, Typography } from '@mui/material';

function HomePage() {
  return (
    <Container maxWidth="sm">
      <Typography variant="h4" component="h1" gutterBottom>
        Home Page
      </Typography>
      <Typography variant="body1">
        Welcome to the home page!
      </Typography>
    </Container>
  );
}

export default HomePage;
