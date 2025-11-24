import { useState, useEffect } from "react";
import "./App.css";
import { Routes, Route, Link } from "react-router-dom";

import ProfileIcon from "./ProfileIcon";
import Back2menu from "./components/back2menu";

import BuyPage from "./pages/BuyPage";
import SellPage from "./pages/SellPage";
import ItemPage from "./pages/ItemPage";
import MyProfile from "./pages/MyProfile";
import PaymentPage from "./pages/PaymentPage";
import SuccessPage from "./pages/SuccessPage";
import LogIn from "./pages/LogIn";
import SignUp from "./pages/SignUp";
import MessagingPage from "./pages/MessagingPage";
import SellerDashboard from "./pages/SellerDashboard";

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const userId = localStorage.getItem("userId");
    const username = localStorage.getItem("username");
    if (userId && username) {
      setIsAuthenticated(true);
    }
  }, []);

  const handleLogout = () => {
    localStorage.clear();
    setIsAuthenticated(false);
  };

  // NOT LOGGED IN
  if (!isAuthenticated) {
    return (
      <Routes>
        <Route
          path="/login"
          element={<LogIn setIsAuthenticated={setIsAuthenticated} />}
        />
        <Route
          path="/signup"
          element={<SignUp setIsAuthenticated={setIsAuthenticated} />}
        />
        <Route
          path="*"
          element={<LogIn setIsAuthenticated={setIsAuthenticated} />}
        />
      </Routes>
    );
  }

  // LOGGED IN
  return (
    <Routes>
      <Route
        path="/"
        element={
          <div className="container">
            {/* HEADER BOX */}
            <div
              style={{
                backgroundColor: "green",
                padding: "20px",
                borderRadius: "10px",
                display: "inline-block",
                width: "400px",
                height: "250px",
                position: "relative",
              }}
            >
              <h1 style={{ color: "white" }}>
                Swap & Sell: Secondhand Marketplace
              </h1>

              <ProfileIcon />
              <Back2menu />

              {/* RESTORED LOGOUT BUTTON */}
              <button
                onClick={handleLogout}
                style={{
                  position: "absolute",
                  top: "10px",
                  right: "10px",
                  backgroundColor: "red",
                  color: "white",
                  border: "none",
                  padding: "8px 16px",
                  borderRadius: "6px",
                  cursor: "pointer",
                  fontWeight: "bold",
                }}
              >
                Log Out
              </button>
            </div>

            {/* ACTIONS */}
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

            {/* SELLER DASHBOARD LINK */}
            <div style={{ marginTop: "30px" }}>
              <Link
                to="/seller/dashboard"
                style={{
                  color: "black",
                  fontSize: "18px",
                  textDecoration: "underline",
                }}
              >
                Go to Seller Dashboard →
              </Link>
            </div>
          </div>
        }
      />

      {/* ROUTES */}
      <Route path="/buy" element={<BuyPage />} />
      <Route path="/sell" element={<SellPage />} />
      <Route path="/item/:id" element={<ItemPage />} />
      <Route path="/profile" element={<MyProfile />} />
      <Route path="/payment/:itemId" element={<PaymentPage />} />
      <Route path="/success" element={<SuccessPage />} />

      <Route
        path="/messages/:sellerId/:itemId"
        element={<MessagingPage />}
      />

      <Route
        path="/seller/dashboard"
        element={<SellerDashboard />}
      />

      <Route path="*" element={<BuyPage />} />
    </Routes>
  );
}

export default App;
