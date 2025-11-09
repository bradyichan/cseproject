import React from "react";
import "./App.css";
import Jonathan from "./assets/Jonathan.png";

const ProfileIcon: React.FC = () => {
  return (
    <a href="http://127.0.0.1:6767/users/1" target="_blank" rel="noopener noreferrer">
      <img src={Jonathan} alt="Profile" className="profileicon" />
    </a>
  );
};

export default ProfileIcon;