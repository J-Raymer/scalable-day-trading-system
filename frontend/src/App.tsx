import { useState, useEffect } from 'react';
import { ThemeProvider, CssBaseline, Toolbar, Box } from '@mui/material';
import { BrowserRouter as Router, Route, Routes, useLocation, useNavigate } from 'react-router-dom';
import LoginPage from './LoginPage';
import HomePage from './HomePage';
import RegisterPage from './RegisterPage';
import Header from './Header';
import Sidebar from './Sidebar';
import AccountPage from './AccountPage';
import TradePage from './TradePage';
import HistoryPage from './HistoryPage';
import theme from './theme';
import './App.css';
import { StocksPage } from './StocksPage.tsx';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient();


function App() {
  const [darkMode, setDarkMode] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme(darkMode)}>
        <CssBaseline />
        <Router>
          <AppContent darkMode={darkMode} setDarkMode={setDarkMode} mobileOpen={mobileOpen} handleDrawerToggle={handleDrawerToggle} />
        </Router>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

function AppContent({ darkMode, setDarkMode, mobileOpen, handleDrawerToggle }: { darkMode: boolean; setDarkMode: React.Dispatch<React.SetStateAction<boolean>>; mobileOpen: boolean; handleDrawerToggle: () => void }) {
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token && location.pathname !== '/register' && location.pathname !== '/login') {
      navigate('/login');
    }
  }, [navigate, location.pathname]);

  const isAuthPage = location.pathname === '/login' || location.pathname === '/register';

  return (
    <Box sx={{ display: 'flex' }}>
      <Header darkMode={darkMode} setDarkMode={setDarkMode} handleDrawerToggle={handleDrawerToggle} />
      {!isAuthPage && (
        <Sidebar mobileOpen={mobileOpen} handleDrawerToggle={handleDrawerToggle} />
      )}
      <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
        <Toolbar />
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/" element={<HomePage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/account" element={<AccountPage />} />
          <Route path="/trade" element={<TradePage />} />
          <Route path="/history" element={<HistoryPage />} />
          <Route path="/stocks" element={<StocksPage/>}/>
        </Routes>
      </Box>
    </Box>
  );
}

export default App;
