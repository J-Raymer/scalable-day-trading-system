import { useState } from 'react';
import { Container, TextField, Button, Typography, Box } from '@mui/material';
import { useNavigate } from 'react-router-dom';

function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const handleLogin = () => {
    // Add login logic here
    console.log('Logging in with', { username, password });
    // Redirect to home page after login
    navigate('/home');
  };

  const handleRegister = () => {
    navigate('/register');
  };

  return (
    <Container maxWidth="sm">
      <Typography variant="h4" component="h1" gutterBottom>
        Login
      </Typography>
      <form className="login-form" noValidate autoComplete="off">
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
        <Button variant="contained" color="primary" onClick={handleLogin} fullWidth>
          Login
        </Button>
        <Box mt={2}>
          <Button
            variant="outlined"
            color="primary"
            onClick={handleRegister}
            fullWidth
            sx={{
              backgroundColor: 'background.default',
              color: 'primary.main',
              borderColor: 'primary.main',
              '&:hover': {
                backgroundColor: 'background.default',
                borderColor: 'primary.dark',
                color: 'primary.dark',
              },
            }}
          >
            Register
          </Button>
        </Box>
      </form>
    </Container>
  );
}

export default LoginPage;
