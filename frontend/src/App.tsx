import { useState, useEffect } from 'react';
import { ThemeProvider, CssBaseline, Toolbar } from '@mui/material';
import { BrowserRouter as Router, Route, Routes, useLocation, useNavigate } from 'react-router-dom';
import LoginPage from './LoginPage';
import HomePage from './HomePage';
import RegisterPage from './RegisterPage';
import Header from './Header';
import theme from './theme';
import './App.css';

function App() {
  const [darkMode, setDarkMode] = useState(false);

  return (
    <ThemeProvider theme={theme(darkMode)}>
      <CssBaseline />
      <Router>
        <AppContent darkMode={darkMode} setDarkMode={setDarkMode} />
      </Router>
    </ThemeProvider>
  );
}

function AppContent({ darkMode, setDarkMode }: { darkMode: boolean; setDarkMode: React.Dispatch<React.SetStateAction<boolean>> }) {
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token && location.pathname !== '/register' && location.pathname !== '/login') {
      navigate('/login');
    }
  }, [navigate, location.pathname]);

  return (
    <>
      <Header darkMode={darkMode} setDarkMode={setDarkMode} />
      <Toolbar />
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/" element={<HomePage />} />
        <Route path="/register" element={<RegisterPage />} />
      </Routes>
    </>
  );
}

export default App;
