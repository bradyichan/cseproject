import React, { useState, useEffect } from "react";
import MyProfileIcon from "../MyProfileIcon";
import Back2menu from "../components/back2menu";

export default function MyProfile() {
  // tate for editable fields
  const [name, setName] = useState("Jonathan XV");
  const [location, setLocation] = useState("Storrs, Connecticut");
  const [bio, setBio] = useState(
    "Mascot for the University of Connecticut!"
  );

  // load saved data from localStorage
  useEffect(() => {
    const savedName = localStorage.getItem("profile_name");
    const savedLocation = localStorage.getItem("profile_location");
    const savedBio = localStorage.getItem("profile_bio");

    if (savedName) setName(savedName);
    if (savedLocation) setLocation(savedLocation);
    if (savedBio) setBio(savedBio);
  }, []);

  // save data to localStorage
  const saveProfile = () => {
    localStorage.setItem("profile_name", name);
    localStorage.setItem("profile_location", location);
    localStorage.setItem("profile_bio", bio);
    alert("Profile saved!");
  };

  return (
    <div>
      <Back2menu />
      <MyProfileIcon />

      {/* editable name */}
      <input
        value={name}
        onChange={(e) => setName(e.target.value)}
        style={{
          position: "fixed",
          top: "250px",
          left: "50%",
          transform: "translateX(-50%)",
          fontSize: "50px",
          textAlign: "center",
          zIndex: 1000,
          border: "none",
          background: "transparent",
          textAlign: "center",
        }}
      />

      {/* editable location */}
      <input
        value={location}
        onChange={(e) => setLocation(e.target.value)}
        style={{
          position: "fixed",
          top: "310px",
          left: "50%",
          transform: "translateX(-50%)",
          fontSize: "30px",
          textAlign: "center",
          zIndex: 1000,
          border: "none",
          background: "transparent",
        }}
      />

      {/* editable bio */}
      <input
        value={bio}
        onChange={(e) => setBio(e.target.value)}
        style={{
          position: "fixed",
          top: "350px",
          left: "50%",
          transform: "translateX(-50%)",
          fontSize: "30px",
          textAlign: "center",
          zIndex: 1000,
          border: "none",
          background: "transparent",
          width: "90%",
          textAlign: "center",
        }}
      />

      {/* save button */}
      <button
        onClick={saveProfile}
        style={{
          position: "fixed",
          top: "400px",
          left: "50%",
          transform: "translateX(-50%)",
          padding: "10px 20px",
          fontSize: "20px",
          cursor: "pointer",
        }}
      >
        Save
      </button>
    </div>
  );
}
