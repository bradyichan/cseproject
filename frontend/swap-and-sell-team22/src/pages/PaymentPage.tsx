import { useParams, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import ProfileIcon from "../ProfileIcon";
import Back2menu from "../components/back2menu";
import "../App.css";

interface Item {
  item_id: number;
  title: string;
  price: number;
  location: string;
}

export default function PaymentPage() {
  const { itemId } = useParams();
  const navigate = useNavigate();
  const [item, setItem] = useState<Item | null>(null);
  const [loading, setLoading] = useState(false);

  // Load the selected item
  useEffect(() => {
    fetch(`http://127.0.0.1:6767/items/${itemId}`)
      .then((res) => res.json())
      .then((data) => {
        if (data.status === "success") {
          setItem(data.data);
        }
      })
      .catch((err) => console.error("Error fetching item:", err));
  }, [itemId]);

  // FULL backend-connected payment handler
  async function handleConfirmPayment() {
    if (!item) return;
    setLoading(true);

    const userId = 1; // placeholder user until login exists

    // 1️⃣ Validate payment
    const validateRes = await fetch("http://127.0.0.1:6767/payment/validate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        paymentMethodId: "visa_1234",
        userId: userId,
        cardNumber: "4242 4242 4242 4242",
        cvv: "123",
        expiryDate: "12/27",
      }),
    });

    const validateData = await validateRes.json();

    if (validateData.status !== "success") {
      alert("Payment validation failed.");
      setLoading(false);
      return;
    }

    // 2️⃣ Create purchase
    const purchaseRes = await fetch("http://127.0.0.1:6767/payment/purchase", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        itemId: item.item_id,
        userId: userId,
        paymentMethodId: "visa_1234",
        amount: item.price,
      }),
    });

    const purchaseData = await purchaseRes.json();

    if (purchaseData.status !== "success") {
      alert("Unable to complete purchase.");
      setLoading(false);
      return;
    }

    setLoading(false);
    navigate("/success");
  }

  if (!item) return <h1 style={{ padding: "20px" }}>Loading item...</h1>;

  return (
    <div className="payment-wrapper">
      <div className="payment-card">

        {/* Page Header */}
        <h1 className="checkout-title">Checkout</h1>

        {/* Profile */}
        <Back2menu />
        <div className="floating-husky">
          <ProfileIcon />
        </div>

        {/* Logos */}
        <div className="payment-logos">
          <img src="/visa.png" alt="visa" />
          <img src="/mastercard.png" alt="mastercard" />
        </div>

        {/* Main layout: form & summary */}
        <div className="payment-section">

          {/* LEFT: Payment Form */}
          <div className="payment-form">
            <input type="text" placeholder="XXXX-XXXX-XXXX" />
            <div className="row">
              <input type="text" placeholder="Expiration" />
              <input type="text" placeholder="Pin" />
            </div>
            <input type="text" placeholder="Name" />
            <input type="text" placeholder="Address" />
            <div className="row">
              <input type="text" placeholder="City" />
              <input type="text" placeholder="Country" />
            </div>

            <button
              className="confirm-btn"
              onClick={handleConfirmPayment}
              disabled={loading}
            >
              {loading ? "Processing..." : "Confirm Payment"}
            </button>
          </div>

          {/* RIGHT: Item Summary */}
          <div className="summary-box">
            <h3>Item Selected</h3>

            <p><strong>{item.title}</strong></p>
            <p>${item.price}</p>
            <p>{item.location}</p>

            <p className="summary-total">Total: ${item.price}</p>
          </div>
        </div>
      </div>
    </div>
  );
}
