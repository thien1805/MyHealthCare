// src/api/chatbotAPI.js
import apiClient, { API_PREFIX } from "./authAPI";

/**
 * Send message to AI Health Chatbot
 * @param {string} message - User's message
 * @param {Array} conversationHistory - Previous messages [{role: 'user'|'assistant', content: '...'}]
 * @returns {Promise<{response: string, error?: string}>}
 */
export async function sendChatMessage(message, conversationHistory = []) {
  try {
    const response = await apiClient.post(
      `${API_PREFIX}/ai/health-qa/`,
      {
        message,
        conversation_history: conversationHistory,
      }
    );

    if (response.data?.response) {
      return { response: response.data.response };
    } else if (response.data?.error) {
      return { error: response.data.error };
    }
    
    return { error: "Unexpected response format" };
  } catch (error) {
    console.error("Chatbot API error:", error);
    const errorMessage = 
      error.response?.data?.error || 
      error.response?.data?.detail ||
      error.message || 
      "Failed to get response from chatbot";
    return { error: errorMessage };
  }
}
