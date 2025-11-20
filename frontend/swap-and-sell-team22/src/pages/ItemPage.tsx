import { useEffect, useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import "../App.css";

interface Item {
  item_id: number;
  title: string;
  price: number;
  description: string;
  location: string;
  image_filename?: string;
}

export default function ItemPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [item, setItem] = useState<Item | null>(null);

  useEffect(() => {
    fetch(`http://127.0.0.1:6767/items/${id}`)
      .then((res) => res.json())
      .then((data) => {
        if (data?.data) setItem(data.data);
      })
      .catch((err) => console.error(err));
  }, [id]);

  if (!item)
    return <p style={{ padding: "20px", fontSize: "24px" }}>Loading...</p>;

  const imgSrc = item.image_filename
    ? `http://127.0.0.1:6767/items/image/${item.image_filename}`
    : null;

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
        {/* LEFT SIDE — IMAGE */}
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
        </div>

        {/* RIGHT SIDE — PRICE + BUTTONS */}
        <div style={{ flex: "1" }}>
          <p
            style={{
              fontSize: "64px",
              fontWeight: "700",
              marginBottom: "20px",
            }}
          >
            ${item.price.toFixed(2)}
          </p>

          <div style={{ display: "flex", gap: "25px", marginTop: "20px" }}>
            {/* BUY NOW -> PAYMENT */}
            <button
              onClick={() => navigate(`/payment/${item.item_id}`)}
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
              Buy Now
            </button>

            <button
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
        </div>
      </div>
    </div>
  );
}
