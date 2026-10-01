"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import { api, saveToken } from "@/lib/api";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [adminCode, setAdminCode] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(e: FormEvent) {
    e.preventDefault();

    setError("");
    setLoading(true);

    try {
      const data = await api("/api/auth/login", {
        method: "POST",
        body: JSON.stringify({
          email,
          password,
          admin_code: adminCode || null
        })
      });

      saveToken(data.access_token);

      window.location.href = "/";
    } catch (err: any) {
      setError(err.message || "Kirish amalga oshmadi.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="site">
      <div className="authPage">
        <form className="authCard" onSubmit={submit}>
          <Link href="/" className="brand">
            <span className="brandIcon">N</span>
            Nexora
          </Link>

          <h1>Kirish</h1>

          <p className="authDescription">
            Nexora hisobingizga kiring.
          </p>

          <label>Email</label>

          <input
            className="formInput"
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />

          <label>Parol</label>

          <input
            className="formInput"
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          <label>
            Owner himoya kodi
            <span className="muted"> faqat egasi uchun</span>
          </label>

          <input
            className="formInput"
            type="password"
            value={adminCode}
            onChange={(e) => setAdminCode(e.target.value)}
            placeholder="Owner code"
          />

          {error && (
            <div className="errorBox">
              {error}
            </div>
          )}

          <button
            className="primaryButton full"
            disabled={loading}
          >
            {loading ? "Tekshirilmoqda..." : "Kirish"}
          </button>

          <Link href="/" className="backLink">
            ← Bosh sahifaga
          </Link>
        </form>
      </div>
    </main>
  );
}
