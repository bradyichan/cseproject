import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";

interface Message {
  message_id: number;
  sender_id: number;
  receiver_id: number;
  content: string;
  timestamp: string;
}

interface ItemSummary {
  item_id: number;
  seller_id: number;
  title: string;
}

const BASE_URL = "http://127.0.0.1:6767";

export default function MessagingPage() {
  // Route params: /messages/:sellerId/:itemId
  // BUT in practice this param is "other user id" now:
  const { sellerId, itemId } = useParams();

  const currentUserIdStr = localStorage.getItem("userId");
  const currentUserId = currentUserIdStr ? Number(currentUserIdStr) : null;
  const otherUserId = sellerId ? Number(sellerId) : null;

  const [item, setItem] = useState<ItemSummary | null>(null);
  const [otherUsername, setOtherUsername] = useState<string>("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [content, setContent] = useState("");

  // If we are missing basic info, bail
  if (!currentUserId || !otherUserId || !itemId) {
    return <p style={{ padding: "20px" }}>Error loading conversation.</p>;
  }

  // -----------------------------
  // Fetch item (to know the true seller_id + title)
  // -----------------------------
  useEffect(() => {
    fetch(`${BASE_URL}/items/${itemId}`)
      .then((res) => res.json())
      .then((data) => {
        if (data.status === "success") {
          setItem({
            item_id: data.data.item_id,
            seller_id: data.data.seller_id,
            title: data.data.title,
          });
        }
      })
      .catch(() => {});
  }, [itemId]);

  // -----------------------------
  // Fetch "other" user's username (buyer or seller)
  // -----------------------------
  useEffect(() => {
    fetch(`${BASE_URL}/users/${otherUserId}`)
      .then((res) => res.json())
      .then((data) => {
        if (data.status === "success") {
          setOtherUsername(data.data.username);
        }
      })
      .catch(() => {});
  }, [otherUserId]);

  // Helper to compute consistent conversation ID
  function getConversationId(itemObj: ItemSummary): string {
    const sellerIdActual = itemObj.seller_id;
    const buyerId =
      currentUserId === sellerIdActual ? otherUserId : currentUserId;
    return `conv_${buyerId}_${sellerIdActual}_${itemObj.item_id}`;
  }

  // -----------------------------
  // Load messages (polling every 3s)
  // -----------------------------
  function loadMessages(itemObj: ItemSummary) {
    const convId = getConversationId(itemObj);

    fetch(`${BASE_URL}/messaging/conversation/${convId}`)
      .then(async (res) => {
        if (!res.ok) {
          // No messages yet
          setMessages([]);
          return;
        }
        const data = await res.json();
        if (data.status === "success") {
          setMessages(data.data.conversation);
        } else {
          setMessages([]);
        }
      })
      .catch(() => setMessages([]));
  }

  useEffect(() => {
    if (!item) return;

    loadMessages(item);
    const interval = setInterval(() => loadMessages(item), 3000);
    return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [item?.item_id, item?.seller_id, currentUserId, otherUserId]);

  // -----------------------------
  // Send a message
  // -----------------------------
  function send() {
    if (!content.trim() || !item) return;

    const sellerIdActual = item.seller_id;
    const buyerId =
      currentUserId === sellerIdActual ? otherUserId : currentUserId;
    const convId = getConversationId(item);

    // Receiver is the OTHER person
    const receiverId =
      currentUserId === sellerIdActual ? buyerId : sellerIdActual;

    fetch(`${BASE_URL}/messaging/send`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        conversation_id: convId,
        sender_id: currentUserId,
        receiver_id: receiverId,
        content,
      }),
    })
      .then((res) => res.json())
      .then(() => {
        setContent("");
        loadMessages(item);
      })
      .catch(() => {});
  }

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        minHeight: "100vh",
        background: "#eaff9f",
        paddingTop: "40px",
        color: "black",
      }}
    >
      <Link to="/buy" style={{ textDecoration: "none", color: "black" }}>
        ← Back to Buy
      </Link>

      <h1 style={{ marginTop: "20px", marginBottom: "10px" }}>
        Chat with {otherUsername || "User"}
      </h1>

      <h3 style={{ marginBottom: "20px", opacity: 0.7 }}>
        About: {item ? item.title : ""}
      </h3>

      {/* CHAT BOX */}
      <div
        style={{
          width: "600px",
          height: "500px",
          background: "#f2f2f2",
          borderRadius: "12px",
          padding: "20px",
          overflowY: "auto",
          boxShadow: "0 4px 12px rgba(0,0,0,0.2)",
        }}
      >
        {messages.length === 0 ? (
          <p style={{ opacity: 0.6 }}>No messages yet — start the conversation.</p>
        ) : (
          messages.map((m) => (
            <div
              key={m.message_id}
              style={{
                display: "flex",
                justifyContent:
                  m.sender_id === currentUserId ? "flex-end" : "flex-start",
                marginBottom: "10px",
              }}
            >
              <div
                style={{
                  background:
                    m.sender_id === currentUserId ? "#c7ffc7" : "#e4e4e4",
                  padding: "10px 14px",
                  borderRadius: "12px",
                  maxWidth: "70%",
                }}
              >
                {m.content}
              </div>
            </div>
          ))
        )}
      </div>

      {/* INPUT BAR */}
      <div
        style={{
          marginTop: "20px",
          display: "flex",
          gap: "10px",
        }}
      >
        <input
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="Message..."
          style={{
            width: "450px",
            padding: "12px",
            borderRadius: "8px",
            border: "1px solid black",
            background: "#ffffff",
            color: 'black',
          }}
        />
        <button
          onClick={send}
          style={{
            padding: "12px 20px",
            background: "black",
            color: "white",
            border: "none",
            borderRadius: "8px",
            cursor: "pointer",
            fontSize: "16px",
          }}
        >
          Send
        </button>
      </div>
    </div>
  );
}
