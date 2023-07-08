// App.js
import React, {useEffect} from 'react';
import { create } from 'zustand';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';
import qrcode from './qrcode.png';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import { CssBaseline } from '@mui/material';
import CircularProgress from '@mui/material/CircularProgress';
import './App.css';
import { ImageComponent } from './ImageComponent.js';
import axios from 'axios';
import {EmailCollectionModal} from './EmailCollectionModal.js';
import { Hero } from './Hero';
import FingerprintJS from '@fingerprintjs/fingerprintjs';


const BASE_API_URL = "http://localhost:8000";
const QRCODE_GEN_PATH = "/qrcode";

var fakeMainImage = qrcode;
const fakeImages = [qrcode, qrcode, qrcode, qrcode, qrcode, qrcode];


// Zustand store holds all the state for the app
const useStore = create((set) => ({
  // Form
  qrContent: '',
  setQrContent: (content) => set({ qrContent: content }),
  prompt: '',
  setPrompt: (prompt) => set({ prompt: prompt }),
  loading: false,
  setLoading: (loading) => set({ loading: loading }),
  email: '',
  setEmail: (email) => set({ email: email }),

  // Images
  images: fakeImages,
  setImages: (images) => set({ images: images }),
  mainImage: fakeMainImage,
  setMainImage: (mainImage) => set({ mainImage: mainImage }),

  // Browser fingerprint
  visitorId: null,
  setVisitorId: id => set({ visitorId: id }),
}));

// Make all API calls to the backend through axios
let axios_handler = axios.create({
  baseURL: BASE_API_URL,
  headers: {
    'Content-Type': 'application/json',
    'Visitor-Id': useStore.getState().visitorId,
  },
})
axios_handler.interceptors.request.use(function (config) {
  const visitorId = useStore.getState().visitorId;
  config.headers['Visitor-Id'] = visitorId;
  return config;
});

function App() {
  const visitorId = useStore(state => state.visitorId);
  const setVisitorId = useStore(state => state.setVisitorId);

  useEffect(() => {
    FingerprintJS.load()
      .then(fp => fp.get())
      .then(result => {
        // This is the visitor identifier:
        const visitorId = result.visitorId;
        setVisitorId(visitorId);
        console.log("Visitor ID:", visitorId);
      })
  }, [setVisitorId]);


  return (
    <>
      <CssBaseline />
        <NavBar />
        <MainPage />
    </>
  );
}

// For now, keep all components in one file. We may split them
//
// TODOs:
// - [ ] Add history of QR codes generated
export function NavBar() {
  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="sticky" sx={{background: "black"}}>
        <Toolbar>
          <Box className="logo" display="flex">
            {/* <IconButton edge="start" color="inherit" aria-label="logo">
              <LogoIcon />
            </IconButton> */}
            <Typography component="span" variant="h4" sx={{ fontWeight: 800 }}>QR<Typography component="span" variant="h4">Artist</Typography>
            </Typography>
          </Box>
        </Toolbar>
      </AppBar>
    </Box>
  );
}



export const MainPage = () => {
  const qrContent = useStore(state => state.qrContent);
  const setQrContent = useStore(state => state.setQrContent);
  const prompt = useStore(state => state.prompt);
  const setPrompt = useStore(state => state.setPrompt);
  const images = useStore(state => state.images);
  const mainImage = useStore(state => state.mainImage);
  const setMainImage = useStore(state => state.setMainImage);
  const loading = useStore(state => state.loading);
  const setLoading = useStore(state => state.setLoading);

  return (
    <Grid
      container
      id="main-page"
      className="gradient-background"
      sx = {{justifyContent: "center", height: "100vh"}}>
      <Hero />
      <Grid
        container
        spacing={3}
        sx={{ marginTop: 8, maxWidth: 1132, justifyContent: "center",
              background: "white",  borderRadius: "30px", "mb": 10,
              height: "fit-content", padding: 3}}>
        <Grid item xs={12} sm={7}
          sx={{justifyContent: "center"}}>
          <Box
            component="form"
            sx={{display: "flex", flexDirection: "column",
                 justifyContent: "top", alignItems: "stretch",
                 height: "100%", width: "100%"}}>
            <Typography variant="h5" sx={{mb: 2}}>Parameters</Typography>
            <TextField
              required
              id="qr-content"
              label="QR Code Content"
              value={qrContent}
              onChange={(e) => setQrContent(e.target.value)}
              sx = {{mb: 2}}
            />
            <TextField
              required
              id="prompt"
              label="Prompt"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              sx = {{mb: 2}}
              multiline
              rows={2}
            />
            <Button
              variant="contained"
              onClick={() => {
                setLoading(true);
                var resp = generateQrCode(qrContent, prompt);
                resp.then(response => {
                  const blob = new Blob([response.data], {type: 'image/png'});
                  const image = URL.createObjectURL(blob);
                  setMainImage(image);
                  setLoading(false); // Set loading to false after response is received
                })
                .catch(error => {
                  console.error("Error generating QR code:", error);
                  setLoading(false); // Set loading to false after response is received
                });}}
              disabled={loading}
              className='gradient-background-rainbow'
              sx = {{mb: 2}}>
              {loading ? <CircularProgress size={24} sx = {{ color: 'white' }}/> : 'Generate'}
            </Button>
          </Box>
        </Grid>
        <Grid
          item
          xs={12} sm={5}
          sx = {{width: "100%", height: "auto"}}>
          <ImageComponent image={mainImage}/>
          {/* <ImageList cols={4} sx={{ width: "100%", height: "auto"}} >
            {images.map((item) => (
              <ImageListItem key={item.img}>
                <img
                  src={`${item}?w=164&h=164&fit=crop&auto=format`}
                  srcSet={`${item}?w=164&h=164&fit=crop&auto=format&dpr=2 2x`}
                  alt={item.title}
                  loading="lazy"
                  style={{objectFit: "contain"}}
                />
              </ImageListItem>
            ))}
          </ImageList> */}
        </Grid>
      </Grid>
      <EmailCollectionModal />
    </Grid>
  );
}

function generateQrCode(qrContent, prompt) {
  // Set the request body
  const data = {
    qrcode_content: qrContent,
    prompt: prompt
  };
  // Send a POST request to the API
  return axios_handler.post(QRCODE_GEN_PATH, data, {responseType: 'blob'});
}



export default App;
