import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import ProfileIcon from "../ProfileIcon";
import "../App.css";

interface Item {
  item_id: number;
  title: string;
  price: number;
  location: string;
  image_filename?: string;
}

export default function BuyPage() {
  const [items, setItems] = useState<Item[]>([]);
  const [searchTerm, setSearchTerm] = useState("");

  // Fetch all items from backend
  useEffect(() => {
    fetch("http://127.0.0.1:6767/items/all")
      .then((res) => res.json())
      .then((data) => {
        if (data?.data?.items) setItems(data.data.items);
      })
      .catch((err) => console.error("Fetch error:", err));
  }, []);

  // Filter items
  const filteredItems = items.filter((item) =>
    item.title.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="buy-wrapper" style={{ padding: "20px" }}>
      <div className="buy-header">
        <h2>Browse Items</h2>
        <a href="/" className="back-home-link">← Back to Home</a>
      </div>

      <div className="search-row">
        <input
          type="text"
          placeholder="Search"
          className="search-bar"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>

      <div className="items-grid">
        {filteredItems.map((item) => {
          const imgSrc = item.image_filename
            ? `http://127.0.0.1:6767/items/image/${item.image_filename}`
            : null;

          return (
            <Link
              to={`/item/${item.item_id}`}
              key={item.item_id}
              style={{ textDecoration: "none", color: "inherit" }}
            >
              <div className="item-card">
                {imgSrc ? (
                  <img src={imgSrc} alt={item.title} className="item-img" />
                ) : (
                  <div
                    className="no-image"
                    style={{
                      width: "100%",
                      height: "300px",
                      background: "#ccc",
                      display: "flex",
                      justifyContent: "center",
                      alignItems: "center",
                    }}
                  >
                    No Image
                  </div>
                )}

                <div className="item-info">
                  <p className="price">${item.price}</p>
                  <p className="title">{item.title}</p>
                  <p className="state">{item.location}</p>
                </div>
              </div>
            </Link>
          );
        })}
      </div>

      <div className="floating-husky">
        <ProfileIcon />
      </div>
    </div>
  );
}