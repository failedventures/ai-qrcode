import React from 'react';
import Typography from '@mui/material/Typography';
import Container from '@mui/material/Container';
import { Brush } from '@mui/icons-material';

export const Hero = () => {
  return (
    <Container
        maxWidth="md"
        sx={{padding: "10 0", textAlign: "center"}}>
      <Typography variant="h3" sx = {{ color: "white", fontWeight: 600 }}>
        AI-generated QR Codes 🔮
      </Typography>
    </Container>
  );
}
