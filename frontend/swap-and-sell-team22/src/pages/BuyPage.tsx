import { useEffect, useState } from "react";
import ProfileIcon from "../ProfileIcon";
import "../App.css";

// ✅ Map item titles → image imports
import BlueChewToyImg from "../assets/items/Blue Chew Toy.png";
import UConnPatchImg from "../assets/items/UConn Patch.png";
import LionCostumeImg from "../assets/items/LionCostume.png";
import StylishLeashImg from "../assets/items/StylishLeash.png";
import WallArtImg from "../assets/items/WallArt.png";
import TreatImg from "../assets/items/Treat.png";
import DogBowlImg from "../assets/items/DogBowl.png";
import DogCoatImg from "../assets/items/DogCoat.png";
import FoxToyImg from "../assets/items/FoxToy.png";
import GroomingBrushImg from "../assets/items/GroomingBrush.png";
import PeanutTreatImg from "../assets/items/PeanutTreat.png";
import DeskLampImg from "../assets/items/DeskLamp.png";

// ✅ MAP: title → image source
const imageMap: Record<string, string> = {
  "UConn PD patch": UConnPatchImg,
  "Blue Chew Toy": BlueChewToyImg,
  "Treat": TreatImg,
  "Lion Costume": LionCostumeImg,
  "Stylish Leash": StylishLeashImg,
  "Wall Art": WallArtImg,
  "Dog Bowl": DogBowlImg,
  "Dog Coat": DogCoatImg,
  "Fox Toy": FoxToyImg,
  "Grooming Brush": GroomingBrushImg,
  "Peanut Treat": PeanutTreatImg,
  "Desk Lamp": DeskLampImg
};

export default function BuyPage() {
  const [items, setItems] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");

  // ✅ Fetch all items from backend API
  useEffect(() => {
    fetch("http://127.0.0.1:6767/items/all")
      .then((res) => res.json())
      .then((data) => {
        console.log("API response:", data);
        if (data?.data?.items) {
          setItems(data.data.items);
        }
      })
      .catch((err) => console.error("Fetch error:", err));
  }, []);

  // ✅ Filter items by search
  const filteredItems = items.filter((item: any) =>
    item.title.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="buy-wrapper">
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

        <button className="filter-button">Filter By..</button>
      </div>

      <div className="items-grid">
        {filteredItems.map((item: any) => {
          const img = imageMap[item.title] || "/placeholder.png"; // fallback image
          return (
            <div className="item" key={item.item_id}>
              <img src={img} alt={item.title} className="item-img" />
              <div className="item-info">
                <p className="price">${item.price}</p>
                <p className="title">{item.title}</p>
                <p className="state">{item.location}</p>
              </div>
            </div>
          );
        })}
      </div>

      <ProfileIcon />
    </div>
  );
}
