import { useState } from 'react';
import { ThemeProvider, createTheme, CssBaseline, Box, IconButton } from '@mui/material';
import { Brightness4, Brightness7 } from '@mui/icons-material';
import LoginPage from './LoginPage';
import './App.css';

function App() {
  const [darkMode, setDarkMode] = useState(false);

  const theme = createTheme({
    palette: {
      mode: darkMode ? 'dark' : 'light',
      background: {
        default: darkMode ? '#121212' : '#ffffff',
      },
    },
  });

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ position: 'absolute', top: 16, right: 16 }}>
        <IconButton
          onClick={() => setDarkMode(!darkMode)}
          color="inherit"
        >
          {darkMode ? <Brightness7 /> : <Brightness4 />}
        </IconButton>
      </Box>
      <LoginPage />
    </ThemeProvider>
  );
}

export default App;
