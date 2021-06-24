import React, { useState, useEffect } from 'react';
import Container from '@material-ui/core/Container';
import Typography from '@material-ui/core/Typography';
import { makeStyles } from '@material-ui/core/styles';
import Toolbar from '@material-ui/core/Toolbar';
import Tooltip from '@material-ui/core/Tooltip';
import Button from '@material-ui/core/Button';
import CssBaseline from '@material-ui/core/CssBaseline';
import Menu from '@material-ui/core/Menu';
import Grid from '@material-ui/core/Grid';
import Paper from '@material-ui/core/Paper';
import TextField from '@material-ui/core/TextField';
import AppBar from '@material-ui/core/AppBar';
import MenuItem from '@material-ui/core/MenuItem';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import Box from '@material-ui/core/Box';
import Plot from 'react-plotly.js';
import axios from 'axios';
import { useSnackbar } from 'notistack';

import './App.scss';
import Copyright from './components/copyright';
import { NETWORK_LABELS } from './constants';

const useStyles = makeStyles((theme) => ({
  appBarSpacer: theme.mixins.toolbar,
  container: {
    paddingTop: theme.spacing(4),
    paddingBottom: theme.spacing(4),
  },
  paper: {
    padding: theme.spacing(2),
    display: 'flex',
    overflow: 'auto',
    flexDirection: 'column',
  },
  language: {
    margin: theme.spacing(0, 0.5, 0, 1),
    display: 'none',
    [theme.breakpoints.up('md')]: {
      display: 'block',
    },
  },
}));

const App = () => {
  const [walletData, setWalletData] = useState({ items: [] });
  const [networkMenuAnchor, setNetworkMenuAnchor] = useState();
  const [selectedNetwork, setSelectedNetwork] = useState('Ethereum');
  const [selectedWallet, setSelectedWallet] = useState();
  const [isLoading, setIsLoading] = useState();
  // eslint-disable-next-line no-unused-vars
  const { enqueueSnackbar, closeSnackbar } = useSnackbar();
  const classes = useStyles();

  const pieChartData = [
    {
      values: walletData.items.map((item) => item.holdings[0].close.quote),
      labels: walletData.items.map((item) => item.contract_name),
      type: 'pie',
    },
  ];

  const lineChartData = walletData.items.map((item) => ({
    type: 'scatter',
    mode: 'lines',
    name: item.contract_name,
    x: item.holdings.map((holding) => holding.timestamp),
    y: item.holdings.map((holding) => holding.close.quote),
  }));

  const handleNetworkMenuClose = (event) => {
    // check that user click inside menu
    if (event.currentTarget.nodeName === 'A') {
      setSelectedNetwork(event.currentTarget.text);
      setNetworkMenuAnchor(null);
    }
  };

  const hasData = walletData.items.length;

  const handleNetworkIconClick = (event) => {
    setNetworkMenuAnchor(event.currentTarget);
  };

  useEffect(() => {
    const fetchData = async () => {
      if (selectedWallet) {
        setIsLoading(true);
        const selectedNetworkCode = NETWORK_LABELS.filter((network) => network.text === selectedNetwork)[0].code;
        try {
          const result = await axios.get(
            `${process.env.REACT_APP_API_BASE}/api/asset-allocation/${selectedNetworkCode}/${selectedWallet}/`,
          );
          setWalletData(result.data);
        } catch (error) {
          enqueueSnackbar(error.response.statusText, { persist: false, variant: 'error' });
          setSelectedWallet();
        } finally {
          setIsLoading(false);
        }
      }
    };

    fetchData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedNetwork, selectedWallet]);

  const handleWalletChange = (event) => {
    setSelectedWallet(event.target.value);
  };

  return (
    <div className="root">
      <CssBaseline />
      <AppBar position="fixed" className="appbar">
        <Toolbar className="toolbar">
          <img src="https://www.covalenthq.com/static/images/covalent-logo-tri.svg" className="logo" alt="covalent" />
          <Tooltip title={selectedNetwork} enterDelay={300}>
            <Button color="inherit" aria-haspopup="true" onClick={handleNetworkIconClick}>
              <span className={classes.language}>{selectedNetwork}</span>
              <ExpandMoreIcon fontSize="small" />
            </Button>
          </Tooltip>
          <Menu
            id="network-menu"
            anchorEl={networkMenuAnchor}
            open={Boolean(networkMenuAnchor)}
            onClose={handleNetworkMenuClose}
          >
            {NETWORK_LABELS.map((network) => (
              <MenuItem
                component="a"
                data-no-link="true"
                key={network.code}
                selected={selectedNetwork === network.text}
                onClick={handleNetworkMenuClose}
              >
                {network.text}
              </MenuItem>
            ))}
          </Menu>
        </Toolbar>
      </AppBar>
      <main className={`content bg ${!hasData && 'bg--loading'}`}>
        {!isLoading && !hasData && (
          <>
            <div className={classes.appBarSpacer} />
            <Container maxWidth="lg" className={classes.container}>
              <Grid container spacing={0} alignItems="center" justify="center" style={{ minHeight: '60vh' }}>
                {/* Input wallet address */}
                <Grid item xs={12} md={10} lg={8}>
                  <Paper className={classes.paper}>
                    <TextField
                      onChange={handleWalletChange}
                      id="outlined-basic"
                      label="Enter your account address..."
                      variant="outlined"
                    />
                  </Paper>
                </Grid>
              </Grid>
              <Box pt={4}>
                <Copyright />
              </Box>
            </Container>
          </>
        )}
        {isLoading && (
          <div className="loader">
            <img
              src="https://www.covalenthq.com/static/images/cqtscan/covalent-logo-loop_dark_v2.gif"
              alt="Loading..."
            />
          </div>
        )}
        {!isLoading && hasData && (
          <>
            <div className={classes.appBarSpacer} />
            <Container maxWidth="lg" className={classes.container}>
              <Grid container spacing={3}>
                {/* Asset Allocation */}
                <Grid item xs={12} md={8} lg={9}>
                  <Paper className={classes.paper}>
                    <Typography component="h2" variant="h6" color="primary" gutterBottom>
                      Asset Allocation
                    </Typography>
                    <Plot data={pieChartData} config={{ displaylogo: false }} />
                  </Paper>
                </Grid>
                {/* Total value */}
                <Grid item xs={12} md={4} lg={3}>
                  <Paper className={classes.paper}>
                    <Typography component="h2" variant="h6" color="primary" gutterBottom>
                      Total value
                    </Typography>
                    <Typography component="p" variant="h4">
                      {walletData.items.reduce((total, item) => total + item.holdings[0].close.quote, 0).toFixed(2)} $
                    </Typography>
                    <Typography color="textSecondary" className="">
                      on {new Date().toDateString()}
                    </Typography>
                  </Paper>
                </Grid>
                {/* Asset Value Over Time */}
                <Grid item xs={12}>
                  <Paper className={classes.paper}>
                    <Typography component="h2" variant="h6" color="primary" gutterBottom>
                      Asset Value Over Time
                    </Typography>
                    <Plot data={lineChartData} config={{ displaylogo: false }} />
                  </Paper>
                </Grid>
              </Grid>
              <Box pt={4}>
                <Copyright />
              </Box>
            </Container>
          </>
        )}
      </main>
    </div>
  );
};

export default App;
