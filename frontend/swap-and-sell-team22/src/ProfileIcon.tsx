import React from "react";
import "./App.css";
import Jonathan from "./assets/Jonathan.png";
import { Link } from "react-router-dom";

const ProfileIcon: React.FC = () => {
  return (
    <Link to="/profile">
      <img src={Jonathan} alt="Profile" className="profileicon" />
    </Link>
  );
};

export default ProfileIcon;