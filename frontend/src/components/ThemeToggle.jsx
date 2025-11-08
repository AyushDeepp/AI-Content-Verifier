import React from "react";
import { useTheme } from "../context/ThemeContext";
import { FaSun, FaMoon } from "react-icons/fa";
import "./ThemeToggle.css";

const ThemeToggle = () => {
  const { theme, toggleTheme } = useTheme();

  return (
    <button
      className={`theme-toggle theme-toggle-${theme}`}
      onClick={toggleTheme}
      aria-label="Toggle theme"
    >
      {theme === "dark" ? (
        <FaSun className="theme-icon" />
      ) : (
        <FaMoon className="theme-icon" />
      )}
    </button>
  );
};

export default ThemeToggle;
