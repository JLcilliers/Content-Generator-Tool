import React, { useState } from 'react';
import './App.css';

function App() {
  const [url, setUrl] = useState('');
  const [topic, setTopic] = useState('');
  const [keywords, setKeywords] = useState('');

  const [response, setResponse] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const response = await fetch('http://localhost:5001/api/brief', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url, topic, keywords }),
    });

    const data = await response.json();
    setResponse(data);
    console.log(data);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>SEO Content Brief Generator</h1>
      </header>
      <main>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="url">Website URL</label>
            <input
              type="text"
              id="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="topic">Topic</label>
            <input
              type="text"
              id="topic"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="keywords">Keywords (one per line, primary first)</label>
            <textarea
              id="keywords"
              value={keywords}
              onChange={(e) => setKeywords(e.target.value)}
              required
            ></textarea>
          </div>
          <button type="submit">Generate Brief</button>
        </form>
        {response && (
          <div className="response">
            <h2>Backend Response</h2>
            <pre>{JSON.stringify(response, null, 2)}</pre>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
