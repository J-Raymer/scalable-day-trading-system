import React, { ReactNode } from 'react';
import { Card, CardContent } from '@mui/material';
import './DashboardCard.scss';

interface DashboardCardProps {
  children: ReactNode;
}

export const DashboardCard = ({ children }: DashboardCardProps) => {
  return (
    <Card>
      <CardContent>{children}</CardContent>
    </Card>
  );
};
