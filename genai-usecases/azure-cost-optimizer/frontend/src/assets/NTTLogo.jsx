import { Box } from '@mui/material';
import nttLogoPng from './logo_new.png';

const NTTLogo = ({ width = 40, height = 40 }) => {
  return (
    <Box
      component="img"
      src={nttLogoPng}
      alt="NTT Logo"
      sx={{
        width: width,
        height: height,
        display: 'block',
        objectFit: 'contain',
      }}
    />
  );
};

export default NTTLogo;
