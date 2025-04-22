import React, { createContext, useContext, useState, useEffect } from 'react';

type ThemeType = 'light' | 'dark' | 'system';

interface ThemeContextType {
  theme: ThemeType;
  isDark: boolean;
  setTheme: (theme: ThemeType) => void;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  // Get initial theme from localStorage or default to 'system'
  const getInitialTheme = (): ThemeType => {
    const savedTheme = localStorage.getItem('theme') as ThemeType;
    return savedTheme || 'system';
  };

  const [theme, setThemeState] = useState<ThemeType>(getInitialTheme);
  
  // Determine if dark mode is active
  const [isDark, setIsDark] = useState<boolean>(false);

  // Update the theme in localStorage and apply it to the document
  const setTheme = (newTheme: ThemeType) => {
    localStorage.setItem('theme', newTheme);
    setThemeState(newTheme);
  };

  // Toggle between light and dark themes
  const toggleTheme = () => {
    setTheme(isDark ? 'light' : 'dark');
  };

  // Apply the theme to the document
  useEffect(() => {
    const applyTheme = () => {
      let isDarkMode = false;
      
      if (theme === 'system') {
        // Use system preference
        isDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
      } else {
        // Use user preference
        isDarkMode = theme === 'dark';
      }
      
      // Update state
      setIsDark(isDarkMode);
      
      // Apply theme to document
      if (isDarkMode) {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }
    };

    applyTheme();

    // Listen for system theme changes
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleChange = () => {
      if (theme === 'system') {
        applyTheme();
      }
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, [theme]);

  return (
    <ThemeContext.Provider value={{ theme, isDark, setTheme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = (): ThemeContextType => {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};
