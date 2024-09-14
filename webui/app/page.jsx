'use client'
import {
  InstantSearch,
  SearchBox,
  Stats,
  Configure,
  useInstantSearch,
  useSearchBox
} from 'react-instantsearch'
import Client from '@searchkit/instantsearch-client'
import { useState } from 'react'

const searchClient = Client({
  url: '/api/search'
})

const HitView = ({ hit, detailsOpen }) => {
  const downloadHitContent = () => {
    const content = hit.filteredContent;
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${hit.title.replace(/\s+/g, '_')}_content.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  return (
    <div className="hit__details">
      <details open={detailsOpen}>
        <summary className="hit-details-panel">
          <h3 className="hit-details-header">{hit.title} - Part {hit.chunk_number}</h3>
          <button className="download-btn" onClick={downloadHitContent}>Download</button>
        </summary>
        <pre>{hit.filteredContent}</pre>
      </details>
    </div>
  )
}

const CustomHits = ({ detailsOpen }) => {
  const { query } = useSearchBox();
  const { results } = useInstantSearch();

  if (results.nbHits === 0) {
    return <p>No results found.</p>; 
  }

  const processedHits = results.hits
    .map(hit => {
      const resultsSplit = hit.content.split("\r\n");
      const filteredResults = resultsSplit.filter(line => line.includes(query));
      const filteredContent = filteredResults.join("\n");
      return { ...hit, filteredContent };
    })
    .filter(hit => hit.filteredContent.trim() !== '');

  if (processedHits.length === 0) {
    return <p>No relevant content found.</p>; 
  }

  const downloadAllHitsContent = () => {
    const allContent = processedHits
      .map(hit => `Title: ${hit.title} - Part ${hit.chunk_number}\n\n${hit.filteredContent}`)
      .join('\n\n-----\n\n');

    const blob = new Blob([allContent], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'all_hits_content.txt';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  return (
    <div>
      <div className={'main-hits-panel'}>
        <div>
          <SearchStatus/>
        </div>
        <button className="download-btn" onClick={downloadAllHitsContent}>Download All</button>
      </div>
      {processedHits.map(hit => (
        <HitView key={hit.objectID} hit={hit} detailsOpen={detailsOpen} />
      ))}
    </div>
  );
}

function SearchStatus() {
  const { status } = useInstantSearch();

  if (status === 'loading') {
    return <p>Loading...</p>; 
  }
  
  return null;
}


export default function Web() {
  const [detailsOpen, setDetailsOpen] = useState(true);

  const toggleDetails = () => {
    setDetailsOpen(prevState => !prevState);
  };

  return (
    <div className="container">
      <h1>BreachRadar</h1>
      <span>v0.0.1</span>
      <InstantSearch 
        indexName="scrapes_chunks"
        searchClient={searchClient}
        routing
      >
        <div className="search-panel">
          <div className="search-panel__filters">
            <div className="searchbox">
              <SearchBox placeholder="Search in content" searchAsYouType={false} />
              <SearchStatus/>
              <span 
                className={'radar-emoji'} 
                onClick={toggleDetails}
                style={{ cursor: 'pointer' }}
              >
                📡
              </span>
            </div>

            <div className="pagination">
              <Stats />
            </div>
          </div>

          <div className="search-panel__results">
            <Configure hitsPerPage={9999} />
            <CustomHits detailsOpen={detailsOpen} />
          </div>
        </div>
      </InstantSearch>
    </div>
  )
}
