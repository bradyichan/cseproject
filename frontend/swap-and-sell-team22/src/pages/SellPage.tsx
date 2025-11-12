import { useState } from "react";
import { Link } from "react-router-dom";

export default function SellPage() {
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    category: "",
    price: "",
    location: "",
    seller_id: "1", // default seller for now
  });

  const [imageFile, setImageFile] = useState<File | null>(null);
  const [message, setMessage] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Handle text / select / textarea changes
  const handleChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
    >
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  // Handle image file selection
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setImageFile(e.target.files[0]);
    }
  };

  // Submit form with FormData (for image upload)
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setMessage("");

    try {
      const data = new FormData();
      Object.entries(formData).forEach(([key, value]) =>
        data.append(key, value)
      );
      if (imageFile) data.append("image", imageFile);

      const response = await fetch("http://127.0.0.1:6767/items/add", {
        method: "POST",
        body: data,
      });

      const result = await response.json();

      if (response.ok) {
        setMessage("✅ Item listed successfully!");
        setFormData({
          title: "",
          description: "",
          category: "",
          price: "",
          location: "",
          seller_id: "1",
        });
        setImageFile(null);
      } else {
        setMessage(`Error: ${result.message || "Failed to list item"}`);
      }
    } catch (error) {
      setMessage(
        `Error: ${
          error instanceof Error ? error.message : "Failed to connect to server"
        }`
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="sell-wrapper">
      <div className="sell-header">
        <h1>List an Item for Sale</h1>
        <Link to="/" className="back-home-link">
          ← Back to Home
        </Link>
      </div>

      <form onSubmit={handleSubmit} className="sell-form">
        {/* TITLE */}
        <div className="form-group">
          <label htmlFor="title">Item Title *</label>
          <input
            type="text"
            id="title"
            name="title"
            value={formData.title}
            onChange={handleChange}
            required
            placeholder="Enter item title"
          />
        </div>

        {/* DESCRIPTION */}
        <div className="form-group">
          <label htmlFor="description">Description *</label>
          <textarea
            id="description"
            name="description"
            value={formData.description}
            onChange={handleChange}
            required
            placeholder="Describe your item"
            rows={4}
          />
        </div>

        {/* CATEGORY */}
        <div className="form-group">
          <label htmlFor="category">Category *</label>
          <select
            id="category"
            name="category"
            value={formData.category}
            onChange={handleChange}
            required
          >
            <option value="">Select a category</option>
            <option value="Electronics">Electronics</option>
            <option value="Books">Books</option>
            <option value="Furniture">Furniture</option>
            <option value="Clothing">Clothing</option>
            <option value="Home">Home</option>
            <option value="Sports">Sports</option>
            <option value="Other">Other</option>
          </select>
        </div>

        {/* PRICE */}
        <div className="form-group">
          <label htmlFor="price">Price ($) *</label>
          <input
            type="number"
            id="price"
            name="price"
            value={formData.price}
            onChange={handleChange}
            required
            min="0"
            step="0.01"
            placeholder="0.00"
          />
        </div>

        {/* LOCATION */}
        <div className="form-group">
          <label htmlFor="location">Location *</label>
          <input
            type="text"
            id="location"
            name="location"
            value={formData.location}
            onChange={handleChange}
            required
            placeholder="City, State"
          />
        </div>

        {/* IMAGE UPLOAD */}
        <div className="form-group">
          <label htmlFor="image">Upload Item Image *</label>
          <input
            type="file"
            id="image"
            name="image"
            accept="image/*"
            onChange={handleFileChange}
            required
          />
        </div>

        {/* IMAGE PREVIEW */}
        {imageFile && (
          <div className="form-group">
            <img
              src={URL.createObjectURL(imageFile)}
              alt="Preview"
              style={{
                width: "100%",
                maxWidth: "300px",
                borderRadius: "8px",
                display: "block",
                marginTop: "10px",
              }}
            />
          </div>
        )}

        {/* SUBMIT BUTTON */}
        <button type="submit" className="submit-btn" disabled={isSubmitting}>
          {isSubmitting ? "Listing..." : "List Item"}
        </button>

        {/* SUCCESS / ERROR MESSAGE */}
        {message && (
          <div
            className={`message ${
              message.includes("Error") ? "error" : "success"
            }`}
          >
            {message}
          </div>
        )}
      </form>
    </div>
  );
}
