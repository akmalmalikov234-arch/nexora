"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import { api, getToken } from "@/lib/api";

export default function UploadPage() {
  const [name, setName] = useState("");
  const [packageName, setPackageName] = useState("");
  const [version, setVersion] = useState("1.0.0");
  const [category, setCategory] = useState("Umumiy");
  const [description, setDescription] = useState("");
  const [file, setFile] = useState<File | null>(null);

  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(e: FormEvent) {
    e.preventDefault();

    setMessage("");
    setError("");

    if (!getToken()) {
      setError("Avval hisobingizga kiring.");
      return;
    }

    if (!file) {
      setError("APK fayl tanlang.");
      return;
    }

    if (!file.name.toLowerCase().endsWith(".apk")) {
      setError("Faqat APK fayl qabul qilinadi.");
      return;
    }

    const form = new FormData();

    form.append("name", name);
    form.append("package_name", packageName);
    form.append("version", version);
    form.append("category", category);
    form.append("description", description);
    form.append("file", file);

    setLoading(true);

    try {
      await api("/api/apps/upload", {
        method: "POST",
        body: form
      });

      setMessage(
        "Ilova qabul qilindi. Endi owner tekshiruviga yuborildi."
      );

      setName("");
      setPackageName("");
      setVersion("1.0.0");
      setDescription("");
      setFile(null);
    } catch (err: any) {
      setError(err.message || "Yuklashda xato.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="site">
      <div className="formPage">
        <form className="bigForm" onSubmit={submit}>
          <Link href="/" className="backLink">
            ← Bosh sahifa
          </Link>

          <h1>Ilova joylash</h1>

          <p className="authDescription">
            Yuklangan APK darhol ommaga chiqmaydi.
            Avval server tekshiruvi va owner tasdig‘idan o‘tadi.
          </p>

          <label>Ilova nomi</label>
          <input
            className="formInput"
            required
            value={name}
            onChange={(e) => setName(e.target.value)}
          />

          <label>Package name</label>
          <input
            className="formInput"
            required
            placeholder="com.example.app"
            value={packageName}
            onChange={(e) => setPackageName(e.target.value)}
          />

          <label>Versiya</label>
          <input
            className="formInput"
            required
            value={version}
            onChange={(e) => setVersion(e.target.value)}
          />

          <label>Kategoriya</label>
          <select
            className="formInput"
            value={category}
            onChange={(e) => setCategory(e.target.value)}
          >
            <option>Umumiy</option>
            <option>O‘yinlar</option>
            <option>Ta’lim</option>
            <option>Biznes</option>
            <option>Foto va video</option>
            <option>Asboblar</option>
            <option>Kommunikatsiya</option>
          </select>

          <label>Tavsif</label>
          <textarea
            className="formInput textarea"
            required
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />

          <label>APK fayl</label>

          <input
            className="fileInput"
            type="file"
            accept=".apk,application/vnd.android.package-archive"
            required
            onChange={(e) =>
              setFile(e.target.files?.[0] || null)
            }
          />

          {message && (
            <div className="successBox">
              {message}
            </div>
          )}

          {error && (
            <div className="errorBox">
              {error}
            </div>
          )}

          <button
            className="primaryButton full"
            disabled={loading}
          >
            {loading
              ? "Tekshirilmoqda va yuklanmoqda..."
              : "APK yuborish"}
          </button>
        </form>
      </div>
    </main>
  );
}
