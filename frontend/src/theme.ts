import { createTheme } from '@mui/material/styles';

const theme = (darkMode: boolean) =>
  createTheme({
    palette: {
      mode: darkMode ? 'dark' : 'light',
      primary: {
        main: '#6200ea', // Modern purple color
      },
      secondary: {
        main: '#03dac6', // Modern teal color
      },
      background: {
        default: darkMode ? '#121212' : '#f5f5f5', // Light gray background for light mode
      },
    },
    typography: {
      fontFamily: 'Roboto, Arial, sans-serif',
      h4: {
        fontWeight: 600,
      },
      body1: {
        fontSize: '1rem',
      },
    },
    components: {
      MuiButton: {
        styleOverrides: {
          root: {
            borderRadius: '8px',
            textTransform: 'none',
          },
        },
      },
      MuiTextField: {
        styleOverrides: {
          root: {
            borderRadius: '8px',
          },
        },
      },
      MuiDialogContent: {
        styleOverrides: {
          root: {
            padding: '0 16px 0 16px'
          }
        }
      }
    },
  });

export default theme;
