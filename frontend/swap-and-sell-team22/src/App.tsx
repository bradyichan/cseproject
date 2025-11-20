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

function App() {
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
