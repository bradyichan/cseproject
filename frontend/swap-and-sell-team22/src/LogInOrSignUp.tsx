import { useState, useEffect } from "react";
import { Routes, Route, Navigate } from "react-router-dom";

import LogIn from "./pages/LogIn";
import SignUp from "./pages/SignUp";
import BuyPage from "./pages/BuyPage";
import SellPage from "./pages/SellPage";
import ItemPage from "./pages/ItemPage";
import MyProfile from "./pages/MyProfile";
import PaymentPage from "./pages/PaymentPage";
import SuccessPage from "./pages/SuccessPage";

import ProfileIcon from "./ProfileIcon";
import Back2menu from "./components/back2menu";
import { Link } from "react-router-dom";

export default function LogInOrSignUp() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Auto-login if data is in localStorage
  useEffect(() => {
    const userId = localStorage.getItem("userId");
    const username = localStorage.getItem("username");

    if (userId && username) {
      setIsAuthenticated(true);
    }
  }, []);

  return (
    <Routes>

      {/* AUTH PAGES */}
      {!isAuthenticated && (
        <>
          <Route path="/" element={<AuthHome />} />
          <Route path="/login" element={<LogIn setIsAuthenticated={setIsAuthenticated} />} />
          <Route path="/signup" element={<SignUp setIsAuthenticated={setIsAuthenticated} />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </>
      )}

      {/* MAIN APP */}
      {isAuthenticated && (
        <>
          <Route path="/" element={<MainApp setIsAuthenticated={setIsAuthenticated} />} />
          <Route path="/buy" element={<BuyPage />} />
          <Route path="/sell" element={<SellPage />} />
          <Route path="/item/:id" element={<ItemPage />} />
          <Route path="/profile" element={<MyProfile />} />
          <Route path="/payment/:itemId" element={<PaymentPage />} />
          <Route path="/success" element={<SuccessPage />} />

          <Route path="*" element={<Navigate to="/" replace />} />
        </>
      )}

    </Routes>
  );
}

/* ---------------------------
   MAIN APP (HOME PAGE)
---------------------------- */
function MainApp({ setIsAuthenticated }: { setIsAuthenticated: (v: boolean) => void }) {
  const logout = () => {
    localStorage.clear();
    setIsAuthenticated(false);
  };

  return (
    <div className="container">
      <button
        onClick={logout}
        style={{
          marginTop: "20px",
          marginBottom: "20px",
          padding: "10px 20px",
          backgroundColor: "red",
          color: "white",
          borderRadius: "8px",
          border: "none",
          cursor: "pointer",
        }}
      >
        Log Out
      </button>

      <div
        style={{
          backgroundColor: "green",
          padding: "20px",
          borderRadius: "10px",
          display: "inline-block",
          width: "400px",
          textAlign: "center",
        }}
      >
        <h1 style={{ color: "white" }}>Swap & Sell</h1>
        <ProfileIcon />
        <Back2menu />
      </div>

      <h1 style={{ color: "black", marginTop: "20px" }}>I want to...</h1>

      <div
        style={{
          display: "flex",
          justifyContent: "center",
          gap: "40px",
          marginTop: "20px",
        }}
      >
        <Link
          to="/buy"
          style={{
            backgroundColor: "blue",
            color: "white",
            borderRadius: "50%",
            width: "100px",
            height: "100px",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            textDecoration: "none",
            fontSize: "20px",
            fontWeight: "bold",
          }}
        >
          BUY
        </Link>

        <Link
          to="/sell"
          style={{
            backgroundColor: "blue",
            color: "white",
            borderRadius: "50%",
            width: "100px",
            height: "100px",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            textDecoration: "none",
            fontSize: "20px",
            fontWeight: "bold",
          }}
        >
          SELL
        </Link>
      </div>
    </div>
  );
}

/* ---------------------------
   UNAUTHENTICATED HOME
---------------------------- */
function AuthHome() {
  return (
    <div
      className="flex flex-col items-center justify-center min-h-screen w-full gap-6 p-6"
      style={{ backgroundColor: "#eaff9f" }}
    >
      <h1
        style={{
          backgroundColor: "green",
          padding: "20px",
          color: "white",
          borderRadius: "10px",
          width: "400px",
          textAlign: "center",
        }}
      >
        Swap & Sell
      </h1>

      <h2 style={{ color: "black" }}>Welcome! Please choose an option:</h2>

      <div style={{ display: "flex", gap: "20px" }}>
        <a
          href="/login"
          style={{
            backgroundColor: "blue",
            color: "white",
            padding: "15px 30px",
            borderRadius: "8px",
            textDecoration: "none",
            fontSize: "18px",
            fontWeight: "bold",
          }}
        >
          Log In
        </a>

        <a
          href="/signup"
          style={{
            backgroundColor: "green",
            color: "white",
            padding: "15px 30px",
            borderRadius: "8px",
            textDecoration: "none",
            fontSize: "18px",
            fontWeight: "bold",
          }}
        >
          Sign Up
        </a>
      </div>
    </div>
  );
}
