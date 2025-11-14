import React from "react";
import "./App.css";
import Jonathan from "./assets/Jonathan.png";

const MyProfileIcon: React.FC = () => {
  return (
    <a target="_blank" rel="noopener noreferrer">
      <img src={Jonathan} alt="Profile" className="myprofilejonny" />
    </a>
  );
};

export default MyProfileIcon;