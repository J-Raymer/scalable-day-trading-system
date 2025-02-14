import { useState, useEffect } from 'react';
import { ThemeProvider, CssBaseline, Toolbar, Box } from '@mui/material';
import {
  BrowserRouter as Router,
  Route,
  Routes,
  useLocation,
  useNavigate,
} from 'react-router-dom';
import { Header } from '@/components/Header';
import { Sidebar } from '@/components/SideBar';
import theme from './theme';
import { AccountPage } from '@/routes/AccountPage';
import { HistoryPage } from '@/routes/HistoryPage';
import { HomePage } from '@/routes/HomePage';
import { LoginPage } from '@/routes/LoginPage';
import { RegisterPage } from '@/routes/RegisterPage';
import { StocksPage } from '@/routes/StocksPage';
import { TradePage } from '@/routes/TradePage';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import setupAxiosInterceptors from './axiosSetup';
import './App.css';

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
          <AppContent
            darkMode={darkMode}
            setDarkMode={setDarkMode}
            mobileOpen={mobileOpen}
            handleDrawerToggle={handleDrawerToggle}
          />
        </Router>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

function AppContent({
  darkMode,
  setDarkMode,
  mobileOpen,
  handleDrawerToggle,
}: {
  darkMode: boolean;
  setDarkMode: React.Dispatch<React.SetStateAction<boolean>>;
  mobileOpen: boolean;
  handleDrawerToggle: () => void;
}) {
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    setupAxiosInterceptors(navigate);
  }, [navigate]);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (
      !token &&
      location.pathname !== '/register' &&
      location.pathname !== '/login'
    ) {
      navigate('/login');
    }
  }, [navigate, location.pathname]);

  const isAuthPage =
    location.pathname === '/login' || location.pathname === '/register';

  return (
    <Box sx={{ display: 'flex' }}>
      <Header
        darkMode={darkMode}
        setDarkMode={setDarkMode}
        handleDrawerToggle={handleDrawerToggle}
      />
      {!isAuthPage && (
        <Sidebar
          mobileOpen={mobileOpen}
          handleDrawerToggle={handleDrawerToggle}
        />
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
          <Route path="/stocks" element={<StocksPage />} />
        </Routes>
      </Box>
    </Box>
  );
}

export default App;
