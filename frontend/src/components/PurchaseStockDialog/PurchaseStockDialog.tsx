import React, { useState } from 'react';
import {
  Checkbox,
  Dialog,
  DialogContent,
  TextField,
  Typography,
} from '@mui/material';
import { DialogHeader } from '@/components/DialogHeader';
import { DialogFooter } from '@/components/DialogFooter';
import { useBuyStock } from '@/api/buyStock.ts';
import './PurchaseStockDialog.scss';
import { OrderType } from '@/lib/enums.ts';

interface PurchaseStockDialogProps {
  isOpen: boolean;
  setIsOpen: React.Dispatch<React.SetStateAction<boolean>>;
  stockId: number;
  stockName: string;
  price: number;
}

export const PurchaseStockDialog = ({
  isOpen,
  setIsOpen,
  stockId,
  stockName,
  price,
}: PurchaseStockDialogProps) => {
  const buyStock = useBuyStock();
  const [isBuy, setIsBut] = useState(false);
  const [orderType, setOrderType] = useState<OrderType>(OrderType.MARKET);
  const [quantity, setQuantity] = useState(0);

  const handleSubmit = async () => {
    try {
      await buyStock.mutateAsync({
        stockId,
        isBuy,
        orderType,
        quantity,
        price,
      });
    } catch (e) {}
  };

  return (
    <Dialog
      open={isOpen}
      slotProps={{ paper: { className: 'purchase-stock-dialog' } }}
    >
      <DialogHeader title="Purchase stock" />
      <DialogContent>
        <div>
          <Checkbox></Checkbox>
        </div>

        <Typography variant="subtitle2">{`Stock: ${stockName}`}</Typography>
        {orderType == OrderType.LIMIT && <TextField label="Price"></TextField>}
        <TextField label="Quantity"></TextField>
      </DialogContent>
      <DialogFooter onSubmit={() => {}} onCancel={() => setIsOpen(false)} />
    </Dialog>
  );
};
