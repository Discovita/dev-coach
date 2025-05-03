import React from 'react';

export const UserMessage: React.FC<
  React.PropsWithChildren<React.HTMLAttributes<HTMLDivElement>>
> = ({ children, ...props }) => (
  <div
    className="_UserMessage mb-4 p-3.5 pr-4 pl-4 rounded-t-[18px] rounded-bl-[18px] rounded-br-[6px] max-w-[75%] leading-[1.5] animate-fadeIn break-words ml-auto bg-gold-600 text-gold-50 border-b-[4px] border-b-primary-color shadow-gold-sm"
    {...props}
  >
    {children}
  </div>
);
