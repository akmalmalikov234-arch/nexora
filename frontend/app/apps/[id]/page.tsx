"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { api, apiUrl } from "@/lib/api";

export default function AppDetails() {
  const params = useParams();
  const id = params.id;

  const [app, setApp] = useState<any>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!id) return;

    api(`/api/apps/${id}`)
      .then(setApp)
      .catch((err) =>
        setError(err.message || "Ilova topilmadi.")
      );
  }, [id]);

  if (error) {
    return (
      <main className="site">
        <div className="formPage">
          <div className="empty">{error}</div>
        </div>
      </main>
    );
  }

  if (!app) {
    return (
      <main className="site">
        <div className="formPage">
          <div className="empty">
            Yuklanmoqda...
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="site">
      <div className="detailsPage">
        <Link href="/" className="backLink">
          ← Bosh sahifa
        </Link>

        <div className="detailsCard">
          <div className="detailsIcon">
            {app.name.charAt(0).toUpperCase()}
          </div>

          <div>
            <h1>{app.name}</h1>

            <p className="muted">
              {app.category} · v{app.version}
            </p>

            <p>
              {app.description}
            </p>

            <p className="package">
              {app.package_name}
            </p>

            <a
              className="primaryButton downloadLarge"
              href={apiUrl(
                `/api/apps/${app.id}/download`
              )}
            >
              APK yuklab olish
            </a>
          </div>
        </div>
      </div>
    </main>
  );
}
