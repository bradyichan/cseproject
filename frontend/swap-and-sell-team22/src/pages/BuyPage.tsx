import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import ProfileIcon from "../ProfileIcon";
import "../App.css";

// Import all images
import bluechewtoy from "../assets/items/bluechewtoy.png";
import desklamp from "../assets/items/desklamp.png";
import dogwallart from "../assets/items/dogwallart.png";
import dogwinterjacket from "../assets/items/dogwinterjacket.png";
import lioncostume from "../assets/items/lioncostume.png";
import peanutbuttertreats from "../assets/items/peanutbuttertreats.png";
import softgroomingbrush from "../assets/items/softgroomingbrush.png";
import squeakyfoxtoy from "../assets/items/squeakyfoxtoy.png";
import stainlesssteelbowlset from "../assets/items/stainlesssteelbowlset.png";
import treat from "../assets/items/treat.png";
import uconnpatch from "../assets/items/uconnpatch.png";
import stylishleash from "../assets/items/stylishleash.png";

const imageMap: Record<string, string> = {
  bluechewtoy,
  desklamp,
  dogwallart,
  dogwinterjacket,
  lioncostume,
  peanutbuttertreats,
  softgroomingbrush,
  squeakyfoxtoy,
  stainlesssteelbowlset,
  treat,
  uconnpatch,
  stylishleash,
};

function normalizeTitle(title: string) {
  return title.trim().replace(/[^a-zA-Z0-9]/g, "").toLowerCase();
}

interface Item {
  item_id: string;
  title: string;
  price: number;
  location: string;
}

export default function BuyPage() {
  const [items, setItems] = useState<Item[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    fetch("http://127.0.0.1:6767/items/all")
      .then((res) => res.json())
      .then((data) => {
        if (data?.data?.items) {
          setItems(data.data.items);
        }
      });
  }, []);

  const filteredItems = items.filter((item) =>
    item.title.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="buy-wrapper" style={{ padding: "20px" }}>
      <div className="buy-header">
        <h2>Browse Items</h2>
        <a href="/">← Back to Home</a>
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
          const normalized = normalizeTitle(item.title);
          let imageKey = Object.keys(imageMap).find((k) =>
            normalized.includes(k)
          );
          if (!imageKey) {
            imageKey = Object.keys(imageMap).find((k) =>
              k.includes(normalized)
            );
          }
          const imgSrc = imageKey ? imageMap[imageKey] : null;

          return (
            <div
              className="item-card"
              key={item.item_id}
              onClick={() => navigate(`/payment/${item.item_id}`)}
              style={{ cursor: "pointer" }}
            >
              {imgSrc ? (
                <img src={imgSrc} alt={item.title} className="item-img" />
              ) : (
                <div
                  className="no-image"
                  style={{
                    width: "100%",
                    height: "300px",
                    background: "#ccc",
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
          );
        })}
      </div>

      <div className="floating-husky">
        <ProfileIcon />
      </div>
    </div>
  );
}
