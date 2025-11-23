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

  const filteredItems = items.filter((item) =>
    item.title.toLowerCase().includes(searchTerm.toLowerCase())
  );

  async function handleDeleteItem(itemId: number) {
    if (!window.confirm("Are you sure you want to delete this item?")) return;

    try {
      const res = await fetch(`http://127.0.0.1:6767/items/delete/${itemId}`, {
        method: "DELETE",
      });

      const data = await res.json();

      if (res.ok) {
        setItems((prev) => prev.filter((i) => i.item_id !== itemId));
        alert("Item deleted!");
      } else {
        alert(data.message || "Delete failed.");
      }
    } catch (err) {
      alert(err);
    }
  }

  return (
    <div className="buy-wrapper" style={{ padding: "20px" }}>
      <div className="buy-header">
        <h2>Browse Items</h2>
        <Link to="/" className="back-home-link">← Back to Home</Link>
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
            <div className="item-card-wrapper" key={item.item_id}>
              
              {/* CLICKABLE AREA */}
              <Link
                to={`/item/${item.item_id}`}
                className="item-card"
                style={{ textDecoration: "none", color: "inherit" }}
              >
                {imgSrc ? (
                  <img src={imgSrc} alt={item.title} className="item-img" />
                ) : (
                  <div className="no-image">No Image</div>
                )}

                <div className="item-info">
                  <p className="price">${item.price}</p>
                  <p className="title">{item.title}</p>
                  <p className="state">{item.location}</p>
                </div>
              </Link>

              {/* DELETE BUTTON — OUTSIDE THE LINK */}
              <button
                onClick={() => handleDeleteItem(item.item_id)}
                className="delete-btn"
              >
                Delete Item
              </button>

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
