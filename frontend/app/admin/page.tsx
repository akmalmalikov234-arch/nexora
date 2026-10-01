"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api, logout } from "@/lib/api";

type AppItem = {
  id: number;
  name: string;
  package_name: string;
  version: string;
  description: string;
  category: string;
  status: string;
  sha256: string;
  size_bytes: number;
};

export default function AdminPage() {
  const [apps, setApps] = useState<AppItem[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  async function load() {
    try {
      const data = await api("/api/admin/apps?status=pending");
      setApps(data);
    } catch (err: any) {
      setError(err.message || "Admin panelga kirish mumkin emas.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function changeStatus(
    id: number,
    status: "approved" | "rejected" | "blocked"
  ) {
    try {
      await api(`/api/admin/apps/${id}/status`, {
        method: "POST",
        body: JSON.stringify({ status })
      });

      await load();
    } catch (err: any) {
      setError(err.message || "Amal bajarilmadi.");
    }
  }

  if (loading) {
    return (
      <main className="site">
        <div className="adminPage">
          <div className="empty">
            Owner panel tekshirilmoqda...
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="site">
      <div className="adminPage">
        <header className="adminHeader">
          <div>
            <Link href="/" className="brand">
              <span className="brandIcon">N</span>
              Nexora
            </Link>

            <h1>Owner Control Center</h1>

            <p>
              Faqat server tomonidan tasdiqlangan owner
              foydalanuvchi bu amallarni bajara oladi.
            </p>
          </div>

          <button
            className="navButton"
            onClick={logout}
          >
            Chiqish
          </button>
        </header>

        {error && (
          <div className="errorBox">
            {error}
          </div>
        )}

        <section className="adminStats">
          <div>
            <small>Kutilayotgan</small>
            <strong>{apps.length}</strong>
          </div>

          <div>
            <small>Tekshiruv</small>
            <strong>ACTIVE</strong>
          </div>

          <div>
            <small>Access</small>
            <strong>OWNER</strong>
          </div>
        </section>

        <h2>Kutilayotgan ilovalar</h2>

        {apps.length === 0 ? (
          <div className="empty">
            Hozircha tekshiriladigan ilova yo‘q.
          </div>
        ) : (
          <div className="adminList">
            {apps.map((item) => (
              <article className="adminCard" key={item.id}>
                <div className="appIcon">
                  {item.name.charAt(0).toUpperCase()}
                </div>

                <div className="adminInfo">
                  <h3>{item.name}</h3>

                  <p>{item.package_name}</p>

                  <p>v{item.version}</p>

                  <p>{item.description}</p>

                  <small>
                    SHA-256:
                    <br />
                    {item.sha256}
                  </small>
                </div>

                <div className="adminActions">
                  <button
                    className="approveButton"
                    onClick={() =>
                      changeStatus(item.id, "approved")
                    }
                  >
                    ✓ Tasdiqlash
                  </button>

                  <button
                    className="rejectButton"
                    onClick={() =>
                      changeStatus(item.id, "rejected")
                    }
                  >
                    Rad etish
                  </button>

                  <button
                    className="blockButton"
                    onClick={() =>
                      changeStatus(item.id, "blocked")
                    }
                  >
                    Bloklash
                  </button>
                </div>
              </article>
            ))}
          </div>
        )}
      </div>
    </main>
  );
}
