import { Box } from '@mui/material';
import azureSvg from './azure-1.svg';

const AzureLogo = ({ width = 20, height = 20 }) => {
  return (
    <Box
      component="img"
      src={azureSvg}
      alt="Azure Logo"
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

export default AzureLogo;
