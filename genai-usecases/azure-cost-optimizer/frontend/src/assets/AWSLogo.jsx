import { Box } from '@mui/material';
import awsPng from './aws.png';

const AWSLogo = ({ width = 24, height = 20 }) => {
  return (
    <Box
      component="img"
      src={awsPng}
      alt="AWS Logo"
      sx={{
        width: width,
        height: height,
        display: 'inline-block',
        verticalAlign: 'middle',
        objectFit: 'contain',
      }}
    />
  );
};

export default AWSLogo;
