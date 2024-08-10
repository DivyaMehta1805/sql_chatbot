import React, { useState } from 'react';
import { Container, Typography, Box, ThemeProvider, createTheme } from '@mui/material';
import { TextField, Button, InputAdornment } from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import { styled } from '@mui/system';
import Footer from './components/Footer';
import './App.css';

const theme = createTheme({
  palette: {
    primary: {
      main: '#002855',
    },
    secondary: {
      main: '#dc004e',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  },
});

const FancyTextField = styled(TextField)({
  '& .MuiOutlinedInput-root': {
    background: 'linear-gradient(45deg, #2c3e50 0%, #a3bcf6 90%)',
    borderRadius: 20,
    '& fieldset': {
      borderColor: 'rgba(255, 255, 255, 0.5)',
    },
    '&:hover fieldset': {
      borderColor: 'rgba(255, 255, 255, 0.7)',
    },
    '&.Mui-focused fieldset': {
      borderColor: '#ffffff',
    },
  },
  '& .MuiOutlinedInput-input': {
    color: 'white',
  },
  '& .MuiInputLabel-outlined': {
    color: 'rgba(255, 255, 255, 0.7)',
  },
  '&:hover .MuiInputLabel-outlined': {
    color: 'rgba(255, 255, 255, 0.9)',
  },
  '& .MuiInputLabel-outlined.Mui-focused': {
    color: '#ffffff',
  },
});

const GlowingButton = styled(Button)({
  background: 'linear-gradient(45deg, #53708d 30%, #496b8d 90%)',
  border: 0,
  borderRadius: 20,
  boxShadow: '0 3px 5px 2px rgba(33, 203, 243, .3)',
  color: 'white',
  height: 48,
  padding: '0 30px',
  '&:hover': {
    background: 'linear-gradient(45deg, #496b8d 30%, #6591bc 90%)',
    boxShadow: '0 3px 5px 2px rgba(33, 203, 243, .5)',
  },
});

function App() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [currentQuery, setCurrentQuery] = useState('');
  const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));
  const [currentAns,setCurrentAns]=useState('');
  const sendQueryToBackend = async (query) => {
    try {
      const response = await fetch('http://127.0.0.1:5000/api/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: query }),
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const data = await response.json();
      console.log('Response from backend:', data);
    } catch (error) {
      console.error('Error sending query to backend:', error);
      setError('An error occurred while sending the query to the backend.');
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    const query = currentQuery;
    if (!query.trim()) return;

    setLoading(true);
    setError('');

    try {
      setHistory(prevHistory => [
        ...prevHistory,
        { userQuery: query, botReply: 'Generating' }
      ]);
    
      await sendQueryToBackend(query);
    
      let newAnswer = null;
      let attempts = 0;
      const maxAttempts = 5;
      const delayBetweenAttempts = 4000; 
    
      while (attempts < maxAttempts) {
        const response = await fetch('http://127.0.0.1:5000/api/result', {
          method: 'GET',
        });
    
        if (!response.ok) {
          throw new Error('Failed to fetch SQL query');
        }
    
        const data = await response.json();
        console.log("data", data);
    
        if (data.response !== currentAns) {
          newAnswer = data.response.replace(/\\n/g, '\n');
          break;
        }
    
        await new Promise(resolve => setTimeout(resolve, delayBetweenAttempts));
        attempts++;
      }
    
      if (newAnswer) {
        setHistory(prevHistory => {
          const newHistory = [...prevHistory];
          newHistory[newHistory.length - 1].botReply = newAnswer;
          return newHistory;
        });
    
        setCurrentAns(newAnswer);
      } else {
        throw new Error('No new answer received after multiple attempts');
      }
    } catch (err) {
      setError('An error occurred while processing your query: ' + err.message);
    } finally {
      setLoading(false);
      setCurrentQuery('');
    }
  };


  return (
    <ThemeProvider theme={theme}>
      <Container maxWidth="md" className="App">
        <Box 
          sx={{
            border: '2px solid #002855', 
            borderRadius: '15px', 
            padding: '40px', 
            boxShadow: '0 4px 8px rgba(0, 0, 0, 0.2)', 
            backgroundColor: '#e3e3f3', 
            marginTop: '20px', 
            marginBottom: '20px',
          }}
        >
          <Box my={4}>
            <div className="title-container">
              <Typography variant="h2" component="h1" className="main-title">
SQL Based <span className="highlight">Chatbot</span>
              </Typography>
              <div className="underline"></div>
            </div>

            <Box className="chat-container" sx={{ maxWidth: '600px', margin: 'auto', padding: '20px' }}>
              {history.map((entry, index) => (
                <Box key={index} sx={{ marginBottom: '20px' }}>
                  <Box 
                    className="user-message"
                    sx={{
                      backgroundColor: '#a0c5ff',
                      borderRadius: '10px',
                      padding: '10px',
                      maxWidth: '70%',
                      boxShadow: '0 1px 2px rgba(0,0,0,0.1)',
                      marginBottom: '10px',
                    }}
                  >
                    <Typography variant="body1">{entry.userQuery}</Typography>
                  </Box>
                  <Box 
                    className="assistant-message"
                    sx={{
                      backgroundColor: '#DCF8F1',
                      borderRadius: '10px',
                      padding: '10px',
                      maxWidth: '70%',
                      marginLeft: 'auto',
                    }}
                  >
                    <Typography variant="body2" sx={{ fontFamily: 'monospace', whiteSpace: 'pre-wrap' }}>
                      {JSON.stringify(entry.botReply, null, 2)}
                    </Typography>
                  </Box>
                </Box>
              ))}
            </Box>

            <Box 
              sx={{
                backgroundColor: '#f0f0f0', 
                borderRadius: '10px',
                padding: '20px',
                boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
                marginTop: '20px',
              }}
            >
      <Box component="form" onSubmit={handleSubmit} sx={{ display: 'flex', alignItems: 'center' }}>
        <FancyTextField
          fullWidth
          variant="outlined"
          value={currentQuery}
          onChange={(e) => setCurrentQuery(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon sx={{ color: 'rgba(255, 255, 255, 0.7)' }} />
              </InputAdornment>
            ),
          }}
          InputLabelProps={{
            style: { color: '#a3bcf6' },
          }}
          sx={{ mr: 2 }}
          disabled={loading}
        />
        <GlowingButton type="submit" variant="contained" disabled={loading || !currentQuery.trim()}>
          {loading ? 'Generating...' : 'Generate SQL'}
        </GlowingButton>
      </Box>
           </Box>
          </Box>
        </Box>
        <Footer />
      </Container>
    </ThemeProvider>
  );
}

export default App;
