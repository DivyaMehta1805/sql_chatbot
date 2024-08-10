import React from 'react';
import { Box, Typography } from '@mui/material';
import './Footer.css';

function Footer() {
  return (
    <Box component="footer" className="footer-container">
      <Typography variant="body2" className="footer-text">
        {new Date().getFullYear()} Divya Mehta
      </Typography>
    </Box>
  );
}

export default Footer;
