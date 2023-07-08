import React from 'react';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import { create } from 'zustand';
import Box from '@mui/material/Box';

const useStore = create(set => ({
  open: false,
  setOpen: newValue => set({ open: newValue }),
  email: '',
  setEmail: newValue => set({ email: newValue })
}));

export const EmailCollectionModal = () => {
  const open = useStore(state => state.open);
  const setOpen = useStore(state => state.setOpen);
  const email = useStore(state => state.email);
  const setEmail = useStore(state => state.setEmail);

  const handleClose = () => {
    setOpen(false);
  };

  const handleSubmit = () => {
    console.log(email);
    alert("Success! Follow the link sent in your email!");
  };

  return (
    <Box >
      <Dialog
        open={open}
        onClose={handleClose}
        aria-labelledby="alert-dialog-title"
        aria-describedby="alert-dialog-description"
        PaperProps={{ style: { borderRadius: 10, padding: 8,
                               flexDirection: "column", spacing: 2,
                               alignContent: "space-evenly", alignItems: "center",
                               justifyContent: "center"} }}
      >
        <DialogTitle id="alert-dialog-title">{"Welcome to QRArtist 👨‍🎨"}</DialogTitle>
        <DialogContent>
          <DialogContentText id="alert-dialog-description">
            Hey there 👋! Looks like you're enjoying QRArtist 🎨! You've spent all your free generations but you can get two more by registering with your email!
          </DialogContentText>
          <TextField
            autoFocus
            margin="dense"
            id="name"
            label="Email Address"
            type="email"
            fullWidth
            variant="standard"
            value={email}
            onChange={e => setEmail(e.target.value)}
          />
        </DialogContent>
        <Button variant="contained" onClick={handleSubmit} sx={{ width: "fit-content" }} color="primary">
          Submit
        </Button>
      </Dialog>
    </Box>
  );
}
