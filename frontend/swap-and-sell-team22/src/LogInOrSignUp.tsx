import { useState } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import LogIn from "./pages/LogIn";
import SignUp from "./pages/SignUp";
import BuyPage from "./pages/BuyPage";
import SellPage from "./pages/SellPage";
import MyProfile from "./pages/MyProfile";
import PaymentPage from "./pages/PaymentPage";
import SuccessPage from "./pages/SuccessPage";
import { Link } from "react-router-dom";
import ProfileIcon from "./ProfileIcon";
import Back2menu from "./components/back2menu";

function LogInOrSignUp() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  return (
    <Routes>
      {/* Auth routes - only accessible when NOT authenticated */}
      {!isAuthenticated && (
        <>
          <Route path="/login" element={<LogIn setIsAuthenticated={setIsAuthenticated} />} />
          <Route path="/signup" element={<SignUp setIsAuthenticated={setIsAuthenticated} />} />
          <Route path="/" element={<AuthHome />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </>
      )}

      {/* App routes - only accessible when authenticated */}
      {isAuthenticated && (
        <>
          <Route path="/" element={<MainApp />} />
          <Route path="/buy" element={<BuyPage />} />
          <Route path="/sell" element={<SellPage />} />
          <Route path="/profile" element={<MyProfile />} />
          <Route path="/payment/:itemId" element={<PaymentPage />} />
          <Route path="/success" element={<SuccessPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </>
      )}
    </Routes>
  );
}

// Main app home page
function MainApp() {
  return (
    <div className="container">
      <div
        style={{
          backgroundColor: "green",
          padding: "20px",
          borderRadius: "10px",
          display: "inline-block",
          width: "400px",
          height: "250px",
        }}
      >
        <h1 style={{ color: "white" }}>
          Swap & Sell: Secondhand Marketplace
        </h1>
        <ProfileIcon />
        <Back2menu />
      </div>

      <h1 style={{ color: "black" }}>I want to...</h1>

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

// Home page with login/signup buttons
function AuthHome() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen w-full gap-6 p-6">
      <div
        style={{
          backgroundColor: "green",
          padding: "20px",
          borderRadius: "10px",
          width: "400px",
          textAlign: "center",
        }}
      >
        <h1 style={{ color: "white" }}>
          Swap & Sell: Secondhand Marketplace
        </h1>
      </div>

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

export default LogInOrSignUp;
