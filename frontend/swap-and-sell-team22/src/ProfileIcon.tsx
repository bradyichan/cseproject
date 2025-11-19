import React from "react";
import "./App.css";
import Jonathan from "./assets/Jonathan.png";

const ProfileIcon: React.FC = () => {
  return (
    <a href="http://localhost:5173/profile" target="_blank" rel="noopener noreferrer">
      <img src={Jonathan} alt="Profile" className="profileicon" />
    </a>
  );
};

export default ProfileIcon;