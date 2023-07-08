import { Box, Button, Modal } from '@mui/material';
import DownloadIcon from '@mui/icons-material/Download';
import IconButton from '@mui/material/IconButton';
import ZoomInIcon from '@mui/icons-material/ZoomIn';
import { create } from 'zustand';
import './ImageComponent.css';

// Define your store
const useStore = create(set => ({
  isHovered: false,
  isModalOpen: false,
  setIsHovered: (value) => set({ isHovered: value }),
  openModal: () => set({ isModalOpen: true }),
  closeModal: () => set({ isModalOpen: false })
}));

export const ImageComponent = ({ image }) => {
  const { isHovered, isModalOpen, setIsHovered, openModal, closeModal } = useStore();

  const downloadImage = (href, filename) => {
    const link = document.createElement('a');
    link.href = href;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <Box
      className="imageContainer"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <Box
        component="img"
        src={image}
        alt="main image"
        className="image"
        sx={{
          display: 'block', mx: 'auto',
          maxWidth: "100%", maxHeight: "auto",
          objectFit: "contain"
        }}
      />
      {isHovered && (
        <Box className="buttons">
          <IconButton onClick={openModal} size="large">
            <ZoomInIcon className="buttonIcon" fontSize='30px' />
          </IconButton>
          <IconButton onClick={() => downloadImage(image, 'qrcode.png')} size="large">
            <DownloadIcon className="buttonIcon" fontSize='30px' />
          </IconButton>
          {/* <Button onClick={() => downloadImage(image, 'qrcode.png')}>
            <MdFileDownload />
          </Button> */}
        </Box>
      )}
      <Modal
        open={isModalOpen}
        onClose={closeModal}
      >
        <Box className="modalContent">
          <img src={image} alt="Zoomed" />
        </Box>
      </Modal>
    </Box>
  );
};
