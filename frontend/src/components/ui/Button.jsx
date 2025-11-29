/**
 * Button Component
 *
 * Variants: primary, secondary, outline, ghost
 * Sizes: sm, md, lg
 */
import { forwardRef } from 'react';
import './Button.css';

const Button = forwardRef(({
  children,
  variant = 'primary',
  size = 'md',
  fullWidth = false,
  disabled = false,
  loading = false,
  leftIcon = null,
  rightIcon = null,
  as: Component = 'button',
  className = '',
  ...props
}, ref) => {
  const classes = [
    'spv-btn',
    `spv-btn--${variant}`,
    `spv-btn--${size}`,
    fullWidth && 'spv-btn--full-width',
    loading && 'spv-btn--loading',
    className
  ].filter(Boolean).join(' ');

  return (
    <Component
      ref={ref}
      className={classes}
      disabled={disabled || loading}
      {...props}
    >
      {loading && (
        <span className="spv-btn__spinner" aria-hidden="true">
          <svg className="spv-btn__spinner-icon" viewBox="0 0 24 24">
            <circle
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="3"
              fill="none"
              strokeLinecap="round"
            />
          </svg>
        </span>
      )}
      {!loading && leftIcon && <span className="spv-btn__icon">{leftIcon}</span>}
      <span className="spv-btn__text">{children}</span>
      {!loading && rightIcon && <span className="spv-btn__icon">{rightIcon}</span>}
    </Component>
  );
});

Button.displayName = 'Button';

export { Button };
