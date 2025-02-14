import { useState } from 'react';
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
import { useNavigate, Link } from 'react-router-dom';
import { SlideTransition } from '@/components/SlideTransition';
import './RegisterPage.scss';

export function RegisterPage() {
  const [name, setName] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
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

    try {
      const response = await axios.post(
        'http://localhost:3001/authentication/register',
        {
          name,
          user_name: username,
          password,
        },
      );
      if (response.status === 201) {
        console.log('User registered successfully');
        navigate('/login', { state: { registered: true } });
      }
    } catch (err) {
      if (axios.isAxiosError(err)) {
        if (err.response && err.response.status === 409) {
          setError('User already exists');
        } else {
          setError('Registration failed. Please try again.');
        }
      } else {
        setError('An unexpected error occurred.');
      }
      setOpen(true);
    }
  };

  const handleClose = () => {
    setOpen(false);
  };

  return (
    <Container maxWidth="sm" className="register-page">
      <Typography variant="h4" component="h1" gutterBottom>
        Register
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
      <form
        className="register-form"
        noValidate
        autoComplete="off"
        onSubmit={handleRegister}
      >
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
        <Box mt={2}>
          <Button variant="contained" color="primary" type="submit" fullWidth>
            Register
          </Button>
        </Box>
        <Box mt={2}>
          <Typography variant="body2">
            Already have an account? <Link to="/login">Login</Link>
          </Typography>
        </Box>
      </form>
    </Container>
  );
}

export default RegisterPage;
