import React from 'react';
import './DialogHeader.scss';
import { Typography } from '@mui/material';


interface DialogHeaderProps {
  title: string;
}

export const DialogHeader = ({ title }: DialogHeaderProps) => {
  return (
    <div className="dialog-header">
      <Typography>{title}</Typography>
    </div>
  );
};
