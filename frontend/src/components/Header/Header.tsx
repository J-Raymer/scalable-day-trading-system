import { AppBar, Toolbar, IconButton, Button, Box } from '@mui/material';
import { Brightness4, Brightness7, Menu } from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import './Header.scss';

interface HeaderProps {
  darkMode: boolean;
  setDarkMode: (mode: boolean) => void;
  handleDrawerToggle: () => void;
}

export function Header({ darkMode, setDarkMode, handleDrawerToggle }: HeaderProps) {
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    // Clear token from localStorage
    localStorage.removeItem('token');
    console.log('Logging out');
    // Redirect to login page after logout
    navigate('/login');
  };

  return (
    <AppBar
      position="fixed"
      sx={{
        backgroundColor: darkMode ? '#333' : '#fff',
        color: darkMode ? '#fff' : '#000',
        boxShadow: '0px 2px 4px rgba(0, 0, 0, 0.1)',
      }}
    >
      <Toolbar>
        <IconButton
          color="inherit"
          aria-label="open drawer"
          edge="start"
          onClick={handleDrawerToggle}
          sx={{ display: { sm: 'none' }, mr: 2 }}
        >
          <Menu />
        </IconButton>
        <Box sx={{ flexGrow: 1 }} />
        {(location.pathname !== '/login' && location.pathname !== '/register') && (
          <Button color="inherit" onClick={handleLogout}>
            Logout
          </Button>
        )}
        <IconButton
          onClick={() => setDarkMode(!darkMode)}
          color="inherit"
        >
          {darkMode ? <Brightness7 /> : <Brightness4 />}
        </IconButton>
      </Toolbar>
    </AppBar>
  );
}

