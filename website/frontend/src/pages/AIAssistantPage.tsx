import { useRef, useState, type FormEvent } from "react";
import { Layout } from "../components/Layout";
import { api, ApiError } from "../api/client";
import type { AiMessage, AiTextResponse } from "../api/types";
import { renderBold } from "../utils/markdown";

export function AIAssistantPage() {
  const [messages, setMessages] = useState<AiMessage[]>([
    {
      role: "model",
      text: "Здравствуйте! Я помогу с вопросами по радиационной безопасности и подготовке к аттестации. Спросите что-нибудь или запросите план обучения.",
    },
  ]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  function scrollToBottom() {
    setTimeout(() => bottomRef.current?.scrollIntoView({ behavior: "smooth" }), 50);
  }

  async function sendMessage(text: string) {
    if (!text.trim() || sending) return;
    setError(null);
    const history = messages;
    const nextMessages = [...messages, { role: "user" as const, text }];
    setMessages(nextMessages);
    setInput("");
    setSending(true);
    scrollToBottom();

    try {
      const res = await api.post<AiTextResponse>("/api/ai/chat", { message: text, history });
      setMessages((prev) => [...prev, { role: "model", text: res.text }]);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Не удалось получить ответ");
    } finally {
      setSending(false);
      scrollToBottom();
    }
  }

  async function handleStudyPlan() {
    if (sending) return;
    setError(null);
    setSending(true);
    scrollToBottom();
    try {
      const res = await api.post<AiTextResponse>("/api/ai/study-plan");
      setMessages((prev) => [...prev, { role: "model", text: res.text }]);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Не удалось получить план обучения");
    } finally {
      setSending(false);
      scrollToBottom();
    }
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    sendMessage(input);
  }

  return (
    <Layout title="ИИ-ассистент">
      <button className="btn btn-ghost btn-block" disabled={sending} onClick={handleStudyPlan}>
        📋 Получить план обучения
      </button>

      <div className="chat-thread">
        {messages.map((m, i) => (
          <div key={i} className={`chat-bubble ${m.role === "user" ? "user" : "assistant"}`}>
            {renderBold(m.text)}
          </div>
        ))}
        {sending && <div className="chat-bubble assistant chat-typing">…</div>}
        <div ref={bottomRef} />
      </div>

      {error && <div className="error-text">{error}</div>}

      <form className="chat-input-row" onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Задайте вопрос…"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={sending}
        />
        <button className="btn btn-primary" type="submit" disabled={sending || !input.trim()}>
          →
        </button>
      </form>
    </Layout>
  );
}
