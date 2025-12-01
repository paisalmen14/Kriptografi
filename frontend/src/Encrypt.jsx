import React, { useState } from "react";
import axios from "axios";

export default function Encrypt({ useModified }) {
  const [text, setText] = useState("");
  const [key, setKey] = useState("");
  const [output, setOutput] = useState("");

  async function doEncrypt() {
    const res = await axios.post("http://localhost:5000/encrypt", {
      text,
      key,
      modified: useModified
    });
    setOutput(res.data.cipher);
  }

  return (
    <div className="card">
      <h2>Encrypt</h2>
      <textarea placeholder="Plaintext..." onChange={e => setText(e.target.value)} />
      <input placeholder="Key (min 16 chars)" onChange={e => setKey(e.target.value)} />
      <button onClick={doEncrypt}>Encrypt</button>
      <textarea value={output} readOnly />
    </div>
  );
}
