import React from 'react';
import { SlideProps } from '@mui/material/Slide';
import { Slide } from '@mui/material';

export const SlideTransition = (props: SlideProps) => {
  return <Slide {...props} direction="up" />;
};
