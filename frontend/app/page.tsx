"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api, apiUrl, getToken, logout } from "@/lib/api";

type AppItem = {
  id: number;
  name: string;
  package_name: string;
  version: string;
  description: string;
  category: string;
  status: string;
  download_count: number;
  size_bytes: number;
};

export default function Home() {
  const [apps, setApps] = useState<AppItem[]>([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState<any>(null);

  async function loadApps() {
    try {
      const query = search
        ? `?q=${encodeURIComponent(search)}`
        : "";

      const data = await api(`/api/apps${query}`);
      setApps(data);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  }

  async function loadUser() {
    if (!getToken()) return;

    try {
      const data = await api("/api/auth/me");
      setUser(data);
    } catch {
      localStorage.removeItem("nexora_token");
    }
  }

  useEffect(() => {
    loadApps();
    loadUser();
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => {
      loadApps();
    }, 350);

    return () => clearTimeout(timer);
  }, [search]);

  function formatSize(bytes: number) {
    if (!bytes) return "0 MB";

    const mb = bytes / 1024 / 1024;

    if (mb < 1) {
      return `${Math.round(bytes / 1024)} KB`;
    }

    return `${mb.toFixed(1)} MB`;
  }

  return (
    <main className="site">
      <header className="navbar">
        <Link href="/" className="brand">
          <span className="brandIcon">N</span>
          <span>Nexora</span>
        </Link>

        <nav className="navLinks">
          <Link href="/">Bosh sahifa</Link>
          <Link href="/upload">Ilova joylash</Link>

          {user?.is_admin && (
            <Link href="/admin" className="ownerLink">
              Owner
            </Link>
          )}

          {user ? (
            <button className="navButton" onClick={logout}>
              Chiqish
            </button>
          ) : (
            <Link href="/login" className="navButton">
              Kirish
            </Link>
          )}
        </nav>
      </header>

      <section className="hero">
        <div className="heroText">
          <div className="badge">NEXORA MARKET</div>

          <h1>
            Ilovalarni
            <br />
            <span>bir joydan</span> toping.
          </h1>

          <p>
            Android ilovalari uchun mustaqil, qulay va
            xavfsizlik tekshiruvlariga ega marketplace.
          </p>

          <div className="heroActions">
            <Link href="/upload" className="primaryButton">
              Ilovangizni joylang
            </Link>

            <a href="#apps" className="secondaryButton">
              Ilovalarni ko‘rish
            </a>
          </div>
        </div>

        <div className="heroCard">
          <div className="heroCardGlow" />

          <div className="phoneMockup">
            <div className="phoneTop" />

            <div className="mockLogo">N</div>

            <div className="mockTitle">
              Nexora
            </div>

            <div className="mockLine" />
            <div className="mockLine short" />

            <div className="mockApp">
              <div className="mockAppIcon">A</div>
              <div>
                <b>Ilovalar</b>
                <small>Tekshirilgan</small>
              </div>
            </div>

            <div className="mockApp">
              <div className="mockAppIcon">G</div>
              <div>
                <b>O‘yinlar</b>
                <small>Yangi ilovalar</small>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="apps" className="appsSection">
        <div className="sectionTitle">
          <div>
            <span>MARKET</span>
            <h2>Ilovalar</h2>
          </div>

          <input
            className="search"
            placeholder="Ilova qidirish..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        {loading ? (
          <div className="empty">
            Yuklanmoqda...
          </div>
        ) : apps.length === 0 ? (
          <div className="empty">
            Hozircha tasdiqlangan ilovalar yo‘q.
          </div>
        ) : (
          <div className="appGrid">
            {apps.map((item) => (
              <article className="appCard" key={item.id}>
                <div className="appIcon">
                  {item.name.charAt(0).toUpperCase()}
                </div>

                <div className="appInfo">
                  <h3>{item.name}</h3>

                  <p>
                    {item.category || "Umumiy"}
                  </p>

                  <small>
                    v{item.version} ·{" "}
                    {formatSize(item.size_bytes)}
                  </small>
                </div>

                <Link
                  href={`/apps/${item.id}`}
                  className="cardButton"
                >
                  Ko‘rish
                </Link>

                <a
                  href={apiUrl(
                    `/api/apps/${item.id}/download`
                  )}
                  className="downloadButton"
                >
                  Yuklash
                </a>
              </article>
            ))}
          </div>
        )}
      </section>

      <footer className="footer">
        <b>Nexora</b>
        <span>Mustaqil Android ilovalar platformasi</span>
      </footer>
    </main>
  );
}
