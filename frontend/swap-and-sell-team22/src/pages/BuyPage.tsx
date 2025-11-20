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
  seller_username?: string;
}

export default function BuyPage() {
  const [items, setItems] = useState<Item[]>([]);
  const [searchTerm, setSearchTerm] = useState("");

  // Fetch items from backend
  useEffect(() => {
    fetch("http://127.0.0.1:6767/items/all")
      .then((res) => res.json())
      .then((data) => {
        if (data?.data?.items) {
          setItems(data.data.items);
        }
      })
      .catch((err) => console.error("Fetch error:", err));
  }, []);

  // Filter items
  const filteredItems = items.filter((item) =>
    item.title.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Delete item handler
  const handleDeleteItem = async (itemId: number) => {
    if (!window.confirm("Are you sure you want to delete this item?")) {
      return;
    }

    try {
      const response = await fetch(`http://127.0.0.1:6767/items/delete/${itemId}`, {
        method: "DELETE",
      });

      const result = await response.json();

      if (response.ok) {
        // Remove item from local state
        setItems(items.filter(item => item.item_id !== itemId));
        alert("Item deleted successfully!");
      } else {
        alert(`Error: ${result.message || "Failed to delete item"}`);
      }
    } catch (error) {
      console.error("Delete error:", error);
      alert("Failed to delete item. Please try again.");
    }
  };

  return (
    <div className="buy-wrapper" style={{ padding: "20px" }}>
      <div className="buy-header">
        <h2>Browse Items</h2>
        <Link to="/" className="back-home-link">
          ← Back to Home
        </Link>
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

          const sellerName = item.seller_username ; //|| Joe Anonymous

          return (
            <div className="item-card" key={item.item_id}>
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
                <p className="seller" style={{ 
                  fontSize: "14px", 
                  color: "#666", 
                  marginTop: "8px",
                  fontStyle: "italic"
                }}>
                  {sellerName}
                </p>
                <button
                  onClick={() => handleDeleteItem(item.item_id)}
                  style={{
                    marginTop: "10px",
                    backgroundColor: "#dc3545",
                    color: "white",
                    padding: "8px 16px",
                    border: "none",
                    borderRadius: "5px",
                    cursor: "pointer",
                    fontSize: "14px",
                    fontWeight: "bold",
                  }}
                  onMouseOver={(e) => e.currentTarget.style.backgroundColor = "#c82333"}
                  onMouseOut={(e) => e.currentTarget.style.backgroundColor = "#dc3545"}
                >
                  Delete Item
                </button>
              </div>
            </div>
          );
        })}
      </div>

      <div className="floating-husky">
        <ProfileIcon />
      </div>
    </div>
  );
}