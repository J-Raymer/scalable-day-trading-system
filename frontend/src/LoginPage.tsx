import { useState } from 'react';
import { Container, TextField, Button, Typography } from '@mui/material';

function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = () => {
    // Add login logic here
    console.log('Logging in with', { username, password });
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
      </form>
    </Container>
  );
}

export default LoginPage;
