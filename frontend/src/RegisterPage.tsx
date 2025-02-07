import { useState } from 'react';
import axios from 'axios';
import { Container, TextField, Button, Typography, Box } from '@mui/material';
import { useNavigate } from 'react-router-dom';

function RegisterPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username) {
      setError('Username cannot be empty');
      return;
    }
    if (/\s|[^a-zA-Z0-9]/.test(username)) {
      setError('Username cannot contain spaces or special characters');
      return;
    }
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    if (!password || !confirmPassword) {
      setError('All fields must be filled out');
      return;
    }
    try {
      const response = await axios.post('http://localhost:8000/register', {
        username,
        password,
      });
      if (response.status === 201) {
        console.log("User registered successfully");
        navigate('/login');
      }
    } catch (err) {
      if (err.response && err.response.status === 409) {
        setError('Username already exists');
      } else {
        setError('Registration failed. Please try again.');
      }
    }
  };

  return (
    <Container maxWidth="sm">
      <Typography variant="h4" component="h1" gutterBottom>
        Register
      </Typography>
      <form className="register-form" noValidate autoComplete="off" onSubmit={handleRegister}>
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
          <Button variant="contained" color="primary" type="submit" fullWidth>
            Register
          </Button>
        </Box>
      </form>
    </Container>
  );
}

export default RegisterPage;
