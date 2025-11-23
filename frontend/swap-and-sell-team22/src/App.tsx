import { useState, useEffect } from "react";
import "./App.css";
import ProfileIcon from "./ProfileIcon";
import Back2menu from "./components/back2menu";

import { Routes, Route, Link } from "react-router-dom";

import BuyPage from "./pages/BuyPage";
import SellPage from "./pages/SellPage";
import ItemPage from "./pages/ItemPage";
import MyProfile from "./pages/MyProfile";
import PaymentPage from "./pages/PaymentPage";
import SuccessPage from "./pages/SuccessPage";
import LogIn from "./pages/LogIn";
import SignUp from "./pages/SignUp";

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Check if user is already logged in on mount
  useEffect(() => {
    const userId = localStorage.getItem("userId");
    const username = localStorage.getItem("username");
    
    console.log("App mounted - checking localStorage:", { userId, username });
    
    if (userId && username) {
      setIsAuthenticated(true);
    }
  }, []);

  // If not authenticated, show login page
  if (!isAuthenticated) {
    return (
      <Routes>
        <Route path="/signup" element={<SignUp setIsAuthenticated={setIsAuthenticated} />} />
        <Route path="*" element={<LogIn setIsAuthenticated={setIsAuthenticated} />} />
      </Routes>
    );
  }

  // If authenticated, show the main app
  return (
    <Routes>

      {/* HOME PAGE */}
      <Route
        path="/"
        element={
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
        }
      />

      {/* MAIN ROUTES */}
      <Route path="/buy" element={<BuyPage />} />
      <Route path="/sell" element={<SellPage />} />
      <Route path="/item/:id" element={<ItemPage />} />

      {/* PROFILE */}
      <Route path="/profile" element={<MyProfile />} />


      {/* PAYMENT FLOW */}
      <Route path="/payment/:itemId" element={<PaymentPage />} />
      <Route path="/success" element={<SuccessPage />} />

    </Routes>
  );
}

export default App;
