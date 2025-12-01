export default function Toggle({ useModified, setUseModified }) {
  return (
    <div className="toggle-box">
      <label>
        <input 
          type="checkbox" 
          checked={useModified}
          onChange={() => setUseModified(!useModified)}
        /> 
        Use Modified S-Box (From Article)
      </label>
    </div>
  );
}
