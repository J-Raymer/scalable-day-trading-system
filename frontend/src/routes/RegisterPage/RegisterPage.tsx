import { useState } from 'react';
import { Container, TextField, Button, Typography, Box } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useRegister } from '@/api/register';
import './RegisterPage.scss';

export function RegisterPage() {
  const [username, setUsername] = useState('');
  const [name, setName] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const register = useRegister({
    mutationConfig: {
      onSuccess: (data) => {
        localStorage.setItem('token', data.token);
        navigate('/');
      },
    },
  });
  /*React Hook Form with zod is really good when working with a lot of fields
   * https://react-hook-form.com/
   * https://zod.dev/
   * */
  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username) {
      setError('Username cannot be empty');
      return;
    }
    if (!name) {
      setError('Name cannot be empty');
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
      await register.mutateAsync({ username, password, name });
    } catch (err) {
      setError(err.response.data.detail);
    }
  };

  return (
    <Container maxWidth="sm" className="register-page">
      <Typography variant="h4" component="h1" gutterBottom>
        Register
      </Typography>
      <form
        className="register-form"
        noValidate
        autoComplete="off"
        onSubmit={handleRegister}
      >
        <TextField
          label="Username"
          variant="outlined"
          fullWidth
          required
          margin="normal"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <TextField
          label="Name"
          fullWidth
          required
          margin="normal"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
        <TextField
          label="Password"
          type="password"
          variant="outlined"
          fullWidth
          required
          margin="normal"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <TextField
          label="Confirm Password"
          type="password"
          variant="outlined"
          fullWidth
          required
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
