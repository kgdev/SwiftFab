import React, { useState, useEffect } from 'react';
import { RollingNumberProps } from '../../types';

const RollingNumber: React.FC<RollingNumberProps> = ({ 
  value, 
  isAnimating, 
  prefix = '', 
  decimals = 2 
}) => {
  const [displayValue, setDisplayValue] = useState(value);
  const [isRolling, setIsRolling] = useState(false);

  useEffect(() => {
    if (isAnimating && value !== displayValue) {
      setIsRolling(true);
      
      // Animate to new value with faster duration
      const startValue = displayValue;
      const endValue = value;
      const duration = 500; // 0.5 seconds - faster animation
      const startTime = Date.now();

      const animate = () => {
        const elapsed = Date.now() - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // Easing function for smooth animation
        const easeOut = 1 - Math.pow(1 - progress, 3);
        
        const currentValue = startValue + (endValue - startValue) * easeOut;
        setDisplayValue(currentValue);

        if (progress < 1) {
          requestAnimationFrame(animate);
        } else {
          setDisplayValue(endValue);
          setIsRolling(false);
        }
      };

      requestAnimationFrame(animate);
    }
  }, [value, isAnimating, displayValue]);

  // Split the formatted value into individual characters for independent animation
  const formatValueWithDigits = (val: number) => {
    const formatted = val.toFixed(decimals);
    return formatted.split('');
  };

  const digits = formatValueWithDigits(displayValue);

  return (
    <span className={`inline-block transition-colors duration-200 ${isRolling ? 'text-green-600' : ''}`}>
      {prefix}
      {digits.map((digit, index) => (
        <span
          key={index}
          className={`inline-block transition-all duration-200 ${
            isRolling ? 'animate-pulse' : ''
          }`}
          style={{
            animationDelay: isRolling ? `${index * 50}ms` : '0ms',
          }}
        >
          {digit}
        </span>
      ))}
    </span>
  );
};

export default RollingNumber;
