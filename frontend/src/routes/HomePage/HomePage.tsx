import { Container, Typography, Grid2, Card, CardContent } from '@mui/material';
import './HomePage.scss';
import { WalletCard } from '@/components/WalletCard';

export function HomePage() {
  return (
    <Container maxWidth="lg" sx={{ mt: 4 }} className="home-page">
      <Typography variant="h4" component="h1" gutterBottom>
        Dashboard
      </Typography>
      <Grid2 container spacing={3}>
        <Grid2 size={{ xs: 12, md: 6 }}>
          <WalletCard/>
        </Grid2>
        <Grid2 size={{ xs: 12, md: 6 }}>
          <Card>
            <CardContent>
              <Typography variant="h5" component="h2">
                Owned Stocks
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Owned stocks details go here.
              </Typography>
            </CardContent>
          </Card>
        </Grid2>
        <Grid2 size={{ xs: 12, md: 4 }}>
          <Card>
            <CardContent>
              <Typography variant="h5" component="h2">
                Stocks
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Stocks details go here.
              </Typography>
            </CardContent>
          </Card>
        </Grid2>
        <Grid2 size={{ xs: 12, md: 8 }}>
          <Card>
            <CardContent>
              <Typography variant="h5" component="h2">
                History
              </Typography>
              <Typography variant="body2" color="textSecondary">
                History details go here.
              </Typography>
            </CardContent>
          </Card>
        </Grid2>
      </Grid2>
    </Container>
  );
}
