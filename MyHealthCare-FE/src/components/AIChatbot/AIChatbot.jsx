// src/components/AIChatbot/AIChatbot.jsx
import React, { useState, useRef, useEffect } from "react";
import { MessageCircle, X, Send, Bot, User, Loader2 } from "lucide-react";
import { sendChatMessage } from "../../api/chatbotAPI";
import { useTranslation } from "../../hooks/useTranslation";
import "./AIChatbot.css";

export default function AIChatbot() {
  const { t } = useTranslation();
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Scroll to bottom when new messages arrive
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  // Focus input when chat opens
  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  // Initialize with welcome message
  useEffect(() => {
    if (isOpen && messages.length === 0) {
      setMessages([
        {
          role: "assistant",
          content: t("chatbot.welcomeMessage") || "Xin chào! Tôi là trợ lý y tế AI của MyHealthCare. Tôi có thể giúp bạn với các câu hỏi về sức khỏe, triệu chứng, hoặc hướng dẫn đặt lịch khám. Bạn cần giúp gì?",
          timestamp: new Date(),
        },
      ]);
    }
  }, [isOpen, messages.length, t]);

  const handleToggle = () => {
    setIsOpen(!isOpen);
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage = {
      role: "user",
      content: inputValue.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");
    setIsLoading(true);

    try {
      // Prepare conversation history for API (last 10 messages)
      const historyForAPI = messages.slice(-10).map((msg) => ({
        role: msg.role,
        content: msg.content,
      }));

      const result = await sendChatMessage(userMessage.content, historyForAPI);

      if (result.error) {
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: result.error,
            timestamp: new Date(),
            isError: true,
          },
        ]);
      } else {
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: result.response,
            timestamp: new Date(),
          },
        ]);
      }
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: t("chatbot.errorMessage") || "Xin lỗi, đã có lỗi xảy ra. Vui lòng thử lại sau.",
          timestamp: new Date(),
          isError: true,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const formatTime = (date) => {
    return new Date(date).toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  return (
    <div className="ai-chatbot-container">
      {/* Chat Window */}
      {isOpen && (
        <div className="ai-chatbot-window">
          {/* Header */}
          <div className="ai-chatbot-header">
            <div className="ai-chatbot-header-info">
              <Bot size={24} className="ai-chatbot-icon" />
              <div>
                <h3>{t("chatbot.title") || "Trợ lý Y tế AI"}</h3>
                <span className="ai-chatbot-status">
                  {t("chatbot.online") || "Đang hoạt động"}
                </span>
              </div>
            </div>
            <button
              className="ai-chatbot-close-btn"
              onClick={handleToggle}
              aria-label="Close chat"
            >
              <X size={20} />
            </button>
          </div>

          {/* Messages */}
          <div className="ai-chatbot-messages">
            {messages.map((msg, index) => (
              <div
                key={index}
                className={`ai-chatbot-message ${
                  msg.role === "user" ? "ai-chatbot-message--user" : "ai-chatbot-message--bot"
                } ${msg.isError ? "ai-chatbot-message--error" : ""}`}
              >
                <div className="ai-chatbot-message-avatar">
                  {msg.role === "user" ? (
                    <User size={16} />
                  ) : (
                    <Bot size={16} />
                  )}
                </div>
                <div className="ai-chatbot-message-content">
                  <p>{msg.content}</p>
                  <span className="ai-chatbot-message-time">
                    {formatTime(msg.timestamp)}
                  </span>
                </div>
              </div>
            ))}
            
            {isLoading && (
              <div className="ai-chatbot-message ai-chatbot-message--bot">
                <div className="ai-chatbot-message-avatar">
                  <Bot size={16} />
                </div>
                <div className="ai-chatbot-message-content ai-chatbot-typing">
                  <Loader2 size={16} className="ai-chatbot-loader" />
                  <span>{t("chatbot.typing") || "Đang trả lời..."}</span>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="ai-chatbot-input-area">
            <input
              ref={inputRef}
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={t("chatbot.placeholder") || "Nhập câu hỏi của bạn..."}
              disabled={isLoading}
              className="ai-chatbot-input"
            />
            <button
              onClick={handleSendMessage}
              disabled={!inputValue.trim() || isLoading}
              className="ai-chatbot-send-btn"
              aria-label="Send message"
            >
              <Send size={18} />
            </button>
          </div>

          {/* Disclaimer */}
          <div className="ai-chatbot-disclaimer">
            {t("chatbot.disclaimer") || "⚠️ Thông tin chỉ mang tính tham khảo, không thay thế khám bác sĩ"}
          </div>
        </div>
      )}

      {/* Floating Button */}
      <button
        className={`ai-chatbot-fab ${isOpen ? "ai-chatbot-fab--open" : ""}`}
        onClick={handleToggle}
        aria-label={isOpen ? "Close chat" : "Open chat"}
      >
        {isOpen ? <X size={24} /> : <MessageCircle size={24} />}
      </button>
    </div>
  );
}
