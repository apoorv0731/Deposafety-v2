import React from 'react';
import { motion } from 'framer-motion';
import { Loader2 } from 'lucide-react';

// Animation variants
const buttonVariants = {
  initial: { scale: 1 },
  hover: { scale: 1.02 },
  tap: { scale: 0.98 },
  disabled: { opacity: 0.6 }
};

const loadingVariants = {
  animate: {
    rotate: 360,
    transition: {
      duration: 1,
      repeat: Infinity,
      ease: "linear"
    }
  }
};

// Premium Button Component
export const PremiumButton = ({ 
  children, 
  variant = 'primary', 
  size = 'md',
  loading = false,
  disabled = false,
  onClick,
  className = ''
}) => {
  const baseStyles = "relative overflow-hidden font-semibold rounded-lg transition-all duration-150 flex items-center justify-center gap-2";
  
  const variants = {
    primary: "bg-gradient-to-r from-blue-600 to-blue-700 text-white shadow-lg shadow-blue-500/30 hover:shadow-xl hover:shadow-blue-500/40 hover:from-blue-500 hover:to-blue-600",
    secondary: "bg-white text-gray-900 border-2 border-gray-200 hover:border-blue-500 hover:text-blue-600",
    ghost: "bg-transparent text-gray-600 hover:bg-gray-100 hover:text-gray-900",
    danger: "bg-gradient-to-r from-red-600 to-red-700 text-white shadow-lg shadow-red-500/30"
  };
  
  const sizes = {
    sm: "px-4 py-2 text-sm",
    md: "px-6 py-3 text-base",
    lg: "px-8 py-4 text-lg"
  };

  return (
    <motion.button
      variants={buttonVariants}
      initial="initial"
      whileHover={!disabled && !loading ? "hover" : undefined}
      whileTap={!disabled && !loading ? "tap" : undefined}
      disabled={disabled || loading}
      onClick={onClick}
      className={`${baseStyles} ${variants[variant]} ${sizes[size]} ${disabled ? 'opacity-60 cursor-not-allowed' : ''} ${className}`}
    >
      {loading && (
        <motion.span variants={loadingVariants} animate="animate">
          <Loader2 className="w-5 h-5" />
        </motion.span>
      )}
      <span className={loading ? 'opacity-80' : ''}>{children}</span>
      
      {/* Ripple effect on click */}
      {!disabled && !loading && (
        <motion.span
          className="absolute inset-0 bg-white/20"
          initial={{ scale: 0, opacity: 0 }}
          whileTap={{ scale: 2, opacity: 0 }}
          transition={{ duration: 0.4 }}
        />
      )}
    </motion.button>
  );
};

// Glass Card Component
export const GlassCard = ({ children, className = '', hover = true }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
      whileHover={hover ? { 
        y: -4,
        boxShadow: "0 20px 40px -10px rgba(0,0,0,0.15)"
      } : undefined}
      className={`
        bg-white/80 backdrop-blur-xl 
        border border-white/20 
        rounded-2xl 
        shadow-lg shadow-gray-200/50
        p-6
        ${className}
      `}
    >
      {children}
    </motion.div>
  );
};

// Animated Input Component
export const PremiumInput = ({ 
  label, 
  error, 
  icon: Icon,
  ...props 
}) => {
  return (
    <motion.div 
      className="relative"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
    >
      {label && (
        <motion.label 
          className="block text-sm font-medium text-gray-700 mb-2"
          initial={{ x: -10, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ delay: 0.1 }}
        >
          {label}
        </motion.label>
      )}
      
      <div className="relative">
        {Icon && (
          <Icon className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
        )}
        
        <motion.input
          className={`
            w-full 
            ${Icon ? 'pl-12' : 'pl-4'} pr-4 py-3
            bg-gray-50 border-2 border-gray-200 rounded-xl
            focus:bg-white focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10
            transition-all duration-200
            ${error ? 'border-red-500 focus:border-red-500 focus:ring-red-500/10' : ''}
          `}
          whileFocus={{ scale: 1.01 }}
          transition={{ type: "spring", stiffness: 300, damping: 20 }}
          {...props}
        />
        
        {/* Focus indicator line */}
        <motion.div
          className="absolute bottom-0 left-0 h-0.5 bg-blue-500"
          initial={{ width: 0 }}
          whileFocus={{ width: "100%" }}
          transition={{ duration: 0.2 }}
        />
      </div>
      
      {/* Error message */}
      {error && (
        <motion.p
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-2 text-sm text-red-600 flex items-center gap-1"
        >
          {error}
        </motion.p>
      )}
    </motion.div>
  );
};

// Loading Skeleton
export const Skeleton = ({ className = '' }) => {
  return (
    <motion.div
      className={`bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 bg-[length:200%_100%] rounded-lg ${className}`}
      animate={{
        backgroundPosition: ["200% 0", "-200% 0"]
      }}
      transition={{
        duration: 1.5,
        repeat: Infinity,
        ease: "linear"
      }}
    />
  );
};

// Success Animation
export const SuccessCheck = ({ show }) => {
  return (
    <motion.div
      initial={{ scale: 0 }}
      animate={show ? { scale: 1 } : { scale: 0 }}
      transition={{ type: "spring", stiffness: 500, damping: 30 }}
      className="w-16 h-16 bg-green-500 rounded-full flex items-center justify-center"
    >
      <motion.svg
        initial={{ pathLength: 0 }}
        animate={show ? { pathLength: 1 } : { pathLength: 0 }}
        className="w-8 h-8 text-white"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="3"
      >
        <motion.path
          d="M5 13l4 4L19 7"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </motion.svg>
    </motion.div>
  );
};

// Page Transition
export const PageTransition = ({ children }) => {
  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
    >
      {children}
    </motion.div>
  );
};

// Stagger Container
export const StaggerContainer = ({ children, className = '' }) => {
  return (
    <motion.div
      initial="hidden"
      animate="visible"
      variants={{
        hidden: { opacity: 0 },
        visible: {
          opacity: 1,
          transition: {
            staggerChildren: 0.1
          }
        }
      }}
      className={className}
    >
      {children}
    </motion.div>
  );
};

// Stagger Item
export const StaggerItem = ({ children, className = '' }) => {
  return (
    <motion.div
      variants={{
        hidden: { opacity: 0, y: 20 },
        visible: { 
          opacity: 1, 
          y: 0,
          transition: {
            type: "spring",
            stiffness: 100,
            damping: 15
          }
        }
      }}
      className={className}
    >
      {children}
    </motion.div>
  );
};
