import { useEffect, useState, type FormEvent } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import "../App.css";

interface Item {
  item_id: number;
  title: string;
  price: number | string;
  description: string;
  location: string;
  category?: string;
  seller_id: number;
  seller_username: string;
  image_filename?: string;
}

interface Bid {
  bid_id: number;
  bidder_id: number;
  amount: number;
  timestamp: string;
}

export default function ItemPage() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [item, setItem] = useState<Item | null>(null);
  const [highestBid, setHighestBid] = useState<Bid | null>(null);

  const [showBidModal, setShowBidModal] = useState(false);
  const [bidAmount, setBidAmount] = useState("");
  const [bidError, setBidError] = useState("");
  const [submittingBid, setSubmittingBid] = useState(false);

  // Safely convert item.price to a number
  function getPriceValue(it: Item | null): number {
    if (!it) return 0;
    const raw = it.price;
    if (typeof raw === "string") {
      const num = Number(raw);
      return Number.isNaN(num) ? 0 : num;
    }
    return raw;
  }

  // -----------------------------
  // Load item
  // -----------------------------
  useEffect(() => {
    if (!id) return;

    fetch(`http://127.0.0.1:6767/items/${id}`)
      .then((res) => res.json())
      .then((data) => {
        if (data?.status === "success") {
          setItem(data.data);
        } else {
          console.error("Failed to load item:", data);
        }
      })
      .catch((err) => console.error("Error fetching item:", err));
  }, [id]);

  // -----------------------------
  // Load highest bid for this item
  // -----------------------------
  useEffect(() => {
    if (!item) return;

    fetch(`http://127.0.0.1:6767/bidding/highest/${item.item_id}`)
      .then(async (res) => {
        // If no bids exist, backend returns 404 → just ignore
        if (!res.ok) return;
        const data = await res.json();
        if (data.status === "success") {
          setHighestBid(data.data);
        }
      })
      .catch((err) => console.error("Error fetching highest bid:", err));
  }, [item]);

  if (!item)
    return <p style={{ padding: "20px", fontSize: "24px" }}>Loading...</p>;

  const imgSrc = item.image_filename
    ? `http://127.0.0.1:6767/items/image/${item.image_filename}`
    : null;

  const listingPrice = getPriceValue(item);

  // -----------------------------
  // Open bid modal
  // -----------------------------
  function handleOpenBidModal() {
    setBidError("");

    // Rule you wanted:
    // - If there IS a bid → min = highestBid + 1 (we'll prefill that)
    // - If there is NO bid → no real minimum, just let them type anything > 0
    if (highestBid) {
      setBidAmount((highestBid.amount + 1).toString());
    } else {
      setBidAmount(""); // let them choose starting bid
    }

    setShowBidModal(true);
  }

  // -----------------------------
  // Submit bid
  // -----------------------------
  async function handleSubmitBid(e: FormEvent) {
    e.preventDefault();
    setBidError("");

    if (!item) return;

    const userIdStr = localStorage.getItem("userId");
    if (!userIdStr) {
      setBidError("You must be logged in to place a bid.");
      return;
    }

    const bidderId = Number(userIdStr);
    if (!Number.isInteger(bidderId)) {
      setBidError("Invalid user ID – log out and log back in.");
      return;
    }

    const numericBid = parseFloat(bidAmount);
    if (Number.isNaN(numericBid) || numericBid <= 0) {
      setBidError("Please enter a valid positive bid amount.");
      return;
    }

    // Only enforce “must beat highest bid” — ignore listing price
    if (highestBid && numericBid <= highestBid.amount) {
      setBidError(
        `Your bid must be higher than $${highestBid.amount.toFixed(2)}.`
      );
      return;
    }

    setSubmittingBid(true);

    try {
      const res = await fetch("http://127.0.0.1:6767/bidding/place", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          item_id: item.item_id,
          bidder_id: bidderId,
          amount: numericBid,
        }),
      });

      const data = await res.json();

      if (!res.ok || data.status !== "success") {
        throw new Error(data.message || "Failed to place bid.");
      }

      // Update highest bid state ONLY – do NOT change item.price
      const newBid: Bid = {
        bid_id: data.data.bid_id,
        bidder_id: data.data.bidder_id,
        amount: data.data.amount,
        timestamp: data.data.timestamp,
      };
      setHighestBid(newBid);

      // DO NOT mutate item.price → keep listing price the same

      setShowBidModal(false);
      alert("Bid placed successfully!");
    } catch (err) {
      console.error("Bid error:", err);
      setBidError("Error placing bid.");
    } finally {
      setSubmittingBid(false);
    }
  }

  return (
    <div
      style={{
        padding: "40px",
        maxWidth: "1300px",
        margin: "0 auto",
        backgroundColor: "#eaff9f",
        minHeight: "100vh",
        color: "black",
      }}
    >
      <Link
        to="/buy"
        style={{
          textDecoration: "none",
          color: "black",
          fontSize: "22px",
          fontWeight: "500",
        }}
      >
        ← Back
      </Link>

      <div
        style={{
          display: "flex",
          marginTop: "40px",
          gap: "80px",
          alignItems: "flex-start",
        }}
      >
        {/* LEFT SIDE — IMAGE & BASIC INFO */}
        <div style={{ flex: "1" }}>
          {imgSrc ? (
            <img
              src={imgSrc}
              alt={item.title}
              style={{
                width: "100%",
                maxWidth: "550px",
                borderRadius: "12px",
                boxShadow: "0 6px 20px rgba(0,0,0,0.25)",
              }}
            />
          ) : (
            <div
              style={{
                width: "550px",
                height: "550px",
                background: "#ccc",
                display: "flex",
                justifyContent: "center",
                alignItems: "center",
                borderRadius: "12px",
                fontSize: "28px",
              }}
            >
              No Image
            </div>
          )}

          <h2 style={{ marginTop: "30px", fontSize: "38px", fontWeight: "700" }}>
            {item.title}
          </h2>
          <p style={{ marginTop: "-10px", fontSize: "22px", color: "#333" }}>
            {item.location}
          </p>
          <p style={{ fontSize: "20px", marginTop: "10px" }}>
            Seller: <b>{item.seller_username}</b>
          </p>
        </div>

        {/* RIGHT SIDE — PRICE + BUTTONS + HIGHEST BID */}
        <div style={{ flex: "1" }}>
          {/* LISTING PRICE — NEVER CHANGES FROM BIDS */}
          <p
            style={{
              fontSize: "64px",
              fontWeight: "700",
              marginBottom: "10px",
            }}
          >
            ${listingPrice.toFixed(2)}
          </p>

          {/* HIGHEST BID INFO */}
          {highestBid ? (
            <p style={{ fontSize: "20px", marginBottom: "10px" }}>
              Highest bid:{" "}
              <strong>${highestBid.amount.toFixed(2)}</strong>
            </p>
          ) : (
            <p style={{ fontSize: "20px", marginBottom: "10px" }}>
              No bids yet – be the first!
            </p>
          )}

          <div style={{ display: "flex", gap: "25px", marginTop: "20px" }}>
            {/* BUY NOW GOES TO PAYMENT */}
            <Link
              to={`/payment/${item.item_id}`}
              style={{
                padding: "18px 40px",
                backgroundColor: "#ff3b3b",
                borderRadius: "10px",
                fontSize: "28px",
                fontWeight: "600",
                color: "black",
                cursor: "pointer",
                textDecoration: "none",
                textAlign: "center",
              }}
            >
              Buy Now
            </Link>

            {/* OPEN BID MODAL */}
            <button
              onClick={handleOpenBidModal}
              style={{
                padding: "18px 40px",
                backgroundColor: "#ff3b3b",
                border: "none",
                borderRadius: "10px",
                fontSize: "28px",
                fontWeight: "600",
                color: "black",
                cursor: "pointer",
              }}
            >
              Bid on Item
            </button>
          </div>

          <p
            style={{
              marginTop: "40px",
              fontSize: "24px",
              lineHeight: "1.4",
            }}
          >
            {item.description}
          </p>

          {/* MESSAGE SELLER */}
          <p
            style={{
              marginTop: "20px",
              fontSize: "20px",
              color: "blue",
              textDecoration: "underline",
              cursor: "pointer",
            }}
            onClick={() =>
              navigate(`/messages/${item.seller_id}/${item.item_id}`)
            }
          >
            Message {item.seller_username}
          </p>
        </div>
      </div>

      {/* -------------------- BID MODAL -------------------- */}
      {showBidModal && (
        <div
          style={{
            position: "fixed",
            inset: 0,
            backgroundColor: "rgba(0,0,0,0.5)",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            zIndex: 1000,
          }}
        >
          <div
            style={{
              backgroundColor: "white",
              padding: "24px",
              borderRadius: "12px",
              minWidth: "350px",
              maxWidth: "90%",
            }}
          >
            <h2 style={{ marginBottom: "10px" }}>Place a Bid</h2>
            <p style={{ marginBottom: "10px" }}>
              Item: <strong>{item.title}</strong>
            </p>

            {highestBid ? (
              <p style={{ marginBottom: "10px", fontSize: "14px" }}>
                Current highest bid: ${highestBid.amount.toFixed(2)}. Your bid
                must be higher than this.
              </p>
            ) : (
              <p style={{ marginBottom: "10px", fontSize: "14px" }}>
                No bids yet – enter any positive amount to start the bidding.
              </p>
            )}

            <form onSubmit={handleSubmitBid}>
              <input
                type="number"
                step="0.01"
                min="0"
                value={bidAmount}
                onChange={(e) => setBidAmount(e.target.value)}
                style={{
                  width: "100%",
                  padding: "8px",
                  marginBottom: "10px",
                  fontSize: "16px",
                }}
                placeholder="Enter your bid amount"
              />

              {bidError && (
                <p
                  style={{
                    color: "red",
                    fontSize: "14px",
                    marginBottom: "8px",
                  }}
                >
                  {bidError}
                </p>
              )}

              <div
                style={{
                  display: "flex",
                  justifyContent: "flex-end",
                  gap: "10px",
                  marginTop: "10px",
                }}
              >
                <button
                  type="button"
                  onClick={() => setShowBidModal(false)}
                  style={{
                    padding: "8px 16px",
                    borderRadius: "6px",
                    border: "1px solid #ccc",
                    backgroundColor: "#f5f5f5",
                    cursor: "pointer",
                  }}
                  disabled={submittingBid}
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  style={{
                    padding: "8px 16px",
                    borderRadius: "6px",
                    border: "none",
                    backgroundColor: "#ff3b3b",
                    color: "black",
                    fontWeight: 600,
                    cursor: "pointer",
                  }}
                  disabled={submittingBid}
                >
                  {submittingBid ? "Submitting..." : "Submit Bid"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
