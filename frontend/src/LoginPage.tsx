import { useState } from 'react';
import axios from 'axios';
import { Container, TextField, Button, Typography, Box } from '@mui/material';
import { useNavigate, Link } from 'react-router-dom';

function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username || !password) {
      setError('All fields must be filled out');
      return;
    }

    // Bypass for login for testing purposes
    if (username === 'test' && password === 'test') {
      const fakeToken = 'fake-jwt-token';
      localStorage.setItem('token', fakeToken);
      navigate('/');
      return;
    }

    try {
      const response = await axios.post('http://localhost:3001/authentication/login', {
        user_name: username,
        password,
      });
      if (response.status === 200) {
        console.log("User logged in successfully, token saved in local storage");
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
    }
  };

  return (
    <Container maxWidth="sm">
      <Typography variant="h4" component="h1" gutterBottom>
        Login
      </Typography>
      <form className="login-form" noValidate autoComplete="off" onSubmit={handleLogin}>
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
        {error && (
          <Typography color="error" variant="body2">
            {error}
          </Typography>
        )}
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
