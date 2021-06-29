import React from 'react';
import ReactDOM from 'react-dom';
import CssBaseline from '@material-ui/core/CssBaseline';
import { ThemeProvider } from '@material-ui/core/styles';
import { SnackbarProvider } from 'notistack';

import './index.scss';
import App from './App';
import theme from './theme';

ReactDOM.render(
  <ThemeProvider theme={theme}>
    <CssBaseline />
    <SnackbarProvider>
      <App />
    </SnackbarProvider>
  </ThemeProvider>,
  document.getElementById('root'),
);
