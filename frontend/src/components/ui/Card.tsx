import React from 'react';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  title?: string;
  icon?: React.ReactNode;
}

const Card: React.FC<CardProps> = ({ children, className = '', title, icon }) => {
  return (
    <div className={`bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 p-8 ${className}`}>
      {title && (
        <div className="flex items-center mb-6">
          {icon && (
            <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-xl flex items-center justify-center mr-4">
              {icon}
            </div>
          )}
          <h2 className="text-2xl font-bold text-gray-900">{title}</h2>
        </div>
      )}
      {children}
    </div>
  );
};

export default Card;
