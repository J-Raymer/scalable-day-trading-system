import { useState } from 'react';
import {
  Container,
  TextField,
  Button,
  Typography,
  Box,
  Snackbar,
  Alert,
} from '@mui/material';
import { useNavigate, Link } from 'react-router-dom';
import { SlideTransition } from '@/components/SlideTransition';
import { useRegister } from '@/api/register.ts';
import './RegisterPage.scss';
import { AxiosError } from 'axios';

export function RegisterPage() {
  const [name, setName] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();
  const register = useRegister({
    mutationConfig: {
      onSuccess: (data) => {
        localStorage.setItem('token', data.token);
        navigate('/');
      },
      onError: (error) => {
        // setError(error.response?.data.detail);
        // setOpen(true);
      },
    },
  });
  const handleRegister = async () => {
    if (!name || !username || !password || !confirmPassword) {
      setError('All fields must be filled out');
      setOpen(true);
      return;
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      setOpen(true);
      return;
    }
    await register.mutateAsync({ username, name, password });
  };

  const handleClose = () => {
    setOpen(false);
  };

  return (
    <Container maxWidth="sm" className="register-page">
      <Typography variant="h4" component="h1" gutterBottom>
        Register
      </Typography>
      <TextField
        label="Name"
        variant="outlined"
        fullWidth
        margin="normal"
        value={name}
        onChange={(e) => setName(e.target.value)}
      />
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
      <TextField
        label="Confirm Password"
        type="password"
        variant="outlined"
        fullWidth
        margin="normal"
        value={confirmPassword}
        onChange={(e) => setConfirmPassword(e.target.value)}
      />
      {error && (
        <Typography color="error" variant="body2">
          {error}
        </Typography>
      )}
      <Box mt={2}>
        <Button
          variant="contained"
          color="primary"
          type="submit"
          fullWidth
          onClick={handleRegister}
        >
          Register
        </Button>
      </Box>
      <Box mt={2}>
        <Typography variant="body2">
          Already have an account? <Link to="/login">Login</Link>
        </Typography>
      </Box>
    </Container>
  );
}
