import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

interface Listing {
  item_id: number;
  title: string;
  price: number;
  image_filename?: string;
}

interface Bid {
  bid_id: number;
  bidder_id: number;
  amount: number;
}

interface Conversation {
  buyer_id: number;
  buyer_username: string;
  item_id: number;
  item_title: string;
}

export default function SellerDashboard() {
  const userId = localStorage.getItem("userId");
  const navigate = useNavigate();

  const [listings, setListings] = useState<Listing[]>([]);
  const [viewingBidsFor, setViewingBidsFor] = useState<number | null>(null);
  const [bids, setBids] = useState<Bid[]>([]);
  const [inbox, setInbox] = useState<Conversation[]>([]);

  // ---------------------------
  // LOAD ACTIVE LISTINGS
  // ---------------------------
  useEffect(() => {
    if (!userId) return;

    fetch(`http://localhost:6767/items/seller/${userId}`)
      .then((res) => res.json())
      .then((data) => {
        if (data.status === "success") {
          setListings(data.data.items);
        }
      })
      .catch(() => {});
  }, [userId]);

  // ---------------------------
  // LOAD SELLER INBOX
  // ---------------------------
  useEffect(() => {
    if (!userId) return;

    fetch(`http://localhost:6767/messaging/inbox/${userId}`)
      .then((res) => res.json())
      .then((data) => {
        if (data.status === "success") {
          setInbox(data.data.conversations);
        }
      })
      .catch(() => {});
  }, [userId]);

  // ---------------------------
  // VIEW BIDS FOR A LISTING
  // ---------------------------
  const openBids = (itemId: number) => {
    setViewingBidsFor(itemId);

    fetch(`http://localhost:6767/bidding/item/${itemId}`)
      .then((res) => res.json())
      .then((data) => {
        if (data.status === "success") {
          setBids(data.data.bids);
        } else {
          setBids([]);
        }
      })
      .catch(() => {});
  };

  // ---------------------------
  // DELETE LISTING
  // ---------------------------
  const deleteListing = (itemId: number) => {
    fetch(`http://localhost:6767/items/delete/${itemId}`, { method: "DELETE" })
      .then((res) => res.json())
      .then(() => {
        setListings((prev) => prev.filter((l) => l.item_id !== itemId));
      })
      .catch(() => {});
  };

  // ---------------------------
  // ACCEPT BID
  // ---------------------------
  const acceptBid = (bidId: number) => {
    fetch(`http://localhost:6767/bidding/accept/${bidId}`, {
      method: "PUT",
    })
      .then((res) => res.json())
      .then(() => {
        alert("Bid Accepted!");
        setViewingBidsFor(null);
        setBids([]);
      })
      .catch(() => {});
  };

  return (
    <div style={{ padding: "30px", maxWidth: "900px", margin: "0 auto", color: "black" }}>
      <h1 style={{ marginBottom: "20px", textAlign: "center" }}>Seller Dashboard</h1>

      {/* --------------------- */}
      {/* INBOX SECTION */}
      {/* --------------------- */}
      <div
        style={{
          backgroundColor: "#e6e6e6",
          padding: "20px",
          borderRadius: "8px",
          marginBottom: "30px",
          border: "1px solid #bbb",
        }}
      >
        <h2 style={{ marginBottom: "15px" }}>Inbox</h2>

        {inbox.length === 0 ? (
          <p>No messages yet.</p>
        ) : (
          inbox.map((conv, idx) => (
            <div
              key={idx}
              style={{
                padding: "10px",
                borderBottom: "1px solid #ccc",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              }}
            >
              <p style={{ margin: 0 }}>
                <b>{conv.buyer_username}</b> about <i>{conv.item_title}</i>
              </p>

              <button
                style={{
                  background: "blue",
                  color: "white",
                  padding: "8px 12px",
                  borderRadius: "6px",
                  border: "none",
                  cursor: "pointer",
                }}
                onClick={() =>
                  navigate(`/messages/${conv.buyer_id}/${conv.item_id}`)
                }
              >
                Open Chat
              </button>
            </div>
          ))
        )}
      </div>

      {/* --------------------- */}
      {/* ACTIVE LISTINGS */}
      {/* --------------------- */}
      <h2 style={{ marginBottom: "15px" }}>Your Active Listings</h2>

      {listings.length === 0 && <p>No active listings.</p>}

      {listings.map((item) => (
        <div
          key={item.item_id}
          style={{
            backgroundColor: "#e6e6e6",
            padding: "20px",
            marginBottom: "15px",
            borderRadius: "8px",
            border: "1px solid #bbb",
          }}
        >
          <h3 style={{ marginTop: 0 }}>{item.title}</h3>
          <p>Price: ${item.price}</p>

          {item.image_filename && (
            <img
              src={`http://localhost:6767/items/image/${item.image_filename}`}
              alt="item"
              style={{ width: "120px", borderRadius: "6px", marginBottom: "10px" }}
            />
          )}

          <div style={{ display: "flex", gap: "15px" }}>
            <button
              style={{
                background: "green",
                color: "white",
                padding: "8px 12px",
                borderRadius: "6px",
                border: "none",
                cursor: "pointer",
              }}
              onClick={() => openBids(item.item_id)}
            >
              View Bids
            </button>

            <button
              style={{
                background: "red",
                color: "white",
                padding: "8px 12px",
                borderRadius: "6px",
                border: "none",
                cursor: "pointer",
              }}
              onClick={() => deleteListing(item.item_id)}
            >
              Delete Listing
            </button>
          </div>
        </div>
      ))}

      {/* --------------------- */}
      {/* BID VIEWER */}
      {/* --------------------- */}
      {viewingBidsFor && (
        <div
          style={{
            marginTop: "30px",
            background: "#e6e6e6",
            padding: "20px",
            borderRadius: "8px",
            border: "1px solid #bbb",
          }}
        >
          <h2>Bids for Item #{viewingBidsFor}</h2>

          {bids.length === 0 ? (
            <p>No bids yet.</p>
          ) : (
            bids.map((bid) => (
              <div
                key={bid.bid_id}
                style={{
                  padding: "12px",
                  borderBottom: "1px solid #ccc",
                  display: "flex",
                  justifyContent: "space-between",
                }}
              >
                <span>
                  <b>${bid.amount}</b> from user {bid.bidder_id}
                </span>

                <button
                  style={{
                    background: "blue",
                    color: "white",
                    padding: "8px 12px",
                    borderRadius: "6px",
                    border: "none",
                    cursor: "pointer",
                  }}
                  onClick={() => acceptBid(bid.bid_id)}
                >
                  Accept Bid
                </button>
              </div>
            ))
          )}

          <button
            style={{
              marginTop: "15px",
              background: "gray",
              color: "white",
              padding: "8px 12px",
              borderRadius: "6px",
              border: "none",
              cursor: "pointer",
            }}
            onClick={() => setViewingBidsFor(null)}
          >
            Close
          </button>
        </div>
      )}
    </div>
  );
}
