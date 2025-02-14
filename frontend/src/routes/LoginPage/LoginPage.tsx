import { useState, useEffect } from 'react';
import axios from 'axios';
import {
  Container,
  TextField,
  Button,
  Typography,
  Box,
  Snackbar,
  Alert,
  Slide,
} from '@mui/material';
import { SlideTransition } from '@/components/SlideTransition';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import './LoginPage.scss';

export function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    if (location.state?.registered) {
      setSuccess(true);
      setOpen(true);
    }
  }, [location]);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username || !password) {
      setError('All fields must be filled out');
      setOpen(true);
      return;
    }

    try {
      const response = await axios.post(
        'http://localhost:3001/authentication/login',
        {
          user_name: username,
          password,
        },
      );
      if (response.status === 200) {
        console.log(
          'User logged in successfully, token saved in local storage',
        );
        const token = response.data.data.token;
        localStorage.setItem('token', token);
        navigate('/');
      }
    } catch (err) {
      if (axios.isAxiosError(err)) {
        if (err.response && err.response.status === 404) {
          setError('User not found');
        } else if (err.response && err.response.status === 401) {
          setError('Unauthorized');
        } else {
          setError('Login failed. Please try again.');
        }
      } else {
        setError('An unexpected error occurred.');
      }
      setOpen(true);
    }
  };

  const handleClose = () => {
    setOpen(false);
    setSuccess(false);
  };

  return (
    <Container maxWidth="sm" className="login-page">
      <Typography variant="h4" component="h1" gutterBottom>
        Login
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
      <Snackbar
        open={success}
        autoHideDuration={6000}
        onClose={handleClose}
        TransitionComponent={SlideTransition}
      >
        <Alert onClose={handleClose} variant="filled" severity="success">
          Registered successfully, please login
        </Alert>
      </Snackbar>
      <form
        className="login-form"
        noValidate
        autoComplete="off"
        onSubmit={handleLogin}
      >
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
          <Button variant="contained" color="primary" type="submit" fullWidth>
            Login
          </Button>
        </Box>
        <Box mt={2}>
          <Typography variant="body2">
            Don't have an account? <Link to="/register">Register</Link>
          </Typography>
        </Box>
      </form>
    </Container>
  );
}

export default LoginPage;
