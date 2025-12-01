import React, { useState } from "react";
import axios from "axios";

export default function Decrypt({ useModified }) {
  const [cipher, setCipher] = useState("");
  const [key, setKey] = useState("");
  const [output, setOutput] = useState("");

  async function doDecrypt() {
    const res = await axios.post("http://localhost:5000/decrypt", {
      cipher,
      key,
      modified: useModified
    });
    setOutput(res.data.plain);
  }

  return (
    <div className="card">
      <h2>Decrypt</h2>
      <textarea placeholder="Cipher hex..." onChange={e => setCipher(e.target.value)} />
      <input placeholder="Key (min 16 chars)" onChange={e => setKey(e.target.value)} />
      <button onClick={doDecrypt}>Decrypt</button>
      <textarea value={output} readOnly />
    </div>
  );
}
