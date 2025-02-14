import React from 'react';
import { Button } from '@mui/material';
import './DialogFooter.scss';

interface DialogFooterProps {
  onSubmit: () => void;
  onCancel: () => void;
}

export const DialogFooter = ({ onSubmit, onCancel }: DialogFooterProps) => {
  return <div className="dialog-footer">
    <Button variant="outlined" onClick={onCancel}>Cancel</Button>
    <Button variant="contained" onClick={onSubmit}>Submit</Button>

  </div>;
};
