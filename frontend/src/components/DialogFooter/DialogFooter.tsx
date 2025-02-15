import React from 'react';
import { Button } from '@mui/material';
import './DialogFooter.scss';
import { ButtonColor } from '@/lib/enums.ts';

interface DialogFooterProps {
  onSubmit: () => void;
  onCancel: () => void;
  color?: ButtonColor;
}

export const DialogFooter = ({
  onSubmit,
  onCancel,
  color,
}: DialogFooterProps) => {
  return (
    <div className="dialog-footer">
      <Button variant="outlined" onClick={onCancel}>
        Cancel
      </Button>
      <Button
        variant="contained"
        onClick={onSubmit}
        color={color ?? ButtonColor.PRIMARY}
      >
        Submit
      </Button>
    </div>
  );
};
