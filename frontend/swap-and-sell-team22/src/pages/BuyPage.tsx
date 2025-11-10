import imgUconn from "../assets/UConn Patch.png";
import imgChewToy from "../assets/Blue Chew Toy.png";
import imgTreat from "../assets/Treat.png";

export default function BuyPage() {
  return (
    <div className="buy-wrapper">

      {/* SEARCH + FILTER */}
      <div className="search-row">
        <input
          type="text"
          placeholder="Search"
          className="search-bar"
        />
        <button className="filter-button">Filter By..</button>
      </div>

      {/* GRID */}
      <div className="items-grid">

        {/* ITEM 1 */}
        <div className="item">
          <img src={imgUconn} alt="UConn PD Patch" className="item-img" />
          <div className="item-info">
            <p className="price">$3</p>
            <p className="title">UConn PD patch</p>
            <p className="state">Connecticut</p>
          </div>
        </div>

        {/* ITEM 2 */}
        <div className="item">
          <img src={imgChewToy} alt="Blue Chew Toy" className="item-img" />
          <div className="item-info">
            <p className="price">$6</p>
            <p className="title">Blue Chew Toy</p>
            <p className="state">Maine</p>
          </div>
        </div>

        {/* ITEM 3 */}
        <div className="item">
          <img src={imgTreat} alt="Treat" className="item-img" />
          <div className="item-info">
            <p className="price">$1</p>
            <p className="title">Treat</p>
            <p className="state">Vermont</p>
          </div>
        </div>

      </div>
    </div>
  );
}
