import { useEffect, useState } from 'react';
import { Drawer, List, ListItem, ListItemIcon, ListItemText, Toolbar, IconButton, Box, useMediaQuery, useTheme } from '@mui/material';
import { Dashboard, AccountCircle, SwapHoriz, History, Close } from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';

const drawerWidth = 240;

interface SidebarProps {
  mobileOpen: boolean;
  handleDrawerToggle: () => void;
}

function Sidebar({ mobileOpen, handleDrawerToggle }: SidebarProps) {
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const [selectedIndex, setSelectedIndex] = useState(location.pathname);

  useEffect(() => {
    setSelectedIndex(location.pathname);
  }, [location.pathname]);

  const handleListItemClick = (path: string) => {
    setSelectedIndex(path);
    navigate(path);
    if (isMobile) {
      handleDrawerToggle();
    }
  };

  const drawer = (
    <div>
      <Toolbar>
        <IconButton onClick={handleDrawerToggle} sx={{ display: { xs: 'block', sm: 'none' } }}>
          <Close />
        </IconButton>
      </Toolbar>
      <List>
        {[
          { text: 'Dashboard', icon: <Dashboard />, path: '/' },
          { text: 'Account', icon: <AccountCircle />, path: '/account' },
          { text: 'Trade', icon: <SwapHoriz />, path: '/trade' },
          { text: 'History', icon: <History />, path: '/history' },
        ].map(({ text, icon, path }) => (
          <ListItem
            key={path}
            onClick={() => handleListItemClick(path)}
            sx={{
              cursor: 'pointer',
              backgroundColor: selectedIndex === path ? theme.palette.primary.light : 'inherit',
              color: selectedIndex === path ? theme.palette.primary.contrastText : 'inherit',
              '&:hover': {
                boxShadow: theme.palette.mode === 'dark' ? '0px 2px 4px rgba(255, 255, 255, 0.2)' : '0px 2px 4px rgba(0, 0, 0, 0.2)',
                border: `2px solid ${theme.palette.mode === 'dark' ? 'rgba(255, 255, 255, 0.2)' : 'rgba(0, 0, 0, 0.2)'}`,
              },
              '&.Mui-selected': {
                backgroundColor: theme.palette.primary.light,
                color: theme.palette.primary.contrastText,
                '&:hover': {
                  backgroundColor: theme.palette.primary.main,
                  boxShadow: theme.palette.mode === 'dark' ? '0px 2px 4px rgba(255, 255, 255, 0.2)' : '0px 2px 4px rgba(0, 0, 0, 0.2)',
                  border: `2px solid ${theme.palette.mode === 'dark' ? 'rgba(255, 255, 255, 0.2)' : 'rgba(0, 0, 0, 0.2)'}`,
                },
              },
            }}
          >
            <ListItemIcon sx={{ color: selectedIndex === path ? theme.palette.primary.contrastText : 'inherit' }}>
              {icon}
            </ListItemIcon>
            <ListItemText primary={text} />
          </ListItem>
        ))}
      </List>
    </div>
  );

  return (
    <Box component="nav" sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}>
      <Drawer
        variant="temporary"
        open={mobileOpen}
        onClose={handleDrawerToggle}
        ModalProps={{ keepMounted: true }}
        sx={{
          display: { xs: 'block', sm: 'none' },
          '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
        }}
      >
        {drawer}
      </Drawer>
      <Drawer
        variant="permanent"
        sx={{
          display: { xs: 'none', sm: 'block' },
          '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
        }}
        open
      >
        {drawer}
      </Drawer>
    </Box>
  );
}

export default Sidebar;
