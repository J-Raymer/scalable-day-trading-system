import { useState, useEffect } from 'react';
import { Container, Typography, Snackbar, Alert, Slide } from '@mui/material';
import { SlideTransition } from '@/components/SlideTransition';
import './AccountPage.scss';

export function AccountPage() {
  const [error, setError] = useState<string | null>(null);
  const [open, setOpen] = useState(false);

  const handleClose = () => {
    setOpen(false);
    setError(null);
  };

  return (
    <Container maxWidth="sm" sx={{ mt: 4 }} className="account-page">
      <Typography variant="h4" component="h1" gutterBottom>
        Account Page
      </Typography>
      <Snackbar
        open={open}
        autoHideDuration={6000}
        onClose={handleClose}
        TransitionComponent={SlideTransition}
      >
        <Alert onClose={handleClose} variant="filled" severity="error">
          {error}
        </Alert>
      </Snackbar>
      {/* Add account details and other content here */}
    </Container>
  );
}
