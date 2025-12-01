import React, { useState } from "react";
import Encrypt from "./Encrypt";
import Decrypt from "./Decrypt";
import Toggle from "./Toggle";
import "./style.css"; // Menggunakan style.css untuk tata letak kustom

export default function App() {
  const [useModified, setUseModified] = useState(false);

  return (
    <div className="container">
      <h1>AES Manual Encryption & Decryption</h1>

      <Toggle useModified={useModified} setUseModified={setUseModified} />

      <div className="grid">
        <Encrypt useModified={useModified} />
        <Decrypt useModified={useModified} />
      </div>

      <p className="footer">
        Catatan: Fungsi Decrypt saat ini hanya bersifat placeholder dan belum diimplementasikan sepenuhnya (sesuai catatan di backend/aes.py).
      </p>
    </div>
  );
}