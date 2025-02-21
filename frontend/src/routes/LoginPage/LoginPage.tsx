import { useState, useEffect } from 'react';
import {
  Container,
  TextField,
  Button,
  Typography,
  Box,
  Snackbar,
  Alert,
} from '@mui/material';
import { SlideTransition } from '@/components/SlideTransition';
import { useNavigate, Link } from 'react-router-dom';
import { useLogin } from '@/api/login.ts';
import './LoginPage.scss';
import logo from '@/assets/logo.svg';

export function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();
  const login = useLogin({
    mutationConfig: {
      onSuccess: (data) => {
        localStorage.setItem('token', data.token);
        navigate('/');
      },
      onError: (error) => {
        setError(error.response?.data.detail ?? 'An unknown error occurred');
        setOpen(true);
      },
    },
  });

  const handleLogin = async () => {
    if (!username || !password) {
      setError('All fields must be filled out');
      setOpen(true);
      return;
    }
    try {
      await login.mutateAsync({ username, password });
    } catch (error) {}
  };

  useEffect(() => {
    const handleKeyPress = (event: KeyboardEvent) => {
      if (event.key === 'Enter') {
        handleLogin();
      }
    };

    window.addEventListener('keypress', handleKeyPress);
    return () => {
      window.removeEventListener('keypress', handleKeyPress);
    };
  }, [username, password]);

  return (
    <Container maxWidth="sm" className="login-page" style={{ marginBottom: '300px' }}>
      <Box display="flex" justifyContent="center" mb={4}>
        <img src={logo} alt="Stockii Logo" style={{ width: '500px' }} />
      </Box>
      <TextField
        label="Username"
        variant="outlined"
        fullWidth
        margin="normal"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
      />
      <TextField
        label="Password"
        type="password"
        variant="outlined"
        fullWidth
        margin="normal"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      <Box mt={2}>
        <Button
          variant="contained"
          color="primary"
          onClick={handleLogin}
          fullWidth
        >
          Login
        </Button>
      </Box>
      <Box mt={2}>
        <Typography variant="body2">
          Don't have an account? <Link to="/register">Register</Link>
        </Typography>
      </Box>
      <Snackbar
        open={open}
        autoHideDuration={6000}
        onClose={() => setOpen(false)}
        TransitionComponent={SlideTransition}
      >
        <Alert onClose={() => setOpen(false)} variant="filled" severity="error">
          {error}
        </Alert>
      </Snackbar>
    </Container>
  );
}
